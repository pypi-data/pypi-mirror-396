from __future__ import annotations

import base64
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _b64url_decode(data: str) -> bytes:
    s = data.strip()
    if not s:
        raise ValueError("empty segment")
    pad = (-len(s)) % 4
    s_padded = s + ("=" * pad)
    return base64.urlsafe_b64decode(s_padded.encode("ascii"))


def _decode_json_segment(seg: str) -> Dict[str, Any]:
    raw = _b64url_decode(seg)
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"invalid json: {e}") from e
    if not isinstance(obj, dict):
        raise ValueError("segment json is not an object")
    return obj


def _parse_jwt(token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("token must have 3 dot-separated parts")
    header = _decode_json_segment(parts[0])
    payload = _decode_json_segment(parts[1])
    return header, payload


def _parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
            return int(v)
    return None


def _ts_to_iso(ts: Optional[int]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def jwt_inspect_one(
    token: str,
    *,
    skew_seconds: int = 60,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    now_dt = now or datetime.now(timezone.utc)
    if now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    result: Dict[str, Any] = {
        "type": "jwt_inspect",
        "generated_at": generated_at,
        "skew_seconds": int(skew_seconds),
        "header": None,
        "payload": None,
        "claims": {
            "iss": None,
            "aud": None,
            "sub": None,
            "kid": None,
            "alg": None,
            "exp": None,
            "nbf": None,
            "iat": None,
            "exp_iso": None,
            "nbf_iso": None,
            "iat_iso": None,
        },
        "status": {"ok": False, "warning": False, "error": None, "messages": []},
    }

    try:
        header, payload = _parse_jwt(token)
        result["header"] = header
        result["payload"] = payload

        alg = header.get("alg")
        kid = header.get("kid")
        iss = payload.get("iss")
        aud = payload.get("aud")
        sub = payload.get("sub")

        exp = _parse_int(payload.get("exp"))
        nbf = _parse_int(payload.get("nbf"))
        iat = _parse_int(payload.get("iat"))

        result["claims"].update(
            {
                "iss": iss,
                "aud": aud,
                "sub": sub,
                "kid": kid,
                "alg": alg,
                "exp": exp,
                "nbf": nbf,
                "iat": iat,
                "exp_iso": _ts_to_iso(exp),
                "nbf_iso": _ts_to_iso(nbf),
                "iat_iso": _ts_to_iso(iat),
            }
        )

        messages: List[str] = []
        warning = False

        if isinstance(alg, str) and alg.strip().lower() == "none":
            warning = True
            messages.append("alg=none")

        skew = timedelta(seconds=int(skew_seconds))

        if exp is None:
            warning = True
            messages.append("exp is missing or not an integer")
        else:
            exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
            if exp_dt < (now_dt - skew):
                warning = True
                messages.append("token is expired")

        if nbf is not None:
            nbf_dt = datetime.fromtimestamp(nbf, tz=timezone.utc)
            if nbf_dt > (now_dt + skew):
                warning = True
                messages.append("nbf is in the future")

        if iat is not None:
            iat_dt = datetime.fromtimestamp(iat, tz=timezone.utc)
            if iat_dt > (now_dt + skew):
                warning = True
                messages.append("iat is in the future")

        result["status"] = {
            "ok": not warning,
            "warning": warning,
            "error": None,
            "messages": messages,
        }
        return result

    except Exception as e:
        result["status"] = {
            "ok": False,
            "warning": False,
            "error": f"{type(e).__name__}: {e}",
            "messages": [],
        }
        return result


def parse_jwt_tokens_file(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: List[str] = []
    for line in lines:
        raw = line.split("#", 1)[0].strip()
        if not raw:
            continue
        out.append(raw)
    return out


def jwt_inspect_batch(
    tokens: List[str],
    *,
    skew_seconds: int = 60,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()

    results: List[Dict[str, Any]] = []
    for tok in tokens:
        results.append(jwt_inspect_one(tok, skew_seconds=skew_seconds, now=now))

    ok_n = sum(1 for r in results if r["status"]["ok"] and not r["status"]["warning"])
    warn_n = sum(1 for r in results if r["status"]["warning"])
    err_n = sum(1 for r in results if r["status"]["error"] is not None)

    return {
        "type": "jwt_inspect_batch",
        "generated_at": generated_at,
        "skew_seconds": int(skew_seconds),
        "summary": {"total": len(results), "ok": ok_n, "warning": warn_n, "error": err_n},
        "results": results,
    }
