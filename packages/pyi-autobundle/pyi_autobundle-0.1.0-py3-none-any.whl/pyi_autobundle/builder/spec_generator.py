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
             pathex=[{pathex}],
             binaries={binaries},
             datas={datas},
             hiddenimports={hiddenimports},
             hookspath=[{hookspath}],
             runtime_hooks=[],
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


def generate_spec(entry: str, datas: List[Tuple[str, str]], binaries: List[Tuple[str, str]], hiddenimports: List[str], outdir: str = "dist", onefile: bool = False, windowed: bool = False) -> str:
    entry = str(entry)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    name = Path(entry).stem
    spec_path = outdir / (name + ".spec")

    pathex = "",  # empty tuple for now
    hookspath = ".pyi-hooks",

    # For now we keep a simple spec; `onefile` toggles console/windowed behaviour.
    text = SPEC_TEMPLATE.format(
        entry=entry,
        pathex=repr([]),
        binaries=_repr_list_of_pairs(binaries),
        datas=_repr_list_of_pairs(datas),
        hiddenimports=repr(hiddenimports),
        hookspath=repr(hookspath),
        name=name,
    )
    spec_path.write_text(text, encoding="utf8")
    return str(spec_path)
