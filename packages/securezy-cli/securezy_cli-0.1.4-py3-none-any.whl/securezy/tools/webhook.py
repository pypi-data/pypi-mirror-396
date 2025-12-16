from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _normalize_algo(algo: str) -> str:
    a = algo.strip().lower().replace("-", "")
    if a in {"sha256", "sha384", "sha512"}:
        return a
    raise ValueError("unsupported algo")


def _payload_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def hmac_sign(payload: bytes, *, secret: bytes, algo: str) -> bytes:
    a = _normalize_algo(algo)
    digestmod = getattr(hashlib, a)
    return hmac.new(secret, payload, digestmod).digest()


def encode_signature(sig: bytes, *, encoding: str) -> str:
    e = encoding.strip().lower()
    if e == "hex":
        return sig.hex()
    if e in {"b64", "base64"}:
        return base64.b64encode(sig).decode("ascii")
    raise ValueError("unsupported encoding")


def decode_signature(sig: str, *, encoding: str) -> bytes:
    e = encoding.strip().lower()
    s = sig.strip()
    if not s:
        raise ValueError("empty signature")

    if e == "hex":
        try:
            return bytes.fromhex(s)
        except Exception as ex:
            raise ValueError("invalid hex signature") from ex

    if e in {"b64", "base64"}:
        try:
            pad = (-len(s)) % 4
            s_padded = s + ("=" * pad)
            return base64.b64decode(s_padded.encode("ascii"), validate=True)
        except Exception as ex:
            raise ValueError("invalid base64 signature") from ex

    raise ValueError("unsupported encoding")


def webhook_sign_one(
    payload: bytes,
    *,
    algo: str,
    secret: bytes,
    encoding: str = "hex",
    secret_source: Optional[str] = None,
    payload_source: Optional[str] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    enc = encoding.strip().lower()

    result: Dict[str, Any] = {
        "type": "webhook_sign",
        "generated_at": generated_at,
        "algo": _normalize_algo(algo),
        "encoding": enc,
        "payload": {"sha256": _payload_sha256(payload), "bytes": len(payload), "source": payload_source},
        "secret_source": secret_source,
        "signature": None,
        "status": {"ok": False, "warning": False, "error": None},
    }

    try:
        sig_b = hmac_sign(payload, secret=secret, algo=algo)
        result["signature"] = encode_signature(sig_b, encoding=enc)
        result["status"] = {"ok": True, "warning": False, "error": None}
        return result
    except Exception as e:
        result["status"] = {"ok": False, "warning": False, "error": f"{type(e).__name__}: {e}"}
        return result


def webhook_verify_one(
    payload: bytes,
    *,
    signature: str,
    algo: str,
    secret: bytes,
    encoding: str = "hex",
    secret_source: Optional[str] = None,
    payload_source: Optional[str] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    enc = encoding.strip().lower()

    result: Dict[str, Any] = {
        "type": "webhook_verify",
        "generated_at": generated_at,
        "algo": _normalize_algo(algo),
        "encoding": enc,
        "payload": {"sha256": _payload_sha256(payload), "bytes": len(payload), "source": payload_source},
        "secret_source": secret_source,
        "signature": {"provided": signature, "computed": None, "match": False},
        "status": {"ok": False, "warning": False, "error": None},
    }

    try:
        provided_b = decode_signature(signature, encoding=enc)
        computed_b = hmac_sign(payload, secret=secret, algo=algo)
        result["signature"]["computed"] = encode_signature(computed_b, encoding=enc)
        match = hmac.compare_digest(provided_b, computed_b)
        result["signature"]["match"] = match
        if match:
            result["status"] = {"ok": True, "warning": False, "error": None}
        else:
            result["status"] = {"ok": False, "warning": False, "error": "signature mismatch"}
        return result
    except Exception as e:
        result["status"] = {"ok": False, "warning": False, "error": f"{type(e).__name__}: {e}"}
        return result


def read_payload_file(path: Path) -> bytes:
    return path.read_bytes()
