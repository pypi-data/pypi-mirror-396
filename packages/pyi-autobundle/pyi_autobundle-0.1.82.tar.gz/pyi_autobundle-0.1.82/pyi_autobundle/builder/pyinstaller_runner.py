"""Run PyInstaller with a generated spec file."""
import subprocess
import sys
from pathlib import Path


def run_pyinstaller(spec_path: str, outdir: str, extra_args: list | None = None):
    spec = Path(spec_path)
    if not spec.exists():
        raise FileNotFoundError(spec_path)
    cmd = [sys.executable, "-m", "PyInstaller", str(spec), "--distpath", str(outdir)]
    if extra_args:
        # extend with any extra args passed through the CLI
        cmd.extend(extra_args)
    print("Calling:", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
