from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PortScanResult:
    target: str
    open_ports: list[int]


def parse_ports(spec: str) -> list[int]:
    spec = spec.strip()
    if not spec:
        raise ValueError("ports spec is empty")

    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s.strip())
            end = int(end_s.strip())
            if start < 0 or end < 0 or start > 65535 or end > 65535:
                raise ValueError("port out of range")
            if end < start:
                raise ValueError("invalid port range")
            ports.update(range(start, end + 1))
        else:
            p = int(part)
            if p < 0 or p > 65535:
                raise ValueError("port out of range")
            ports.add(p)

    return sorted(ports)


async def _check_port(target: str, port: int, timeout: float) -> bool:
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except (asyncio.TimeoutError, OSError):
        return False


async def _worker(
    target: str,
    queue: "asyncio.Queue[int]",
    open_ports: list[int],
    timeout: float,
) -> None:
    while True:
        port = await queue.get()
        try:
            if port < 0:
                return
            if await _check_port(target, port, timeout):
                open_ports.append(port)
        finally:
            queue.task_done()


async def scan_ports(
    target: str,
    ports: Iterable[int],
    *,
    concurrency: int = 500,
    timeout: float = 0.5,
) -> PortScanResult:
    port_list = list(ports)
    open_ports: list[int] = []
    queue: asyncio.Queue[int] = asyncio.Queue()

    worker_count = max(1, min(int(concurrency), max(1, len(port_list))))
    workers = [asyncio.create_task(_worker(target, queue, open_ports, timeout)) for _ in range(worker_count)]

    for p in port_list:
        await queue.put(p)

    for _ in range(worker_count):
        await queue.put(-1)

    await queue.join()
    await asyncio.gather(*workers)

    open_ports.sort()
    return PortScanResult(target=target, open_ports=open_ports)


def scan_ports_sync(
    target: str,
    ports: Iterable[int],
    *,
    concurrency: int = 500,
    timeout: float = 0.5,
) -> PortScanResult:
    return asyncio.run(scan_ports(target, ports, concurrency=concurrency, timeout=timeout))


def result_to_json(result: PortScanResult) -> str:
    return json.dumps({"target": result.target, "open_ports": result.open_ports}, indent=2)
