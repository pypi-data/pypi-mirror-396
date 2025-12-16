"""Parse a simple .buildignore file and provide matching utilities."""
from pathlib import Path
from typing import List


def load_buildignore(path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        return []
    lines = []
    for line in p.read_text(encoding="utf8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines
