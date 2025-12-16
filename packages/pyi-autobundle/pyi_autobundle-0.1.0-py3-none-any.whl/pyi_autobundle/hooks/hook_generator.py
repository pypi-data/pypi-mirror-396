"""Automatically generate PyInstaller hook files from collected assets.

This implementation creates per-module `hook-<module>.py` files when possible,
placing datas/binaries located under a module's package directory into that
module's hook. Any remaining assets are written to `hook-auto.py`.
"""
from pathlib import Path
from typing import List, Tuple, Optional
import importlib.util
from .hardcoded_hooks import hidden_imports_for


HOOK_TEMPLATE = """
# Auto-generated hook for {module}
hiddenimports = {hidden}
datas = {datas}
binaries = {binaries}
"""


def _module_path(module: str) -> Optional[Path]:
    try:
        spec = importlib.util.find_spec(module)
    except Exception:
        return None
    if not spec or not spec.origin:
        return None
    origin = Path(spec.origin)
    if origin.name == "__init__.py":
        return origin.parent.resolve()
    return origin.resolve()


def generate_hooks(out_dir: Path, datas: List[Tuple[str, str]], binaries: List[Tuple[str, str]], modules: List[str], hiddenimports: Optional[List[str]] = None) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    remaining_datas = list(datas)
    remaining_bins = list(binaries)
    created = []

    # Group assets under module hooks when possible
    for mod in sorted(set(modules)):
        mod_path = _module_path(mod)
        if not mod_path:
            continue

        mod_datas = []
        mod_bins = []

        # collect datas under module path
        for src, dest in list(remaining_datas):
            try:
                if Path(src).resolve().is_relative_to(mod_path):
                    mod_datas.append((src, dest))
                    remaining_datas.remove((src, dest))
            except Exception:
                # Path.is_relative_to may raise if paths unrelated
                pass

        for src, dest in list(remaining_bins):
            try:
                if Path(src).resolve().is_relative_to(mod_path):
                    mod_bins.append((src, dest))
                    remaining_bins.remove((src, dest))
            except Exception:
                pass

        if not mod_datas and not mod_bins and not hidden_imports_for([mod]):
            continue

        hid = hidden_imports_for([mod])
        # also include any global hiddenimports that reference this module name
        if hiddenimports:
            for h in hiddenimports:
                if h.startswith(mod + ".") or h == mod:
                    hid.append(h)

        name = f"hook-{mod.replace('.', '_')}.py"
        content = HOOK_TEMPLATE.format(module=mod, hidden=repr(sorted(set(hid))), datas=repr(mod_datas), binaries=repr(mod_bins))
        fpath = out_dir / name
        fpath.write_text(content, encoding="utf8")
        created.append(fpath)

    # leftover assets go into a generic hook-auto.py
    content = HOOK_TEMPLATE.format(module="auto", hidden=repr(sorted(set(hiddenimports or []))), datas=repr(remaining_datas), binaries=repr(remaining_bins))
    fpath = out_dir / "hook-auto.py"
    fpath.write_text(content, encoding="utf8")
    created.append(fpath)

    return created
