from __future__ import annotations

import ipaddress
import socket
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _parse_asn1_time(value: str) -> datetime:
    v = " ".join(value.split())
    dt = datetime.strptime(v, "%b %d %H:%M:%S %Y %Z")
    return dt.replace(tzinfo=timezone.utc)


def _fmt_name(parts: Any) -> Optional[str]:
    if not parts:
        return None
    out: List[str] = []
    for rdn in parts:
        for k, v in rdn:
            out.append(f"{k}={v}")
    return ",".join(out) if out else None


def tls_check_one(
    host: str,
    port: int = 443,
    *,
    timeout: float = 3.0,
    servername: Optional[str] = None,
    verify: bool = True,
    ca_file: Optional[str] = None,
    warn_days: int = 30,
    min_tls: Optional[str] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    target_servername = servername or (host if not _is_ip(host) else None)

    result: Dict[str, Any] = {
        "type": "tls_check",
        "generated_at": generated_at,
        "target": {"host": host, "port": int(port), "servername": target_servername},
        "verification": {"verify": bool(verify), "ca_file": ca_file},
        "certificate": None,
        "connection": None,
        "status": {"ok": False, "warning": False, "error": None},
    }

    try:
        if verify:
            ctx = ssl.create_default_context()
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.check_hostname = target_servername is not None
            if ca_file:
                ctx.load_verify_locations(cafile=ca_file)
        else:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        if min_tls is not None:
            v = min_tls.strip().lower()
            if v in {"1.2", "tls1.2", "tls1_2"}:
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            elif v in {"1.3", "tls1.3", "tls1_3"}:
                ctx.minimum_version = ssl.TLSVersion.TLSv1_3
            else:
                raise ValueError("unsupported min tls")

        with socket.create_connection((host, int(port)), timeout=timeout) as sock:
            peer_ip = sock.getpeername()[0]
            with ctx.wrap_socket(sock, server_hostname=target_servername) as ssock:
                cert = ssock.getpeercert() or {}
                nb_raw = cert.get("notBefore")
                na_raw = cert.get("notAfter")

                nb = _parse_asn1_time(nb_raw) if nb_raw else None
                na = _parse_asn1_time(na_raw) if na_raw else None

                days_to_expiry: Optional[int] = None
                ok = True
                warning = False
                if na is not None:
                    delta = na - datetime.now(timezone.utc)
                    days_to_expiry = int(delta.total_seconds() // 86400)
                    ok = days_to_expiry >= 0
                    warning = days_to_expiry <= int(warn_days)

                sans: List[str] = []
                for typ, val in cert.get("subjectAltName", []) or []:
                    if typ in {"DNS", "IP Address"}:
                        sans.append(val)

                result["certificate"] = {
                    "subject": _fmt_name(cert.get("subject")),
                    "issuer": _fmt_name(cert.get("issuer")),
                    "sans": sans,
                    "not_before": nb.isoformat() if nb else None,
                    "not_after": na.isoformat() if na else None,
                    "days_to_expiry": days_to_expiry,
                    "serial_number": None,
                    "signature_algorithm": None,
                }
                result["connection"] = {
                    "tls_version": ssock.version(),
                    "cipher": ssock.cipher(),
                    "peer_ip": peer_ip,
                }
                result["status"] = {"ok": ok, "warning": warning, "error": None}
                return result

    except Exception as e:
        result["status"] = {"ok": False, "warning": False, "error": f"{type(e).__name__}: {e}"}
        return result


def _parse_host_port(value: str) -> tuple[str, Optional[int]]:
    s = value.strip()
    if not s:
        raise ValueError("empty host")

    if s.startswith("[") and "]" in s:
        host = s[1 : s.index("]")]
        rest = s[s.index("]") + 1 :]
        if rest.startswith(":"):
            return host, int(rest[1:])
        return host, None

    if s.count(":") == 1:
        host_s, port_s = s.split(":", 1)
        return host_s.strip(), int(port_s.strip())

    return s, None


def parse_tls_targets_file(path: Path) -> List[Dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    targets: List[Dict[str, Any]] = []
    for line in lines:
        raw = line.split("#", 1)[0].strip()
        if not raw:
            continue

        if "," in raw:
            hostport, sni = [x.strip() for x in raw.split(",", 1)]
        else:
            hostport, sni = raw, None

        host, port = _parse_host_port(hostport)
        targets.append({"host": host, "port": port, "servername": sni})

    return targets


def tls_check_batch(
    targets: List[Dict[str, Any]],
    *,
    default_port: int = 443,
    timeout: float = 3.0,
    verify: bool = True,
    ca_file: Optional[str] = None,
    warn_days: int = 30,
    min_tls: Optional[str] = None,
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()

    results: List[Dict[str, Any]] = []
    for t in targets:
        host = str(t["host"])
        port = int(t.get("port") or default_port)
        servername = t.get("servername")
        results.append(
            tls_check_one(
                host,
                port,
                timeout=timeout,
                servername=str(servername) if servername else None,
                verify=verify,
                ca_file=ca_file,
                warn_days=warn_days,
                min_tls=min_tls,
            )
        )

    ok_n = sum(1 for r in results if r["status"]["ok"] and not r["status"]["warning"])
    warn_n = sum(1 for r in results if r["status"]["warning"])
    err_n = sum(1 for r in results if r["status"]["error"] is not None)

    return {
        "type": "tls_check_batch",
        "generated_at": generated_at,
        "warn_days": int(warn_days),
        "summary": {"total": len(results), "ok": ok_n, "warning": warn_n, "error": err_n},
        "results": results,
    }


def tls_exit_code(payload: Dict[str, Any]) -> int:
    t = payload.get("type")
    if t == "tls_check_batch":
        summary = payload.get("summary") or {}
        if int(summary.get("error", 0)) > 0:
            return 2
        if int(summary.get("warning", 0)) > 0:
            return 1
        return 0

    status = payload.get("status") or {}
    if status.get("error") is not None:
        return 2
    if status.get("warning"):
        return 1
    return 0
