from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .portscan import PortScanResult


def _build_portscan_payload(
    *,
    result: PortScanResult,
    scanned_ports: List[int],
    concurrency: int,
    timeout: float,
) -> Dict[str, Any]:
    return {
        "type": "portscan",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": result.target,
        "scanned_ports": scanned_ports,
        "open_ports": result.open_ports,
        "parameters": {"concurrency": concurrency, "timeout": timeout},
    }


def render_portscan_markdown(payload: Dict[str, Any]) -> str:
    target = payload["target"]
    open_ports = payload["open_ports"]
    scanned_ports = payload["scanned_ports"]
    params = payload["parameters"]

    lines = []
    lines.append("# Port Scan Report")
    lines.append("")
    lines.append(f"Target: `{target}`")
    lines.append("")
    lines.append(f"Scanned ports: `{len(scanned_ports)}`")
    lines.append(f"Open ports: `{len(open_ports)}`")
    lines.append("")
    lines.append(f"Concurrency: `{params['concurrency']}`")
    lines.append(f"Timeout: `{params['timeout']}`")
    lines.append("")

    lines.append("## Open Ports")
    lines.append("")
    lines.append("| Port |")
    lines.append("| ---: |")
    for p in open_ports:
        lines.append(f"| {p} |")

    lines.append("")
    return "\n".join(lines)


def write_portscan_report(
    *,
    result: PortScanResult,
    scanned_ports: List[int],
    concurrency: int,
    timeout: float,
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    payload = _build_portscan_payload(
        result=result, scanned_ports=scanned_ports, concurrency=concurrency, timeout=timeout
    )

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_portscan_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["port", "status"])
            open_set = set(payload["open_ports"])
            for p in payload["scanned_ports"]:
                w.writerow([p, "open" if p in open_set else "closed"])
        return

    raise ValueError("unsupported format")


def write_portscan_report_dir(
    *,
    result: PortScanResult,
    scanned_ports: List[int],
    concurrency: int,
    timeout: float,
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_target = "".join(c if (c.isalnum() or c in "._-") else "_" for c in result.target)
    base = f"portscan-{safe_target}-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_portscan_report(
            result=result,
            scanned_ports=scanned_ports,
            concurrency=concurrency,
            timeout=timeout,
            out_path=out_path,
            format=f,
            overwrite=overwrite,
        )
        written.append(out_path)

    return written


def _tls_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = payload.get("type")
    if t == "tls_check_batch":
        results = payload.get("results") or []
        if isinstance(results, list):
            return [r for r in results if isinstance(r, dict)]
        return []

    if t == "tls_check":
        return [payload]

    raise ValueError("unsupported payload")


def render_tls_markdown(payload: Dict[str, Any]) -> str:
    t = payload.get("type")
    lines: List[str] = []
    lines.append("# TLS Check Report")
    lines.append("")
    lines.append(f"Generated at: `{payload.get('generated_at')}`")
    lines.append("")

    if t == "tls_check_batch":
        summary = payload.get("summary") or {}
        lines.append(
            f"Summary: total={summary.get('total')} ok={summary.get('ok')} warning={summary.get('warning')} error={summary.get('error')}"
        )
        lines.append("")

    rows = _tls_rows(payload)
    lines.append("| Host | Port | SNI | Days to expiry | Not after | TLS | OK | Warning | Error |")
    lines.append("| --- | ---: | --- | ---: | --- | --- | --- | --- | --- |")
    for r in rows:
        target = r.get("target") or {}
        cert = r.get("certificate") or {}
        conn = r.get("connection") or {}
        status = r.get("status") or {}
        host = target.get("host")
        port = target.get("port")
        sni = target.get("servername")
        dte = cert.get("days_to_expiry")
        na = cert.get("not_after")
        tls = conn.get("tls_version")
        ok = status.get("ok")
        warning = status.get("warning")
        err = status.get("error")
        lines.append(
            f"| {host} | {port} | {sni or ''} | {'' if dte is None else dte} | {na or ''} | {tls or ''} | {ok} | {warning} | {err or ''} |"
        )

    lines.append("")
    return "\n".join(lines)


