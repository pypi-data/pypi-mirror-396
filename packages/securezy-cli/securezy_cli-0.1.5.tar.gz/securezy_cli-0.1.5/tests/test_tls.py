from pathlib import Path

from securezy.tools.reporting import write_tls_report, write_tls_report_dir
from securezy.tools.tls import parse_tls_targets_file, tls_exit_code


def test_parse_tls_targets_file_supports_port_and_sni(tmp_path: Path) -> None:
    p = tmp_path / "targets.txt"
    p.write_text(
        """
# comment
example.com
example.com:8443
example.com:443,api.example.com

""".lstrip(),
        encoding="utf-8",
    )

    targets = parse_tls_targets_file(p)
    assert targets == [
        {"host": "example.com", "port": None, "servername": None},
        {"host": "example.com", "port": 8443, "servername": None},
        {"host": "example.com", "port": 443, "servername": "api.example.com"},
    ]


def test_tls_exit_code_single() -> None:
    assert (
        tls_exit_code(
            {
                "type": "tls_check",
                "status": {"ok": True, "warning": False, "error": None},
            }
        )
        == 0
    )
    assert (
        tls_exit_code(
            {
                "type": "tls_check",
                "status": {"ok": True, "warning": True, "error": None},
            }
        )
        == 1
    )
    assert (
        tls_exit_code(
            {
                "type": "tls_check",
                "status": {"ok": False, "warning": False, "error": "x"},
            }
        )
        == 2
    )


def test_tls_exit_code_batch() -> None:
    assert (
        tls_exit_code(
            {
                "type": "tls_check_batch",
                "summary": {"total": 2, "ok": 2, "warning": 0, "error": 0},
            }
        )
        == 0
    )
    assert (
        tls_exit_code(
            {
                "type": "tls_check_batch",
                "summary": {"total": 2, "ok": 1, "warning": 1, "error": 0},
            }
        )
        == 1
    )
    assert (
        tls_exit_code(
            {
                "type": "tls_check_batch",
                "summary": {"total": 2, "ok": 1, "warning": 0, "error": 1},
            }
        )
        == 2
    )


def _sample_tls_single_payload() -> dict:
    return {
        "type": "tls_check",
        "generated_at": "2025-12-13T10:00:00+00:00",
        "target": {"host": "example.com", "port": 443, "servername": "example.com"},
        "verification": {"verify": True, "ca_file": None},
        "certificate": {
            "subject": "CN=example.com",
            "issuer": "CN=R3",
            "sans": ["example.com"],
            "not_before": "2025-01-01T00:00:00+00:00",
            "not_after": "2026-01-01T00:00:00+00:00",
            "days_to_expiry": 123,
            "serial_number": None,
            "signature_algorithm": None,
        },
        "connection": {
            "tls_version": "TLSv1.3",
            "cipher": ["TLS_AES_128_GCM_SHA256", "TLSv1.3", 128],
            "peer_ip": "93.184.216.34",
        },
        "status": {"ok": True, "warning": False, "error": None},
    }


def test_write_tls_report_json_md_csv(tmp_path: Path) -> None:
    payload = _sample_tls_single_payload()

    out_json = tmp_path / "r.json"
    write_tls_report(payload=payload, out_path=out_json, format="json", overwrite=False)
    assert out_json.exists()
    assert "tls_check" in out_json.read_text(encoding="utf-8")

    out_md = tmp_path / "r.md"
    write_tls_report(payload=payload, out_path=out_md, format="md", overwrite=False)
    assert out_md.exists()
    assert "TLS Check Report" in out_md.read_text(encoding="utf-8")

    out_csv = tmp_path / "r.csv"
    write_tls_report(payload=payload, out_path=out_csv, format="csv", overwrite=False)
    assert out_csv.exists()
    assert "host" in out_csv.read_text(encoding="utf-8")


def test_write_tls_report_dir(tmp_path: Path) -> None:
    payload = {
        "type": "tls_check_batch",
        "generated_at": "2025-12-13T10:00:00+00:00",
        "warn_days": 30,
        "summary": {"total": 2, "ok": 1, "warning": 0, "error": 1},
        "results": [
            _sample_tls_single_payload(),
            {
                "type": "tls_check",
                "generated_at": "2025-12-13T10:00:00+00:00",
                "target": {"host": "bad.example", "port": 443, "servername": "bad.example"},
                "verification": {"verify": True, "ca_file": None},
                "certificate": None,
                "connection": None,
                "status": {"ok": False, "warning": False, "error": "TimeoutError"},
            },
        ],
    }

    out_dir = tmp_path / "reports"
    written = write_tls_report_dir(payload=payload, out_dir=out_dir, formats=["json", "md", "csv"], overwrite=False)
    assert len(written) == 3
    assert any(p.suffix == ".json" for p in written)
    assert any(p.suffix == ".md" for p in written)
    assert any(p.suffix == ".csv" for p in written)
