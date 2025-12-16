from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from securezy.tools.headers import headers_check_batch, headers_check_one, parse_headers_targets_file
from securezy.tools.reporting import write_headers_report, write_headers_report_dir


class _HandlerAllGood(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Strict-Transport-Security", "max-age=31536000")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "geolocation=()")
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()

    def log_message(self, format, *args):
        _ = format
        _ = args


class _HandlerMissingCsp(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Strict-Transport-Security", "max-age=31536000")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "geolocation=()")
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()

    def log_message(self, format, *args):
        _ = format
        _ = args


class _HandlerHead405(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(405)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Strict-Transport-Security", "max-age=31536000")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "geolocation=()")
        self.end_headers()

    def log_message(self, format, *args):
        _ = format
        _ = args


def _run_server(handler_cls):
    server = HTTPServer(("127.0.0.1", 0), handler_cls)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def test_parse_headers_targets_file(tmp_path: Path) -> None:
    p = tmp_path / "urls.txt"
    p.write_text(
        """
# comment
example.com
http://localhost:1234

x.y.z  # trailing
""".lstrip(),
        encoding="utf-8",
    )
    assert parse_headers_targets_file(p) == ["example.com", "http://localhost:1234", "x.y.z"]


def test_headers_check_one_ok() -> None:
    s = _run_server(_HandlerAllGood)
    try:
        url = f"http://127.0.0.1:{s.server_address[1]}/"
        payload = headers_check_one(url, timeout=2.0, method="HEAD")
        assert payload["type"] == "headers_check"
        assert payload["status"]["ok"] is True
        assert payload["status"]["warning"] is False
        assert payload["status"]["error"] is None
        assert payload["missing"] == []
    finally:
        s.shutdown()
        s.server_close()


def test_headers_check_one_warning_missing() -> None:
    s = _run_server(_HandlerMissingCsp)
    try:
        url = f"http://127.0.0.1:{s.server_address[1]}/"
        payload = headers_check_one(url, timeout=2.0, method="HEAD")
        assert payload["status"]["warning"] is True
        assert "content-security-policy" in (payload["missing"] or [])
    finally:
        s.shutdown()
        s.server_close()


def test_headers_check_one_head_fallback_to_get() -> None:
    s = _run_server(_HandlerHead405)
    try:
        url = f"http://127.0.0.1:{s.server_address[1]}/"
        payload = headers_check_one(url, timeout=2.0, method="HEAD")
        target = payload.get("target") or {}
        assert target.get("method") == "GET"
        assert payload["status"]["ok"] is True
    finally:
        s.shutdown()
        s.server_close()


def test_headers_check_batch_summary() -> None:
    s1 = _run_server(_HandlerAllGood)
    s2 = _run_server(_HandlerMissingCsp)
    try:
        u1 = f"http://127.0.0.1:{s1.server_address[1]}/"
        u2 = f"http://127.0.0.1:{s2.server_address[1]}/"
        payload = headers_check_batch([u1, u2], timeout=2.0, method="HEAD")
        assert payload["type"] == "headers_check_batch"
        assert payload["summary"] == {"total": 2, "ok": 1, "warning": 1, "error": 0}
    finally:
        s1.shutdown()
        s1.server_close()
        s2.shutdown()
        s2.server_close()


def test_write_headers_report_json_md_csv_and_dir(tmp_path: Path) -> None:
    s = _run_server(_HandlerAllGood)
    try:
        url = f"http://127.0.0.1:{s.server_address[1]}/"
        payload = headers_check_one(url, timeout=2.0, method="HEAD")

        out_json = tmp_path / "r.json"
        write_headers_report(payload=payload, out_path=out_json, format="json", overwrite=False)
        assert out_json.exists()
        assert "headers_check" in out_json.read_text(encoding="utf-8")

        out_md = tmp_path / "r.md"
        write_headers_report(payload=payload, out_path=out_md, format="md", overwrite=False)
        assert out_md.exists()
        assert "Headers Check Report" in out_md.read_text(encoding="utf-8")

        out_csv = tmp_path / "r.csv"
        write_headers_report(payload=payload, out_path=out_csv, format="csv", overwrite=False)
        assert out_csv.exists()
        assert "url" in out_csv.read_text(encoding="utf-8")

        out_dir = tmp_path / "reports"
        written = write_headers_report_dir(payload=payload, out_dir=out_dir, formats=["json", "md", "csv"], overwrite=False)
        assert len(written) == 3
        assert any(p.suffix == ".json" for p in written)
        assert any(p.suffix == ".md" for p in written)
        assert any(p.suffix == ".csv" for p in written)

    finally:
        s.shutdown()
        s.server_close()
