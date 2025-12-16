"""Internal hidden-imports database for common problematic packages."""
from typing import List


DEFAULTS = {
    "numpy": ["numpy.core._methods", "numpy.lib.format"],
    "pandas": ["pandas._libs.tslibs", "pandas.io.parsers"],
    "torch": ["torch._C"],
    "PIL": ["PIL._imaging"],
}


def hidden_imports_for(modules: List[str]) -> List[str]:
    out = []
    mods = set(m.lower() for m in modules)
    for key, hid in DEFAULTS.items():
        if key.lower() in mods:
            out.extend(hid)
    return sorted(set(out))