def write_tls_report(
    *,
    payload: Dict[str, Any],
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_tls_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        rows = _tls_rows(payload)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "host",
                    "port",
                    "servername",
                    "days_to_expiry",
                    "not_after",
                    "issuer",
                    "subject",
                    "tls_version",
                    "cipher",
                    "peer_ip",
                    "ok",
                    "warning",
                    "error",
                ]
            )
            for r in rows:
                target = r.get("target") or {}
                cert = r.get("certificate") or {}
                conn = r.get("connection") or {}
                status = r.get("status") or {}
                cipher = conn.get("cipher")
                w.writerow(
                    [
                        target.get("host"),
                        target.get("port"),
                        target.get("servername"),
                        cert.get("days_to_expiry"),
                        cert.get("not_after"),
                        cert.get("issuer"),
                        cert.get("subject"),
                        conn.get("tls_version"),
                        json.dumps(cipher) if cipher is not None else "",
                        conn.get("peer_ip"),
                        status.get("ok"),
                        status.get("warning"),
                        status.get("error"),
                    ]
                )
        return

    raise ValueError("unsupported format")


def write_tls_report_dir(
    *,
    payload: Dict[str, Any],
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
    base_name: Optional[str] = None,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = base_name
    if not base:
        base = "tls"
        if payload.get("type") == "tls_check":
            t = payload.get("target") or {}
            host = t.get("host") or "target"
            safe_host = "".join(c if (c.isalnum() or c in "._-") else "_" for c in str(host))
            base = f"tls-{safe_host}-{ts}"
        else:
            base = f"tls-batch-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_tls_report(payload=payload, out_path=out_path, format=f, overwrite=overwrite)
        written.append(out_path)

    return written


def _jwt_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = payload.get("type")
    if t == "jwt_inspect_batch":
        results = payload.get("results") or []
        if isinstance(results, list):
            return [r for r in results if isinstance(r, dict)]
        return []

    if t == "jwt_inspect":
        return [payload]

    raise ValueError("unsupported payload")


def render_jwt_markdown(payload: Dict[str, Any]) -> str:
    t = payload.get("type")
    lines: List[str] = []
    lines.append("# JWT Inspect Report")
    lines.append("")
    lines.append(f"Generated at: `{payload.get('generated_at')}`")
    lines.append("")

    if t == "jwt_inspect_batch":
        summary = payload.get("summary") or {}
        lines.append(
            f"Summary: total={summary.get('total')} ok={summary.get('ok')} warning={summary.get('warning')} error={summary.get('error')}"
        )
        lines.append("")

    rows = _jwt_rows(payload)
    lines.append("| Alg | Kid | Iss | Aud | Sub | Exp | Nbf | Iat | OK | Warning | Error | Messages |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        claims = r.get("claims") or {}
        status = r.get("status") or {}
        msgs = status.get("messages") or []
        lines.append(
            "| {alg} | {kid} | {iss} | {aud} | {sub} | {exp} | {nbf} | {iat} | {ok} | {warning} | {error} | {messages} |".format(
                alg=claims.get("alg") or "",
                kid=claims.get("kid") or "",
                iss=claims.get("iss") or "",
                aud=claims.get("aud") or "",
                sub=claims.get("sub") or "",
                exp=claims.get("exp_iso") or "",
                nbf=claims.get("nbf_iso") or "",
                iat=claims.get("iat_iso") or "",
                ok=status.get("ok"),
                warning=status.get("warning"),
                error=status.get("error") or "",
                messages=json.dumps(msgs) if msgs else "",
            )
        )

    lines.append("")
    return "\n".join(lines)


def write_jwt_report(
    *,
    payload: Dict[str, Any],
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_jwt_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        rows = _jwt_rows(payload)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "alg",
                    "kid",
                    "iss",
                    "aud",
                    "sub",
                    "exp",
                    "nbf",
                    "iat",
                    "ok",
                    "warning",
                    "error",
                    "messages",
                ]
            )
            for r in rows:
                claims = r.get("claims") or {}
                status = r.get("status") or {}
                msgs = status.get("messages") or []
                w.writerow(
                    [
                        claims.get("alg"),
                        claims.get("kid"),
                        claims.get("iss"),
                        json.dumps(claims.get("aud")) if claims.get("aud") is not None else "",
                        claims.get("sub"),
                        claims.get("exp_iso"),
                        claims.get("nbf_iso"),
                        claims.get("iat_iso"),
                        status.get("ok"),
                        status.get("warning"),
                        status.get("error"),
                        json.dumps(msgs) if msgs else "",
                    ]
                )
        return

    raise ValueError("unsupported format")


def write_jwt_report_dir(
    *,
    payload: Dict[str, Any],
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
    base_name: Optional[str] = None,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = base_name
    if not base:
        base = f"jwt-{ts}" if payload.get("type") == "jwt_inspect" else f"jwt-batch-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_jwt_report(payload=payload, out_path=out_path, format=f, overwrite=overwrite)
        written.append(out_path)

    return written


def _webhook_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = payload.get("type")
    if t in {"webhook_sign", "webhook_verify"}:
        return [payload]
    raise ValueError("unsupported payload")


def render_webhook_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Webhook Report")
    lines.append("")
    lines.append(f"Generated at: `{payload.get('generated_at')}`")
    lines.append("")

    rows = _webhook_rows(payload)
    lines.append("| Type | Algo | Encoding | Payload SHA256 | Bytes | Secret Source | Provided | Computed | Match | OK | Error |")
    lines.append("| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        t = r.get("type")
        algo = r.get("algo")
        enc = r.get("encoding")
        ps = (r.get("payload") or {}).get("sha256")
        pb = (r.get("payload") or {}).get("bytes")
        src = r.get("secret_source")
        status = r.get("status") or {}
        if t == "webhook_sign":
            provided = ""
            computed = r.get("signature")
            match = ""
        else:
            sig = r.get("signature") or {}
            provided = sig.get("provided")
            computed = sig.get("computed")
            match = sig.get("match")
        lines.append(
            f"| {t} | {algo} | {enc} | {ps} | {pb} | {src or ''} | {provided or ''} | {computed or ''} | {match if match is not None else ''} | {status.get('ok')} | {status.get('error') or ''} |"
        )

    lines.append("")
    return "\n".join(lines)


def write_webhook_report(
    *,
    payload: Dict[str, Any],
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_webhook_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        rows = _webhook_rows(payload)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "type",
                    "algo",
                    "encoding",
                    "payload_sha256",
                    "payload_bytes",
                    "secret_source",
                    "signature_provided",
                    "signature_computed",
                    "match",
                    "ok",
                    "error",
                ]
            )
            for r in rows:
                t = r.get("type")
                p = r.get("payload") or {}
                status = r.get("status") or {}
                if t == "webhook_sign":
                    provided = ""
                    computed = r.get("signature") or ""
                    match = ""
                else:
                    sig = r.get("signature") or {}
                    provided = sig.get("provided") or ""
                    computed = sig.get("computed") or ""
                    match = sig.get("match")
                w.writerow(
                    [
                        t,
                        r.get("algo"),
                        r.get("encoding"),
                        p.get("sha256"),
                        p.get("bytes"),
                        r.get("secret_source") or "",
                        provided,
                        computed,
                        match if match is not None else "",
                        status.get("ok"),
                        status.get("error") or "",
                    ]
                )
        return

    raise ValueError("unsupported format")


def write_webhook_report_dir(
    *,
    payload: Dict[str, Any],
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
    base_name: Optional[str] = None,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = base_name
    if not base:
        t = payload.get("type")
        if t == "webhook_sign":
            base = f"webhook-sign-{ts}"
        elif t == "webhook_verify":
            base = f"webhook-verify-{ts}"
        else:
            base = f"webhook-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_webhook_report(payload=payload, out_path=out_path, format=f, overwrite=overwrite)
        written.append(out_path)

    return written


def _headers_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = payload.get("type")
    if t == "headers_check_batch":
        results = payload.get("results") or []
        if isinstance(results, list):
            return [r for r in results if isinstance(r, dict)]
        return []

    if t == "headers_check":
        return [payload]

    raise ValueError("unsupported payload")


def render_headers_markdown(payload: Dict[str, Any]) -> str:
    t = payload.get("type")
    lines: List[str] = []
    lines.append("# Headers Check Report")
    lines.append("")
    lines.append(f"Generated at: `{payload.get('generated_at')}`")
    lines.append("")

    if t == "headers_check_batch":
        summary = payload.get("summary") or {}
        lines.append(
            f"Summary: total={summary.get('total')} ok={summary.get('ok')} warning={summary.get('warning')} error={summary.get('error')}"
        )
        lines.append("")

    rows = _headers_rows(payload)
    lines.append("| URL | Final URL | HTTP | Method | Missing | OK | Warning | Error |")
    lines.append("| --- | --- | ---: | --- | --- | --- | --- | --- |")
    for r in rows:
        target = r.get("target") or {}
        resp = r.get("response") or {}
        status = r.get("status") or {}
        missing = r.get("missing") or []
        lines.append(
            "| {url} | {final} | {code} | {method} | {missing} | {ok} | {warning} | {error} |".format(
                url=target.get("url") or "",
                final=target.get("final_url") or "",
                code=resp.get("status") or "",
                method=target.get("method") or "",
                missing=", ".join(missing) if isinstance(missing, list) else "",
                ok=status.get("ok"),
                warning=status.get("warning"),
                error=status.get("error") or "",
            )
        )

    lines.append("")
    return "\n".join(lines)


def write_headers_report(
    *,
    payload: Dict[str, Any],
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_headers_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        rows = _headers_rows(payload)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "url",
                    "final_url",
                    "method",
                    "http_status",
                    "missing",
                    "ok",
                    "warning",
                    "error",
                ]
            )
            for r in rows:
                target = r.get("target") or {}
                resp = r.get("response") or {}
                status = r.get("status") or {}
                missing = r.get("missing") or []
                w.writerow(
                    [
                        target.get("url") or "",
                        target.get("final_url") or "",
                        target.get("method") or "",
                        resp.get("status") or "",
                        ",".join(missing) if isinstance(missing, list) else "",
                        status.get("ok"),
                        status.get("warning"),
                        status.get("error") or "",
                    ]
                )
        return

    raise ValueError("unsupported format")


def write_headers_report_dir(
    *,
    payload: Dict[str, Any],
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
    base_name: Optional[str] = None,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = base_name
    if not base:
        if payload.get("type") == "headers_check":
            target = payload.get("target") or {}
            url = target.get("url") or "target"
            safe = "".join(c if (c.isalnum() or c in "._-") else "_" for c in str(url))
            base = f"headers-{safe}-{ts}"
        else:
            base = f"headers-batch-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_headers_report(payload=payload, out_path=out_path, format=f, overwrite=overwrite)
        written.append(out_path)

    return written


def _pwgen_rows(payload: Dict[str, Any]) -> List[str]:
    t = payload.get("type")
    if t == "pwgen_batch":
        results = payload.get("results") or []
        if isinstance(results, list):
            return [str(x) for x in results]
        return []

    if t == "pwgen":
        v = payload.get("value")
        return [str(v)] if v is not None else []

    raise ValueError("unsupported payload")


def render_pwgen_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Password Generator Report")
    lines.append("")
    lines.append(f"Generated at: `{payload.get('generated_at')}`")
    lines.append("")

    if payload.get("type") == "pwgen_batch":
        summary = payload.get("summary") or {}
        lines.append(f"Summary: total={summary.get('total')}")
        lines.append("")

    lines.append("| Value |")
    lines.append("| --- |")
    for v in _pwgen_rows(payload):
        lines.append(f"| `{v}` |")
    lines.append("")
    return "\n".join(lines)


def write_pwgen_report(
    *,
    payload: Dict[str, Any],
    out_path: Path,
    format: str,
    overwrite: bool = False,
) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    fmt = format.lower()
    if fmt == "json":
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if fmt == "md" or fmt == "markdown":
        out_path.write_text(render_pwgen_markdown(payload), encoding="utf-8")
        return

    if fmt == "csv":
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["value"])
            for v in _pwgen_rows(payload):
                w.writerow([v])
        return

    raise ValueError("unsupported format")


def write_pwgen_report_dir(
    *,
    payload: Dict[str, Any],
    out_dir: Path,
    formats: List[str],
    overwrite: bool = False,
    base_name: Optional[str] = None,
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = base_name
    if not base:
        if payload.get("type") == "pwgen":
            preset = payload.get("preset") or "pwgen"
            base = f"pwgen-{preset}-{ts}"
        else:
            preset = payload.get("preset") or "pwgen"
            base = f"pwgen-batch-{preset}-{ts}"

    written: List[Path] = []
    for fmt in formats:
        f = fmt.strip().lower()
        if not f:
            continue
        ext = "md" if f == "markdown" else f
        out_path = out_dir / f"{base}.{ext}"
        write_pwgen_report(payload=payload, out_path=out_path, format=f, overwrite=overwrite)
        written.append(out_path)

    return written
