import os
import sys
from pathlib import Path


def abbr_path(path: str | os.PathLike[str], truncation_symbol: str = "󰇘/") -> str:
    path = Path(path)
    for prefix in sys.path:
        if path.is_relative_to(prefix):
            return f"{truncation_symbol}{path.relative_to(prefix)}"
    return str(path)
