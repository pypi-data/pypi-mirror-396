from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class PasswordAuditResult:
    found: bool
    checked_lines: int


def audit_password(
    *,
    password: str,
    wordlist_path: Path,
    encoding: str = "utf-8",
    case_insensitive: bool = False,
    max_lines: Optional[int] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> PasswordAuditResult:
    pw = password
    if case_insensitive:
        pw = pw.lower()

    total_bytes = wordlist_path.stat().st_size
    processed_bytes = 0
    checked = 0

    with wordlist_path.open("rb") as f:
        for line in f:
            processed_bytes += len(line)
            if on_progress is not None:
                on_progress(processed_bytes, total_bytes)

            candidate_b = line.rstrip(b"\r\n")
            if not candidate_b:
                continue

            checked += 1
            if max_lines is not None and checked > max_lines:
                break

            try:
                candidate = candidate_b.decode(encoding)
            except Exception:
                candidate = candidate_b.decode(encoding, errors="ignore")

            if case_insensitive:
                candidate = candidate.lower()

            if candidate == pw:
                return PasswordAuditResult(found=True, checked_lines=checked)

    return PasswordAuditResult(found=False, checked_lines=checked)
