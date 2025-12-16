"""Command-line entrypoint for pyi-autobundle."""
import argparse
import sys
from pathlib import Path
import os
try:
    import tomllib as _tomllib
except Exception:
    _tomllib = None

from .scanner.import_scanner import scan_imports, scan_for_resources
from .scanner.tracer import trace_imports
from .scanner.pkg_scanner import scan_packages_for_assets
from .hooks.hook_generator import generate_hooks
from .hooks.hardcoded_hooks import hidden_imports_for
from .builder.spec_generator import generate_spec
from .builder.pyinstaller_runner import run_pyinstaller
from .utils.buildignore import load_buildignore
from .utils.path_resolver import normalize_dest


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="pybundle")
    parser.add_argument("entry", help="Entry script (e.g. main.py)")
    parser.add_argument("--out", default="dist", help="Output folder for PyInstaller")
    parser.add_argument("--hooks-dir", default=".pyi-hooks", help="Directory to write generated hooks")
    parser.add_argument("--trace", action="store_true", help="Run runtime import tracer in addition to static scan")
    parser.add_argument("--spec-only", action="store_true", help="Generate spec and hooks but don't run PyInstaller")
    parser.add_argument("--onefile", action="store_true", help="Build single-file executable (PyInstaller --onefile)")
    parser.add_argument("--onedir", action="store_true", help="Build directory bundle (default)")
    parser.add_argument("--windowed", action="store_true", help="Build windowed app (no console)")
    parser.add_argument("--buildignore", default=".buildignore", help="Path to .buildignore file to exclude files/dirs")
    parser.add_argument("--dry-run", action="store_true", help="List files/modules that would be included, then exit")
    args, unknown = parser.parse_known_args(argv)

    entry = Path(args.entry)
    if not entry.exists():
        print(f"Entry script not found: {entry}")
        raise SystemExit(2)

    # merge config from pyproject.toml (optional)
    config = {}
    pyproject = Path("pyproject.toml")
    if pyproject.exists() and _tomllib is not None:
        try:
            with pyproject.open("rb") as f:
                doc = _tomllib.load(f)
            config = doc.get("tool", {}).get("pyi-autobundle", {})
        except Exception:
            config = {}

    print("Scanning imports (static)...")
    found = scan_imports(str(entry))
    resources = scan_for_resources(str(entry))

    if args.trace:
        print("Tracing imports (runtime)...")
        traced = trace_imports(str(entry))
        found.update(traced)

    # load buildignore patterns
    buildignore = load_buildignore(args.buildignore) if args.buildignore else []

    print(f"Found {len(found)} modules/packages")

    print("Scanning packages for assets and binaries...")
    datas, binaries = scan_packages_for_assets(found, extra_resources=resources, ignore_patterns=buildignore)

    # include hidden imports for known packages
    hid = hidden_imports_for(list(found))
    if hid:
        print(f"Adding {len(hid)} built-in hiddenimports for known packages")

    # normalize destination paths for datas/binaries
    datas = [(src, normalize_dest(dest)) for src, dest in datas]
    binaries = [(src, normalize_dest(dest)) for src, dest in binaries]

    hooks_dir = Path(args.hooks_dir)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    print(f"Generating hooks into {hooks_dir}")
    # generate per-module hooks where possible
    generate_hooks(hooks_dir, datas, binaries, modules=list(found), hiddenimports=hid)

    print("Generating PyInstaller spec...")
    spec_path = generate_spec(str(entry), datas, binaries, list(found), outdir=args.out, hiddenimports=hid, onefile=args.onefile or config.get("onefile", False), windowed=args.windowed or config.get("windowed", False))
    print(f"Spec written to: {spec_path}")

    if not args.spec_only:
        if args.dry_run:
            from .builder.dryrun import dry_run_report
            dry_run_report(spec_path, datas, binaries, hiddenimports=hid)
        else:
            # pass any unknown args directly to PyInstaller
            print("Running PyInstaller...")
            run_pyinstaller(spec_path, args.out, extra_args=unknown)
        


if __name__ == "__main__":
    main()
