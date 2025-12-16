import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from securezy.tools.jwt import jwt_inspect_batch, jwt_inspect_one, parse_jwt_tokens_file
from securezy.tools.reporting import write_jwt_report, write_jwt_report_dir


def _b64url_json(obj: dict) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _jwt(header: dict, payload: dict) -> str:
    h = _b64url_json(header)
    p = _b64url_json(payload)
    return f"{h}.{p}.sig"


def test_parse_jwt_tokens_file_ignores_comments_and_blank(tmp_path: Path) -> None:
    p = tmp_path / "tokens.txt"
    p.write_text(
        """
# comment
abc.def.ghi

x.y.z  # trailing
""".lstrip(),
        encoding="utf-8",
    )
    assert parse_jwt_tokens_file(p) == ["abc.def.ghi", "x.y.z"]


def test_jwt_inspect_warns_alg_none_and_missing_exp() -> None:
    tok = _jwt({"alg": "none", "typ": "JWT"}, {"sub": "u"})
    r = jwt_inspect_one(tok, skew_seconds=0)
    assert r["type"] == "jwt_inspect"
    assert r["status"]["warning"] is True
    assert r["status"]["error"] is None
    assert "alg=none" in r["status"]["messages"]
    assert any("exp" in m for m in r["status"]["messages"])


def test_jwt_inspect_expired() -> None:
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    tok = _jwt({"alg": "HS256"}, {"sub": "u", "exp": int(now.timestamp()) - 10})
    r = jwt_inspect_one(tok, now=now, skew_seconds=0)
    assert r["status"]["warning"] is True
    assert "token is expired" in r["status"]["messages"]


def test_jwt_inspect_nbf_future_with_skew() -> None:
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    tok = _jwt({"alg": "HS256"}, {"sub": "u", "exp": int(now.timestamp()) + 3600, "nbf": int(now.timestamp()) + 61})
    r = jwt_inspect_one(tok, now=now, skew_seconds=60)
    assert r["status"]["warning"] is True
    assert "nbf is in the future" in r["status"]["messages"]


def test_jwt_inspect_batch_summary_counts() -> None:
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    ok_tok = _jwt({"alg": "HS256"}, {"sub": "u", "exp": int(now.timestamp()) + 3600})
    warn_tok = _jwt({"alg": "none"}, {"sub": "u", "exp": int(now.timestamp()) + 3600})
    payload = jwt_inspect_batch([ok_tok, warn_tok], now=now, skew_seconds=0)
    assert payload["type"] == "jwt_inspect_batch"
    assert payload["summary"] == {"total": 2, "ok": 1, "warning": 1, "error": 0}


def test_write_jwt_report_json_md_csv_and_dir(tmp_path: Path) -> None:
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    tok = _jwt({"alg": "HS256", "kid": "k"}, {"sub": "u", "iss": "i", "exp": int(now.timestamp()) + 3600})
    payload = jwt_inspect_one(tok, now=now, skew_seconds=0)

    out_json = tmp_path / "r.json"
    write_jwt_report(payload=payload, out_path=out_json, format="json", overwrite=False)
    assert out_json.exists()
    assert "jwt_inspect" in out_json.read_text(encoding="utf-8")

    out_md = tmp_path / "r.md"
    write_jwt_report(payload=payload, out_path=out_md, format="md", overwrite=False)
    assert out_md.exists()
    assert "JWT Inspect Report" in out_md.read_text(encoding="utf-8")

    out_csv = tmp_path / "r.csv"
    write_jwt_report(payload=payload, out_path=out_csv, format="csv", overwrite=False)
    assert out_csv.exists()
    assert "alg" in out_csv.read_text(encoding="utf-8")

    out_dir = tmp_path / "reports"
    written = write_jwt_report_dir(payload=payload, out_dir=out_dir, formats=["json", "md", "csv"], overwrite=False)
    assert len(written) == 3
    assert any(p.suffix == ".json" for p in written)
    assert any(p.suffix == ".md" for p in written)
    assert any(p.suffix == ".csv" for p in written)
