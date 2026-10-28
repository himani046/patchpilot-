from pathlib import Path

from app.schemas import RepairPatch


def apply_patch(workspace: str, patch: RepairPatch, allowed_paths: list[str]) -> list[str]:
    root = Path(workspace).resolve()
    allowed = set(allowed_paths)
    prepared: list[tuple[Path, str, str]] = []

    # Validate every change before writing any file (all-or-nothing validation).
    for change in patch.changes:
        relative = Path(change.path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe patch path.")
        if change.path not in allowed:
            raise ValueError(f"File is not approved: {change.path}")
        target = root / relative
        if target.is_symlink() or not target.is_file():
            raise ValueError("Only existing, regular files may be modified.")
        resolved = target.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("Patch path escapes workspace.") from exc
        if len(change.content.encode("utf-8")) > 200_000:
            raise ValueError("Replacement file is too large.")
        # Read now so write failures can be handled by workspace rollback upstream.
        original = target.read_text(encoding="utf-8", errors="replace")
        prepared.append((target, original, change.content))

    for target, _original, content in prepared:
        target.write_text(content, encoding="utf-8")
    return [change.path for change in patch.changes]
