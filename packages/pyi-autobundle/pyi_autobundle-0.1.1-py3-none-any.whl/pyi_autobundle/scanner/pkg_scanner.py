"""Package scanner: resolve module paths and collect data files and binaries."""
from importlib import util
from pathlib import Path
from typing import Iterable, List, Set, Tuple, Optional
import os
from fnmatch import fnmatch


def _match_ignore(path: str, patterns: Optional[List[str]]):
    if not patterns:
        return False
    for pat in patterns:
        if fnmatch(path, pat) or fnmatch(os.path.basename(path), pat):
            return True
    return False

DATA_EXT = {".txt", ".json", ".png", ".jpg", ".jpeg", ".html", ".xml", ".csv", ".npy", ".npz"}
BINARY_EXT = {".so", ".pyd", ".dll"}


def _find_module_path(modname: str) -> Path | None:
    try:
        spec = util.find_spec(modname)
    except Exception:
        return None
    if not spec or not spec.origin:
        return None
    origin = Path(spec.origin)
    if origin.name == "__init__.py":
        return origin.parent
    return origin


def scan_packages_for_assets(modules: Iterable[str], extra_resources: Optional[List[str]] = None, ignore_patterns: Optional[List[str]] = None) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Return (datas, binaries) suitable for PyInstaller: lists of (src, dest).

    - datas: list of (file_or_dir, dest_relative)
    - binaries: list of (file, dest_relative)
    """
    datas = []
    binaries = []
    seen_dirs: Set[Path] = set()

    for m in sorted(set(modules)):
        path = _find_module_path(m)
        if not path or not path.exists():
            continue
        if _match_ignore(m, ignore_patterns):
            continue
        if path.is_file():
            # a single file module
            parent = path.parent
        else:
            parent = path

        if parent in seen_dirs:
            continue
        seen_dirs.add(parent)

        # Walk and collect
        for root, dirs, files in os.walk(parent):
            rootp = Path(root)
            for f in files:
                p = rootp / f
                ext = p.suffix.lower()
                rel = p.relative_to(parent)
                if ext in DATA_EXT:
                    datas.append((str(p), str(rel.parent)))
                elif ext in BINARY_EXT:
                    binaries.append((str(p), str(rel.parent)))

    # include explicit extra_resources (relative paths from project)
    if extra_resources:
        for r in extra_resources:
            rp = Path(r)
            if not rp.exists():
                # try relative to cwd
                rp = Path(os.getcwd()) / r
            if rp.exists() and not _match_ignore(str(rp), ignore_patterns):
                datas.append((str(rp), "."))

    return datas, binaries
