from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_AMBIGUOUS = set("O0Il1")


def _normalize_preset(preset: str) -> str:
    p = (preset or "").strip().lower()
    if p in {"site", "hex", "base64url"}:
        return p
    raise ValueError("unsupported preset")


def _site_charset(*, no_ambiguous: bool) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    symbols = "!@#$%^&*()-_=+[]{}:,.?"
    chars = alphabet + symbols
    if no_ambiguous:
        chars = "".join(c for c in chars if c not in _AMBIGUOUS)
    if not chars:
        raise ValueError("empty charset")
    return chars


def generate_one(
    *,
    preset: str,
    length: Optional[int] = None,
    nbytes: Optional[int] = None,
    no_ambiguous: bool = False,
) -> str:
    p = _normalize_preset(preset)

    if p == "site":
        ln = 24 if length is None else int(length)
        if ln <= 0 or ln > 4096:
            raise ValueError("invalid length")
        chars = _site_charset(no_ambiguous=no_ambiguous)
        return "".join(secrets.choice(chars) for _ in range(ln))

    if nbytes is None:
        nb = 32
    else:
        nb = int(nbytes)
    if nb <= 0 or nb > 4096:
        raise ValueError("invalid bytes")

    if p == "hex":
        return secrets.token_hex(nb)

    if p == "base64url":
        return secrets.token_urlsafe(nb)

    raise ValueError("unsupported preset")


def pwgen_payload(
    *,
    preset: str,
    length: Optional[int],
    nbytes: Optional[int],
    count: int,
    no_ambiguous: bool,
) -> Dict[str, Any]:
    p = _normalize_preset(preset)
    c = int(count)
    if c <= 0 or c > 10000:
        raise ValueError("invalid count")

    generated_at = datetime.now(timezone.utc).isoformat()

    if c == 1:
        value = generate_one(preset=p, length=length, nbytes=nbytes, no_ambiguous=no_ambiguous)
        return {
            "type": "pwgen",
            "generated_at": generated_at,
            "preset": p,
            "length": int(length) if (length is not None) else None,
            "bytes": int(nbytes) if (nbytes is not None) else None,
            "no_ambiguous": bool(no_ambiguous),
            "value": value,
            "status": {"ok": True, "warning": False, "error": None},
        }

    values: List[str] = []
    for _ in range(c):
        values.append(generate_one(preset=p, length=length, nbytes=nbytes, no_ambiguous=no_ambiguous))

    return {
        "type": "pwgen_batch",
        "generated_at": generated_at,
        "preset": p,
        "length": int(length) if (length is not None) else None,
        "bytes": int(nbytes) if (nbytes is not None) else None,
        "no_ambiguous": bool(no_ambiguous),
        "summary": {"total": len(values), "ok": len(values), "warning": 0, "error": 0},
        "results": values,
    }
