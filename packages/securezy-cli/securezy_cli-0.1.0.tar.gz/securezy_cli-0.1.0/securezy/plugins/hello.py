from __future__ import annotations

from typing import List


def run(args: List[str]) -> int:
    msg = " ".join(args) if args else "hello"
    print(msg)
    return 0
