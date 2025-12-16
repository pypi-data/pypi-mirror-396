"""Static AST-based import scanner."""
import ast
from pathlib import Path
from typing import Set, List


def _gather_from_ast(node: ast.AST, collected: Set[str]):
    # Walk AST looking for import statements and dynamic import calls
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                collected.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                collected.add(n.module.split(".")[0])
        elif isinstance(n, ast.Call):
            # detect __import__("mod") or importlib.import_module("mod")
            func = n.func
            if isinstance(func, ast.Name) and func.id == "__import__" and n.args:
                arg = n.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    collected.add(arg.value.split(".")[0])
            elif isinstance(func, ast.Attribute):
                # detect importlib.import_module("mod") or similar attribute calls
                if getattr(func, "attr", "") == "import_module" and n.args:
                    arg = n.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        collected.add(arg.value.split(".")[0])


def scan_for_resources(path: str) -> List[str]:
    """Scan source for `get_resource_path("path/to/file")` style calls and return literal paths found.

    This allows automatic inclusion of assets referenced through a helper.
    """
    p = Path(path)
    src = p.read_text(encoding="utf8")
    tree = ast.parse(src, filename=str(p))
    found: List[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            func = n.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name == "get_resource_path" and n.args:
                arg = n.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.append(arg.value)
    return found


def _resolve_local_module_file(module: str, project_root: str) -> Path | None:
    """Try to resolve a module name to a local file under `project_root`.

    Returns a Path to the .py file or package __init__.py when found, otherwise None.
    """
    root = Path(project_root)
    parts = module.split('.')
    # try module as file
    candidate = root.joinpath(*parts).with_suffix('.py')
    if candidate.exists():
        return candidate.resolve()
    # try package __init__.py
    pkg_init = root.joinpath(*parts, '__init__.py')
    if pkg_init.exists():
        return pkg_init.resolve()
    return None


def scan_imports_recursive(entry_path: str, project_root: str | None = None) -> tuple[Set[str], List[str]]:
    """Recursively scan the entry file and any local modules it imports.

    Returns a tuple `(modules, files_scanned)` where `modules` is a set of top-level
    module names discovered and `files_scanned` is the list of filesystem paths that
    were statically scanned.
    """
    entry = Path(entry_path)
    if not entry.exists():
        raise FileNotFoundError(entry_path)

    project_root = Path(project_root).resolve() if project_root else Path('.').resolve()

    to_scan = [entry.resolve()]
    scanned_files: Set[Path] = set()
    found_modules: Set[str] = set()

    while to_scan:
        p = to_scan.pop()
        if p in scanned_files:
            continue
        scanned_files.add(p)
        try:
            mods = scan_imports(str(p))
        except Exception:
            mods = set()
        found_modules.update(mods)

        # For each imported module, if it resolves to a local file under project_root, scan it too
        for m in mods:
            local = _resolve_local_module_file(m, str(project_root))
            if local and local not in scanned_files:
                to_scan.append(local)

    return found_modules, [str(p) for p in sorted(scanned_files)]


def scan_imports(path: str) -> Set[str]:
    """Return a set of top-level module/package names imported by the file at `path`.

    This is a conservative static scanner using AST and basic dynamic import detection.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    src = p.read_text(encoding="utf8")
    tree = ast.parse(src, filename=str(p))
    found = set()
    _gather_from_ast(tree, found)
    return found
