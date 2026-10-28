import os
from pathlib import Path

IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache"}
ALLOWED_SUFFIXES = {".py", ".toml", ".ini", ".cfg", ".json", ".yaml", ".yml", ".txt", ".md"}


def scan_repository(root: str) -> list[str]:
    root_path = Path(root).resolve()
    files: list[str] = []
    for current_root, dirs, filenames in os.walk(root_path, followlinks=False):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        for filename in filenames:
            path = Path(current_root) / filename
            if path.is_symlink() or path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            try:
                path.resolve().relative_to(root_path)
            except (ValueError, OSError):
                continue
            if path.is_file() and path.stat().st_size <= 200_000:
                files.append(path.relative_to(root_path).as_posix())
    return sorted(files)


def read_source_file(root: str, relative_path: str, max_chars: int = 12000) -> str:
    root_path = Path(root).resolve()
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Unsafe relative path.")
    target = root_path / relative
    if target.is_symlink() or not target.is_file() or target.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError("Unsupported or unsafe source file.")
    try:
        target.resolve().relative_to(root_path)
    except ValueError as exc:
        raise ValueError("File path escapes project directory.") from exc
    return target.read_text(encoding="utf-8", errors="replace")[:max_chars]
