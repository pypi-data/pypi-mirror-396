from __future__ import annotations

import re
from pathlib import Path

import pytest

from securezy.tools.pwgen import generate_one, pwgen_payload
from securezy.tools.reporting import write_pwgen_report, write_pwgen_report_dir


def test_generate_site_default_len() -> None:
    v = generate_one(preset="site")
    assert isinstance(v, str)
    assert len(v) == 24


def test_generate_site_no_ambiguous() -> None:
    v = generate_one(preset="site", length=256, no_ambiguous=True)
    assert not any(c in v for c in "O0Il1")


def test_generate_hex_bytes() -> None:
    v = generate_one(preset="hex", nbytes=4)
    assert re.fullmatch(r"[0-9a-f]+", v) is not None
    assert len(v) == 8


def test_generate_base64url_bytes() -> None:
    v = generate_one(preset="base64url", nbytes=8)
    assert isinstance(v, str)
    assert len(v) > 0


def test_pwgen_payload_single_has_status() -> None:
    payload = pwgen_payload(preset="site", length=12, nbytes=None, count=1, no_ambiguous=False)
    assert payload["type"] == "pwgen"
    assert payload["status"] == {"ok": True, "warning": False, "error": None}
    assert len(payload["value"]) == 12


def test_pwgen_payload_batch_summary() -> None:
    payload = pwgen_payload(preset="hex", length=None, nbytes=2, count=3, no_ambiguous=False)
    assert payload["type"] == "pwgen_batch"
    assert payload["summary"] == {"total": 3, "ok": 3, "warning": 0, "error": 0}
    assert len(payload["results"]) == 3


def test_pwgen_invalid_preset() -> None:
    with pytest.raises(ValueError):
        generate_one(preset="bad")


def test_write_pwgen_report_json_md_csv_and_dir(tmp_path: Path) -> None:
    payload = pwgen_payload(preset="site", length=8, nbytes=None, count=1, no_ambiguous=True)

    out_json = tmp_path / "r.json"
    write_pwgen_report(payload=payload, out_path=out_json, format="json", overwrite=False)
    assert out_json.exists()
    assert "pwgen" in out_json.read_text(encoding="utf-8")

    out_md = tmp_path / "r.md"
    write_pwgen_report(payload=payload, out_path=out_md, format="md", overwrite=False)
    assert out_md.exists()
    assert "Password Generator Report" in out_md.read_text(encoding="utf-8")

    out_csv = tmp_path / "r.csv"
    write_pwgen_report(payload=payload, out_path=out_csv, format="csv", overwrite=False)
    assert out_csv.exists()
    assert "value" in out_csv.read_text(encoding="utf-8")

    out_dir = tmp_path / "reports"
    written = write_pwgen_report_dir(payload=payload, out_dir=out_dir, formats=["json", "md", "csv"], overwrite=False)
    assert len(written) == 3
    assert any(p.suffix == ".json" for p in written)
    assert any(p.suffix == ".md" for p in written)
    assert any(p.suffix == ".csv" for p in written)
