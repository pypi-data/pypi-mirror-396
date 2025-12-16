from pathlib import Path

from securezy.tools.portscan import PortScanResult
from securezy.tools.reporting import write_portscan_report, write_portscan_report_dir


def test_write_portscan_report_json(tmp_path: Path) -> None:
    out = tmp_path / "r.json"
    write_portscan_report(
        result=PortScanResult(target="127.0.0.1", open_ports=[80]),
        scanned_ports=[79, 80, 81],
        concurrency=100,
        timeout=0.5,
        out_path=out,
        format="json",
        overwrite=False,
    )
    assert out.exists()
    assert "open_ports" in out.read_text(encoding="utf-8")


def test_write_portscan_report_dir(tmp_path: Path) -> None:
    out_dir = tmp_path / "reports"
    written = write_portscan_report_dir(
        result=PortScanResult(target="127.0.0.1", open_ports=[80]),
        scanned_ports=[79, 80, 81],
        concurrency=100,
        timeout=0.5,
        out_dir=out_dir,
        formats=["json", "md", "csv"],
        overwrite=False,
    )
    assert len(written) == 3
    assert any(p.suffix == ".json" for p in written)
    assert any(p.suffix == ".md" for p in written)
    assert any(p.suffix == ".csv" for p in written)
