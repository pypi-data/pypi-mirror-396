from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from securezy.paths import ensure_app_dir


@dataclass(frozen=True)
class PortScanProfile:
    name: str
    target: str
    ports: str
    concurrency: int
    timeout: float


def _profiles_path() -> Path:
    return ensure_app_dir() / "profiles.json"


def _read_profiles() -> Dict[str, PortScanProfile]:
    path = _profiles_path()
    if not path.exists():
        return {}

    raw = json.loads(path.read_text(encoding="utf-8") or "{}")
    out: Dict[str, PortScanProfile] = {}
    for name, data in raw.items():
        out[name] = PortScanProfile(
            name=name,
            target=str(data["target"]),
            ports=str(data["ports"]),
            concurrency=int(data["concurrency"]),
            timeout=float(data["timeout"]),
        )
    return out


def _write_profiles(profiles: Dict[str, PortScanProfile]) -> None:
    path = _profiles_path()
    tmp = path.with_suffix(".tmp")
    payload = {name: asdict(p) for name, p in profiles.items()}
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def set_profile(profile: PortScanProfile) -> None:
    profiles = _read_profiles()
    profiles[profile.name] = profile
    _write_profiles(profiles)


def get_profile(name: str) -> PortScanProfile:
    profiles = _read_profiles()
    if name not in profiles:
        raise KeyError(name)
    return profiles[name]


def delete_profile(name: str) -> None:
    profiles = _read_profiles()
    if name in profiles:
        del profiles[name]
        _write_profiles(profiles)


def list_profiles() -> List[PortScanProfile]:
    profiles = _read_profiles()
    return [profiles[k] for k in sorted(profiles.keys())]


def profiles_file_path() -> Path:
    return _profiles_path()
