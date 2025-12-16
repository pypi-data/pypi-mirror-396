from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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
