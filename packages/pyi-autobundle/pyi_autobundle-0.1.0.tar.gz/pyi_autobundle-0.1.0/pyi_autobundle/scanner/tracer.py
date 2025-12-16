"""Runtime import tracer that runs the entry script in a subprocess and records imports."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Set


RUNNER_TEMPLATE = r"""
import runpy, sys, json
import importlib.abc

seen = set()

class Tracker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        seen.add(fullname.split('.')[0])
        return None

sys.meta_path.insert(0, Tracker())
try:
    runpy.run_path(sys.argv[1], run_name='__main__')
except SystemExit:
    pass
print(json.dumps(sorted(list(seen))))
"""


def trace_imports(entry_path: str, timeout: int | None = 30) -> Set[str]:
    """Execute the entry script in a subprocess with an import-tracking runner.

    Returns a set of top-level module/package names discovered at runtime.
    """
    entry = Path(entry_path)
    if not entry.exists():
        raise FileNotFoundError(entry_path)

    with tempfile.NamedTemporaryFile("w", suffix="_pyi_tracer.py", delete=False, encoding="utf8") as tf:
        tf.write(RUNNER_TEMPLATE)
        runner_path = tf.name

    cmd = [sys.executable, runner_path, str(entry)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode not in (0, None):
            # still try to parse stdout
            pass
        out = proc.stdout.strip()
        if not out:
            return set()
        data = json.loads(out)
        return set(data)
    finally:
        try:
            Path(runner_path).unlink()
        except Exception:
            pass
