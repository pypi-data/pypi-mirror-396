from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, build_opener


def _normalize_url(url: str) -> str:
    s = url.strip()
    if not s:
        raise ValueError("empty url")
    if "://" not in s:
        s = f"https://{s}"
    u = urlparse(s)
    if not u.scheme or not u.netloc:
        raise ValueError("invalid url")
    return s


def _fetch(url: str, *, method: str, timeout: float) -> Tuple[int, str, Dict[str, str]]:
    req = Request(url, method=method)
    opener = build_opener()
    with opener.open(req, timeout=timeout) as resp:
        code = int(getattr(resp, "status", resp.getcode()))
        final_url = resp.geturl()
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return code, final_url, headers


def _evaluate_headers(headers: Dict[str, str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    checks: List[Dict[str, Any]] = []
    missing: List[str] = []

    def add(name: str, ok: bool, message: Optional[str] = None) -> None:
        checks.append({"header": name, "ok": bool(ok), "message": message})

    def require(name: str, predicate=None, message_ok: Optional[str] = None, message_bad: Optional[str] = None) -> None:
        v = headers.get(name)
        if v is None:
            missing.append(name)
            add(name, False, "missing")
            return
        if predicate is None:
            add(name, True, message_ok)
            return
        ok = bool(predicate(v))
        add(name, ok, message_ok if ok else (message_bad or "invalid"))

    require("strict-transport-security", predicate=lambda v: "max-age" in v.lower())
    require("content-security-policy")
    require("x-frame-options", predicate=lambda v: v.strip().upper() in {"DENY", "SAMEORIGIN"})
    require("x-content-type-options", predicate=lambda v: v.strip().lower() == "nosniff")
    require("referrer-policy")
    require("permissions-policy")

    return checks, missing


def headers_check_one(
    url: str,
    *,
    timeout: float = 5.0,
    method: str = "HEAD",
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()

    result: Dict[str, Any] = {
        "type": "headers_check",
        "generated_at": generated_at,
        "target": {"url": None, "method": None, "final_url": None},
        "response": None,
        "checks": None,
        "missing": None,
        "status": {"ok": False, "warning": False, "error": None},
    }

    try:
        u = _normalize_url(url)
        m = method.strip().upper() if method else "HEAD"
        if m not in {"HEAD", "GET"}:
            raise ValueError("unsupported method")

        try:
            code, final_url, headers = _fetch(u, method=m, timeout=timeout)
            used_method = m
        except HTTPError as e:
            if m == "HEAD" and int(getattr(e, "code", 0)) in {405, 501}:
                code, final_url, headers = _fetch(u, method="GET", timeout=timeout)
                used_method = "GET"
            else:
                raise

        checks, missing = _evaluate_headers(headers)
        warning = len(missing) > 0 or any(not c.get("ok") and c.get("message") != "missing" for c in checks)

        result["target"] = {"url": u, "method": used_method, "final_url": final_url}
        result["response"] = {"status": code, "headers": headers}
        result["checks"] = checks
        result["missing"] = missing
        result["status"] = {"ok": not warning, "warning": warning, "error": None}
        return result

    except Exception as e:
        result["status"] = {"ok": False, "warning": False, "error": f"{type(e).__name__}: {e}"}
        return result


def parse_headers_targets_file(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: List[str] = []
    for line in lines:
        raw = line.split("#", 1)[0].strip()
        if not raw:
            continue
        out.append(raw)
    return out


def headers_check_batch(
    urls: List[str],
    *,
    timeout: float = 5.0,
    method: str = "HEAD",
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()

    results: List[Dict[str, Any]] = []
    for u in urls:
        results.append(headers_check_one(u, timeout=timeout, method=method))

    ok_n = sum(1 for r in results if r["status"]["ok"] and not r["status"]["warning"])
    warn_n = sum(1 for r in results if r["status"]["warning"])
    err_n = sum(1 for r in results if r["status"]["error"] is not None)

    return {
        "type": "headers_check_batch",
        "generated_at": generated_at,
        "method": method,
        "timeout": float(timeout),
        "summary": {"total": len(results), "ok": ok_n, "warning": warn_n, "error": err_n},
        "results": results,
    }
