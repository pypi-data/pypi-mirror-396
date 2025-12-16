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
