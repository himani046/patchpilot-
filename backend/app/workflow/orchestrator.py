import shutil
import tempfile
import uuid
from pathlib import Path

from app.agents.coder import generate_patch
from app.agents.root_cause import create_repair_plan
from app.agents.triage import triage_failure
from app.agents.verifier import verify_repair
from app.config import settings
from app.tools.patcher import apply_patch
from app.tools.repository import read_source_file, scan_repository
from app.tools.test_runner import run_tests


def investigate(workspace: str) -> dict:
    """Investigate a failing project. Each patch is attempted in a fresh copy."""
    investigation_id = str(uuid.uuid4())
    root = Path(workspace).resolve()
    events: list[dict] = []

    def record(name: str, details: dict | None = None) -> None:
        events.append({"event": name, "details": details or {}})

    record("investigation_started")
    files = scan_repository(str(root))
    if not files:
        return {"investigation_id": investigation_id, "status": "no_source_files", "events": events}

    baseline = run_tests(str(root))
    record("baseline_tests_completed", {"passed": baseline["passed"], "exit_code": baseline["exit_code"]})
    if baseline["passed"]:
        return {"investigation_id": investigation_id, "status": "no_failure_reproduced", "baseline": {k: v for k, v in baseline.items() if k != "output"}, "events": events}

    failure = triage_failure(baseline["output"])
    record("failure_triaged", {"category": failure.category})
    candidates = [p for p in failure.affected_files if p in files]
    if not candidates:
        candidates = [p for p in files if p.endswith(".py") and not p.startswith("tests/")][:8]
    if not candidates:
        return {"investigation_id": investigation_id, "status": "no_candidate_files", "failure": failure.model_dump(), "events": events}

    sources = {p: read_source_file(str(root), p) for p in candidates}
    plan = create_repair_plan(failure.model_dump(), sources)
    record("repair_plan_created")
    if not plan.files_to_change or not set(plan.files_to_change).issubset(set(candidates)):
        return {"investigation_id": investigation_id, "status": "repair_plan_rejected", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "events": events}

    last_raw = None
    # Each attempt starts from a clean copy; failed edits never contaminate retry context.
    for attempt in range(1, max(1, settings.max_repair_attempts) + 1):
        attempt_dir = Path(tempfile.mkdtemp(prefix=f"patchpilot-{investigation_id}-"))
        try:
            shutil.copytree(root, attempt_dir / "project", dirs_exist_ok=True, symlinks=False)
            attempt_root = attempt_dir / "project"
            attempt_sources = {p: read_source_file(str(attempt_root), p) for p in candidates}
            patch = generate_patch(plan.model_dump(), attempt_sources, candidates)
            changed = apply_patch(str(attempt_root), patch, candidates)
            record("patch_applied", {"attempt": attempt, "files": changed})
            raw = run_tests(str(attempt_root))
            last_raw = raw
            verification = verify_repair(raw)
            record("verification_completed", {"attempt": attempt, "passed": verification.passed})
            if verification.passed:
                # Return the changed contents and diffs in the result; leave uploaded original untouched.
                diffs = []
                import difflib
                for rel in changed:
                    before = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
                    after = (attempt_root / rel).read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
                    diffs.append({"path": rel, "diff": "".join(difflib.unified_diff(before, after, fromfile=f"a/{rel}", tofile=f"b/{rel}"))})
                return {"investigation_id": investigation_id, "status": "verification_passed", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "changed_files": changed, "diffs": diffs, "verification": verification.model_dump(), "attempts": attempt, "baseline": {k: v for k, v in baseline.items() if k != "output"}, "latest_test_output": raw["output"][-10000:], "events": events}
            # Add new execution evidence to the next attempt prompt via updated plan context.
            if attempt < settings.max_repair_attempts:
                plan = create_repair_plan({**failure.model_dump(), "latest_verification_output": raw["output"][-10000:]}, attempt_sources)
                record("repair_plan_revised", {"after_attempt": attempt})
        except Exception as exc:
            record("repair_attempt_error", {"attempt": attempt, "type": type(exc).__name__})
            if attempt >= settings.max_repair_attempts:
                return {"investigation_id": investigation_id, "status": "repair_error", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "attempts": attempt, "error": "Repair attempt could not be completed safely.", "events": events}
        finally:
            shutil.rmtree(attempt_dir, ignore_errors=True)

    from app.agents.verifier import verify_repair
    verification = verify_repair(last_raw or {"passed": False, "exit_code": None, "output": "No verification result", "timed_out": False})
    return {"investigation_id": investigation_id, "status": "repair_failed", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "verification": verification.model_dump(), "attempts": max(1, settings.max_repair_attempts), "latest_test_output": (last_raw or {}).get("output", "")[-10000:], "events": events}
