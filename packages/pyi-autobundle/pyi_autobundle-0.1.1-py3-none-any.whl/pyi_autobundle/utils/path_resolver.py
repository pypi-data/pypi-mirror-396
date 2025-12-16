"""Cross-platform path normalization utilities."""
import os
from pathlib import Path


def normalize_dest(dest: str) -> str:
    """Normalize a destination folder path for PyInstaller hook usage.

    Ensures forward slashes and strips leading/trailing separators.
    """
    if not dest:
        return "."
    p = Path(dest)
    # Use posix style relative path used by PyInstaller datas/binaries dest
    parts = p.parts
    return "/".join(parts).lstrip("/")


def join_for_platform(*parts: str) -> str:
    """Join path parts using the current platform separator.

    Useful when generating shell commands or paths consumed by OS.
    """
    return os.path.join(*parts)
