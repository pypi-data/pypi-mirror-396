"""Generate a PyInstaller .spec file from discovered inputs."""
from pathlib import Path
from typing import List, Tuple


SPEC_TEMPLATE = '''# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules
block_cipher = None

a = Analysis([
    {entry!r}
],
             pathex={pathex},
             binaries={binaries},
             datas={datas},
             hiddenimports={hiddenimports},
             hookspath={hookspath},
             runtime_hooks={runtime_hooks},
             excludes={excludes},
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name={name!r},
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name={name!r})
'''


def _repr_list_of_pairs(items: List[Tuple[str, str]]):
    return repr(list(items))


def generate_spec(entry: str, datas: List[Tuple[str, str]], binaries: List[Tuple[str, str]], hiddenimports: List[str], outdir: str = "dist", onefile: bool = False, windowed: bool = False, runtime_hook_paths: List[str] | None = None, excludes: List[str] | None = None) -> str:
    # ensure entry is absolute so PyInstaller resolves it regardless of spec location
    entry_path = Path(entry).resolve()
    entry = str(entry_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    name = Path(entry).stem
    spec_path = outdir / (name + ".spec")
    # include the script directory in pathex so PyInstaller can resolve relative imports
    pathex_list = [str(entry_path.parent.resolve())]
    # make hookspath absolute so hooks are found even if spec is written to a different dir
    hookspath = str(Path('.pyi-hooks').resolve())
    # runtime hooks may be provided by the caller (written into the output
    # directory as "output-only" hooks). If not provided, fall back to
    # scanning the repo-level .pyi-hooks directory for rt-hook-*.py.
    if runtime_hook_paths is not None:
        runtime_hooks_list = list(runtime_hook_paths)
    else:
        runtime_hooks_list = []
        try:
            for p in Path('.pyi-hooks').glob('rt-hook-*.py'):
                runtime_hooks_list.append(str(p.resolve()))
        except Exception:
            runtime_hooks_list = []

    # For now we keep a simple spec; `onefile` toggles console/windowed behaviour.
    # sanitize dest dirs: PyInstaller requires dest to be non-empty (use '.' for top-level)
    def _sanitize(items: List[Tuple[str, str]]):
        out = []
        for src, dest in items:
            if not dest:
                dest = "."
            out.append((src, dest))
        return out

    datas_s = _sanitize(datas)
    binaries_s = _sanitize(binaries)

    if excludes is None:
        excludes = []

    text = SPEC_TEMPLATE.format(
        entry=entry,
        pathex=repr(pathex_list),
        binaries=_repr_list_of_pairs(binaries_s),
        datas=_repr_list_of_pairs(datas_s),
        hiddenimports=repr(hiddenimports),
        hookspath=repr([hookspath]),
        runtime_hooks=repr(runtime_hooks_list),
        excludes=repr(excludes),
        name=name,
    )
    spec_path.write_text(text, encoding="utf8")
    return str(spec_path)
