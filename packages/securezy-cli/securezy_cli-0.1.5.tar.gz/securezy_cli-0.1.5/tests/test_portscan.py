import socket

from securezy.tools.portscan import parse_ports, scan_ports_sync


def test_parse_ports_range_and_list() -> None:
    assert parse_ports("1-3") == [1, 2, 3]
    assert parse_ports("1-3,5,7") == [1, 2, 3, 5, 7]


def test_scan_ports_finds_open_local_port() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    try:
        port = s.getsockname()[1]
        result = scan_ports_sync("127.0.0.1", [port], concurrency=50, timeout=1.0)
        assert port in result.open_ports
    finally:
        s.close()
