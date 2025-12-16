"""Utility functions for resolving modules and resources."""
from importlib import util
from pathlib import Path
from typing import Optional


def resolve_module_path(module_name: str) -> Optional[Path]:
    """Return filesystem Path to module or package, or None if not found."""
    try:
        spec = util.find_spec(module_name)
    except Exception:
        return None
    if not spec or not spec.origin:
        return None
    origin = Path(spec.origin)
    if origin.name == "__init__.py":
        return origin.parent
    return origin
