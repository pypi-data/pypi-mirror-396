from pathlib import Path

import pytest

from securezy.tools.output import emit, exit_code, parse_formats_csv


def _write_report(*, payload, out_path: Path, format: str, overwrite: bool = False) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))
    out_path.write_text(f"{format}:{payload.get('type')}", encoding="utf-8")


def _write_report_dir(*, payload, out_dir: Path, formats: list[str], overwrite: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in formats:
        p = out_dir / f"r.{fmt}"
        _write_report(payload=payload, out_path=p, format=fmt, overwrite=overwrite)
        written.append(p)
    return written


def test_parse_formats_csv_trims() -> None:
    assert parse_formats_csv("json, md ,csv") == ["json", "md", "csv"]


def test_exit_code_single_ok() -> None:
    payload = {"type": "x", "status": {"ok": True, "warning": False, "error": None}}
    assert exit_code(payload) == 0


def test_exit_code_single_warning() -> None:
    payload = {"type": "x", "status": {"ok": False, "warning": True, "error": None}}
    assert exit_code(payload) == 1


def test_exit_code_single_error() -> None:
    payload = {"type": "x", "status": {"ok": False, "warning": False, "error": "boom"}}
    assert exit_code(payload) == 2


def test_exit_code_batch_summary() -> None:
    payload = {"type": "something_batch", "summary": {"total": 2, "ok": 1, "warning": 1, "error": 0}}
    assert exit_code(payload) == 1


def test_emit_writes_report_and_dir(tmp_path: Path) -> None:
    payload = {"type": "unit"}
    out = tmp_path / "out.json"
    out_dir = tmp_path / "dir"
    written = emit(
        payload,
        json_stdout=False,
        report=out,
        report_dir=out_dir,
        report_format="json",
        report_formats=["json", "md"],
        overwrite=False,
        write_report=_write_report,
        write_report_dir=_write_report_dir,
    )
    assert out in written
    assert out.exists()
    assert (out_dir / "r.json").exists()
    assert (out_dir / "r.md").exists()


def test_emit_no_overwrite(tmp_path: Path) -> None:
    payload = {"type": "unit"}
    out = tmp_path / "out.json"
    out.write_text("exists", encoding="utf-8")

    with pytest.raises(FileExistsError):
        emit(
            payload,
            json_stdout=True,
            report=out,
            report_dir=None,
            report_format="json",
            report_formats=["json"],
            overwrite=False,
            write_report=_write_report,
            write_report_dir=_write_report_dir,
        )
