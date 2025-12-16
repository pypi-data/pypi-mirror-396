from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib import metadata
from typing import Callable, Dict, List


@dataclass(frozen=True)
class Plugin:
    name: str
    run: Callable[[List[str]], int]


def load_plugins() -> Dict[str, Plugin]:
    eps = metadata.entry_points()

    group = None
    if hasattr(eps, "select"):
        group = eps.select(group="securezy.plugins")
    else:
        group = eps.get("securezy.plugins", [])

    plugins: Dict[str, Plugin] = {}
    for ep in group:
        try:
            obj = ep.load()
        except Exception:
            continue

        def _wrap(f):
            def _run(args: List[str]) -> int:
                return int(f(args))

            return _run

        plugins[ep.name] = Plugin(name=ep.name, run=_wrap(obj))

    if "hello" not in plugins:
        try:
            mod = import_module("securezy.plugins.hello")
            plugins["hello"] = Plugin(name="hello", run=lambda args: int(mod.run(args)))
        except Exception:
            pass

    return plugins
