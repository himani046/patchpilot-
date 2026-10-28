import uuid
from pathlib import Path
from app.agents.coder import generate_patch
from app.agents.root_cause import create_repair_plan
from app.agents.triage import triage_failure
from app.agents.verifier import verify_repair
from app.tools.patcher import apply_patch
from app.tools.repository import read_source_file, scan_repository
from app.tools.test_runner import run_tests


def investigate(workspace: str) -> dict:
    investigation_id = str(uuid.uuid4())
    root = Path(workspace).resolve()
    events = []
    def record(event, details=None): events.append({"event": event, "details": details or {}})
    record("investigation_started")
    files = scan_repository(str(root))
    if not files: return {"investigation_id": investigation_id, "status": "no_source_files", "events": events}
    baseline = run_tests(str(root))
    record("baseline_tests_completed", {"passed": baseline["passed"], "exit_code": baseline["exit_code"]})
    if baseline["passed"]: return {"investigation_id": investigation_id, "status": "no_failure_reproduced", "baseline": {k:v for k,v in baseline.items() if k != "output"}, "events": events}
    failure = triage_failure(baseline["output"])
    record("failure_triaged", {"category": failure.category})
    candidates = [p for p in failure.affected_files if p in files]
    if not candidates: candidates = [p for p in files if p.endswith(".py") and not p.startswith("tests/")][:8]
    if not candidates: return {"investigation_id": investigation_id, "status": "no_candidate_files", "failure": failure.model_dump(), "events": events}
    sources = {p: read_source_file(str(root), p) for p in candidates}
    plan = create_repair_plan(failure.model_dump(), sources)
    record("repair_plan_created")
    if not plan.files_to_change or not set(plan.files_to_change).issubset(set(candidates)):
        return {"investigation_id": investigation_id, "status": "repair_plan_rejected", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "events": events}
    originals = {p: (root / p).read_bytes() for p in candidates}
    try:
        patch = generate_patch(plan.model_dump(), sources, candidates)
        changed = apply_patch(str(root), patch, candidates)
        record("patch_applied", {"files": changed})
        raw = run_tests(str(root)); verification = verify_repair(raw)
        record("verification_completed", {"passed": verification.passed})
        return {"investigation_id": investigation_id, "status": "verification_passed" if verification.passed else "repair_failed", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "changed_files": changed, "verification": verification.model_dump(), "attempts": 1, "baseline": {k:v for k,v in baseline.items() if k != "output"}, "latest_test_output": raw["output"][-10000:], "events": events}
    except Exception as exc:
        for relative, content in originals.items(): (root / relative).write_bytes(content)
        record("repair_error", {"type": type(exc).__name__})
        return {"investigation_id": investigation_id, "status": "repair_error", "failure": failure.model_dump(), "repair_plan": plan.model_dump(), "attempts": 0, "error": "Repair attempt could not be completed; workspace restored.", "events": events}
