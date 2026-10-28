from pathlib import Path
from app.schemas import RepairPatch
def apply_patch(workspace: str, patch: RepairPatch, allowed_paths: list[str]) -> list[str]:
    root = Path(workspace).resolve(); allowed = set(allowed_paths); prepared = []
    for change in patch.changes:
        relative = Path(change.path)
        if relative.is_absolute() or ".." in relative.parts or change.path not in allowed: raise ValueError("Unsafe or unapproved patch path.")
        target = root / relative
        if target.is_symlink() or not target.is_file(): raise ValueError("Only existing, regular files may be modified.")
        try: target.resolve().relative_to(root)
        except ValueError as exc: raise ValueError("Patch path escapes workspace.") from exc
        if len(change.content.encode("utf-8")) > 200_000: raise ValueError("Replacement file is too large.")
        prepared.append((target, change.content))
    for target, content in prepared: target.write_text(content, encoding="utf-8")
    return [change.path for change in patch.changes]
