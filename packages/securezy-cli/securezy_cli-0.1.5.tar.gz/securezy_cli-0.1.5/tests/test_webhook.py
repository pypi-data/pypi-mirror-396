import base64
import hashlib
import hmac
from pathlib import Path

from securezy.tools.reporting import write_webhook_report, write_webhook_report_dir
from securezy.tools.webhook import webhook_sign_one, webhook_verify_one


def test_webhook_sign_and_verify_hex() -> None:
    payload = b"The quick brown fox jumps over the lazy dog"
    secret = b"key"

    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    signed = webhook_sign_one(payload, algo="sha256", secret=secret, encoding="hex")
    assert signed["type"] == "webhook_sign"
    assert signed["status"]["ok"] is True
    assert signed["signature"] == expected

    verified = webhook_verify_one(payload, signature=expected, algo="sha256", secret=secret, encoding="hex")
    assert verified["type"] == "webhook_verify"
    assert verified["status"]["ok"] is True
    assert verified["signature"]["match"] is True


def test_webhook_verify_base64_accepts_missing_padding() -> None:
    payload = b"payload"
    secret = b"secret"

    sig_b = hmac.new(secret, payload, hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig_b).decode("ascii").rstrip("=")

    verified = webhook_verify_one(payload, signature=sig_b64, algo="sha256", secret=secret, encoding="base64")
    assert verified["status"]["ok"] is True
    assert verified["signature"]["match"] is True


def test_webhook_verify_mismatch_is_error() -> None:
    payload = b"payload"
    secret = b"secret"
    verified = webhook_verify_one(payload, signature="00" * 32, algo="sha256", secret=secret, encoding="hex")
    assert verified["status"]["ok"] is False
    assert verified["status"]["error"] is not None


def test_write_webhook_report_json_md_csv_and_dir(tmp_path: Path) -> None:
    payload = webhook_sign_one(b"payload", algo="sha256", secret=b"secret", encoding="hex")

    out_json = tmp_path / "r.json"
    write_webhook_report(payload=payload, out_path=out_json, format="json", overwrite=False)
    assert out_json.exists()
    assert "webhook_sign" in out_json.read_text(encoding="utf-8")

    out_md = tmp_path / "r.md"
    write_webhook_report(payload=payload, out_path=out_md, format="md", overwrite=False)
    assert out_md.exists()
    assert "Webhook Report" in out_md.read_text(encoding="utf-8")

    out_csv = tmp_path / "r.csv"
    write_webhook_report(payload=payload, out_path=out_csv, format="csv", overwrite=False)
    assert out_csv.exists()
    assert "type" in out_csv.read_text(encoding="utf-8")

    out_dir = tmp_path / "reports"
    written = write_webhook_report_dir(payload=payload, out_dir=out_dir, formats=["json", "md", "csv"], overwrite=False)
    assert len(written) == 3
    assert any(p.suffix == ".json" for p in written)
    assert any(p.suffix == ".md" for p in written)
    assert any(p.suffix == ".csv" for p in written)
