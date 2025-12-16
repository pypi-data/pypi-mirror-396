"""config"""

import os
from pathlib import Path


PACKAGE_NAME = "bardata"


def cache_dir(*, mkdir: bool = True) -> Path:
    CACHE_HOME = os.getenv("XDG_CACHE_HOME", "~/.cache")

    cache_dir = Path(CACHE_HOME, PACKAGE_NAME).expanduser()

    if mkdir:
        cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


