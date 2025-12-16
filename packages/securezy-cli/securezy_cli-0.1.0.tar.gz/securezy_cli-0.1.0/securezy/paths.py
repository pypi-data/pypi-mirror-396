from __future__ import annotations

import os
from pathlib import Path


def get_app_dir() -> Path:
    override = os.getenv("SECUREZY_HOME")
    if override:
        return Path(override)

    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "securezy"

    return Path.home() / ".securezy"


def ensure_app_dir() -> Path:
    p = get_app_dir()
    p.mkdir(parents=True, exist_ok=True)
    return p
