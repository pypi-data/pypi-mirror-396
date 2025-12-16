"""Write runtime hook files into the build output directory.

This module creates an output-only runtime hook directory under the PyInstaller
output (`outdir/.pyi-runtime-hooks`) and writes hook source files there. The
spec should then reference these files via `runtime_hooks` so they are bundled
with the frozen application without committing hooks into the library repo.
"""
from pathlib import Path
from typing import Dict, List


def write_runtime_hooks(outdir: str, hooks: Dict[str, str]) -> List[str]:
    """Write provided hooks into `outdir/.pyi-runtime-hooks`.

    Args:
        outdir: output directory (where spec will be written)
        hooks: mapping filename -> source code

    Returns:
        list of absolute paths to written hook files
    """
    out = Path(outdir)
    hooks_dir = out / ".pyi-runtime-hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, src in hooks.items():
        p = hooks_dir / name
        p.write_text(src, encoding="utf8")
        written.append(str(p.resolve()))
    return written
