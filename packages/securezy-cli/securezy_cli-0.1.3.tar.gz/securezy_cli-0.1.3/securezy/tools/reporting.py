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
