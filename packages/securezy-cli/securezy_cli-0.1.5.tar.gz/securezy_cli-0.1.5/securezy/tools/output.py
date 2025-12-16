from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def parse_formats_csv(value: str) -> List[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def exit_code(payload: Dict[str, Any]) -> int:
    t = payload.get("type")
    if isinstance(t, str) and t.endswith("_batch"):
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


WriteReportFn = Callable[..., None]
WriteReportDirFn = Callable[..., List[Path]]


def emit(
    payload: Dict[str, Any],
    *,
    json_stdout: bool,
    report: Optional[Path],
    report_dir: Optional[Path],
    report_format: str,
    report_formats: List[str],
    overwrite: bool,
    write_report: WriteReportFn,
    write_report_dir: WriteReportDirFn,
) -> List[Path]:
    written: List[Path] = []

    if report is not None:
        write_report(payload=payload, out_path=report, format=report_format, overwrite=overwrite)
        written.append(report)

    if report_dir is not None:
        written.extend(
            write_report_dir(payload=payload, out_dir=report_dir, formats=report_formats, overwrite=overwrite)
        )

    if json_stdout:
        return written

    return written
