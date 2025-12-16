"""Package scanner: resolve module paths and collect data files and binaries."""
from importlib import util
import importlib.metadata as md
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
        # First, include common package data directories entirely (e.g. mpl-data, assets)
        common_data_dirs = ["mpl-data", "assets", "data", "resources", "templates", "mpl-data"]
        for dname in common_data_dirs:
            dpath = parent / dname
            if dpath.exists() and dpath.is_dir() and not _match_ignore(str(dpath), ignore_patterns):
                # add the whole directory as a datas entry
                pkg_dest = m.replace('.', '/') + f"/{dname}"
                datas.append((str(dpath), pkg_dest))

        for root, dirs, files in os.walk(parent):
            rootp = Path(root)
            for f in files:
                p = rootp / f
                ext = p.suffix.lower()
                rel = p.relative_to(parent)
                # Destination inside the bundle should include the package name so
                # runtime resource lookups (package-relative) find them under
                # _internal/<package>/...
                pkg_dest_prefix = m.replace('.', '/')
                rel_parent = str(rel.parent) if str(rel.parent) != '.' else ''
                if rel_parent:
                    dest = f"{pkg_dest_prefix}/{rel_parent}"
                else:
                    dest = f"{pkg_dest_prefix}"
                # include files that look like data even without extensions (e.g. matplotlibrc)
                if ext in DATA_EXT or (ext == '' and p.name.lower() in ("matplotlibrc", "fonts", "fontlist-v310.json")):
                    datas.append((str(p), dest))
                elif ext in BINARY_EXT:
                    binaries.append((str(p), dest))

    # include explicit extra_resources (relative paths from project)
    if extra_resources:
        for r in extra_resources:
            rp = Path(r)
            if not rp.exists():
                # try relative to cwd
                rp = Path(os.getcwd()) / r
            if rp.exists() and not _match_ignore(str(rp), ignore_patterns):
                datas.append((str(rp), "."))

    # Also inspect installed distributions for package data using importlib.metadata
    try:
        dist_datas, dist_bins = scan_distributions_for_assets(modules, ignore_patterns=ignore_patterns)
        # Merge, avoiding duplicates
        for s, d in dist_datas:
            if (s, d) not in datas:
                datas.append((s, d))
        for s, d in dist_bins:
            if (s, d) not in binaries:
                binaries.append((s, d))
    except Exception:
        # don't fail the whole scan if metadata inspection isn't available or errors
        pass

    return datas, binaries


def scan_distributions_for_assets(modules: Iterable[str], ignore_patterns: Optional[List[str]] = None) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Inspect installed distributions for files that should be packaged as datas/binaries.

    Uses importlib.metadata to map top-level packages to distributions and includes
    files matching known data extensions or common data directories (e.g., mpl-data, assets).
    Returns lists of (abs_src, dest_rel) suitable for PyInstaller.
    """
    datas: List[Tuple[str, str]] = []
    binaries: List[Tuple[str, str]] = []

    # map top-level package -> distributions that provide it
    try:
        pkg_map = md.packages_distributions()
    except Exception:
        pkg_map = {}

    for m in sorted(set(modules)):
        dist_names = pkg_map.get(m, [])
        for dist_name in dist_names:
            try:
                dist = md.distribution(dist_name)
            except Exception:
                continue
            for member in dist.files or []:
                # member is a PackagePath (path-like inside the distribution)
                mp = Path(str(member))
                # skip metadata files
                if str(mp).startswith('EGG-INFO') or str(mp).endswith('.dist-info'):
                    continue

                full = dist.locate_file(member)
                if not full.exists():
                    continue

                # decide dest path: keep package prefix so runtime finds resources
                pkg_dest_prefix = m.replace('.', '/')
                rel_parts = list(mp.parts)
                # if member points inside the top-level package folder, drop any unrelated leading parts
                if rel_parts and rel_parts[0] == m.split('.')[0]:
                    rel = Path(*rel_parts[1:])
                else:
                    rel = Path(*rel_parts)

                dest_parent = str(rel.parent) if str(rel.parent) != '.' else ''
                dest = f"{pkg_dest_prefix}/{dest_parent}" if dest_parent else f"{pkg_dest_prefix}"

                ext = mp.suffix.lower()
                if ext in DATA_EXT or (ext == '' and mp.name.lower() in ("matplotlibrc",)):
                    if not _match_ignore(str(full), ignore_patterns):
                        datas.append((str(full), dest))
                elif ext in BINARY_EXT:
                    if not _match_ignore(str(full), ignore_patterns):
                        binaries.append((str(full), dest))

    return datas, binaries
