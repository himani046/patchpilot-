from pathlib import Path


def ensure_within(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes the allowed root.") from exc
    return resolved
