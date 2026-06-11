from pathlib import Path
from typing import Iterable


def ensure_dirs(paths: Iterable[Path]):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)
