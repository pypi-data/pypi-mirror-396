"""Dry-run auditor: list what would be included in the build without running PyInstaller."""
from typing import List, Tuple
from pathlib import Path


def dry_run_report(spec_path: str, datas: List[Tuple[str, str]], binaries: List[Tuple[str, str]], hiddenimports: List[str] | None = None):
    print("DRY-RUN REPORT")
    print("Spec:", spec_path)
    print("Hidden imports:")
    for h in (hiddenimports or []):
        print(" -", h)
    print("Datas:")
    for s, d in datas:
        print(" -", s, "->", d)
    print("Binaries:")
    for s, d in binaries:
        print(" -", s, "->", d)
    print("End of dry-run. No build performed.")
