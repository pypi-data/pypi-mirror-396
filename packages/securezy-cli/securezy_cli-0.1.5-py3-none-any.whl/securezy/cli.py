from __future__ import annotations

import json
import os
import sys
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from pathlib import Path

from .tools.portscan import parse_ports, result_to_json, scan_ports_sync
from .tools.jwt import jwt_inspect_batch, jwt_inspect_one, parse_jwt_tokens_file
from .tools.tls import parse_tls_targets_file, tls_check_batch, tls_check_one, tls_exit_code
from .tools.output import emit as emit_output, exit_code as audit_exit_code, parse_formats_csv
from .tools.webhook import read_payload_file, webhook_sign_one, webhook_verify_one
from .tools.headers import headers_check_batch, headers_check_one, parse_headers_targets_file
from .tools.pwgen import pwgen_payload
from .tools.vault import add_entry, get_entry, init_vault, list_services
from .tools.crypto import decrypt_file, encrypt_file
from .tools.hashing import hash_file, hash_text
from .tools.plugins import load_plugins
from .tools.plugin_scaffold import create_plugin_skeleton
from .tools.profiles import PortScanProfile, delete_profile, get_profile, list_profiles, profiles_file_path, set_profile
from .tools.reporting import (
    write_jwt_report,
    write_jwt_report_dir,
    write_headers_report,
    write_headers_report_dir,
    write_pwgen_report,
    write_pwgen_report_dir,
    write_portscan_report,
    write_portscan_report_dir,
    write_tls_report,
    write_tls_report_dir,
    write_webhook_report,
    write_webhook_report_dir,
)

app = typer.Typer(add_completion=True, no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)
scan_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(scan_app, name="scan")
tls_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(tls_app, name="tls")
jwt_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(jwt_app, name="jwt")
webhook_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(webhook_app, name="webhook")
headers_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(headers_app, name="headers")
vault_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(vault_app, name="vault")
crypto_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(crypto_app, name="crypto")
hash_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(hash_app, name="hash")
profiles_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(profiles_app, name="profiles")
plugins_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(plugins_app, name="plugins")


@scan_app.command("ports")
def scan_ports(
    target: Optional[str] = typer.Option(None, "--target", "-t"),
    ports: Optional[str] = typer.Option(None, "--ports", "-p"),
    concurrency: Optional[int] = typer.Option(None, "--concurrency", "-c", min=1, max=5000),
    timeout: Optional[float] = typer.Option(None, "--timeout", "--to", min=0.05, max=10.0),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
    profile: Optional[str] = typer.Option(None, "--profile"),
) -> None:
    if profile is not None:
        p = get_profile(profile)
        if target is None:
            target = p.target
        if ports is None:
            ports = p.ports
        if concurrency is None:
            concurrency = p.concurrency
        if timeout is None:
            timeout = p.timeout

    if target is None:
        raise typer.BadParameter("--target is required unless --profile provides it")
    if ports is None:
        ports = "1-1024"
    if concurrency is None:
        concurrency = 500
    if timeout is None:
        timeout = 0.5

    port_list = parse_ports(ports)
    result = scan_ports_sync(target, port_list, concurrency=concurrency, timeout=timeout)

    if report is not None:
        write_portscan_report(
            result=result,
            scanned_ports=port_list,
            concurrency=concurrency,
            timeout=timeout,
            out_path=report,
            format=report_format,
            overwrite=overwrite_report,
        )

    if report_dir is not None:
        written = write_portscan_report_dir(
            result=result,
            scanned_ports=port_list,
            concurrency=concurrency,
            timeout=timeout,
            out_dir=report_dir,
            formats=[x.strip() for x in report_formats.split(",")],
            overwrite=overwrite_report,
        )
        for p in written:
            err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(result_to_json(result))
        return

    table = Table(title=f"Open ports on {result.target}")
    table.add_column("Port", justify="right")
    for p in result.open_ports:
        table.add_row(str(p))
    console.print(table)
    console.print(f"Found {len(result.open_ports)} open ports")


@tls_app.command("check")
def tls_check(
    host: Optional[str] = typer.Argument(None),
    from_file: Optional[Path] = typer.Option(None, "--from-file", exists=True, dir_okay=False, readable=True),
    port: int = typer.Option(443, "--port", min=1, max=65535),
    timeout: float = typer.Option(3.0, "--timeout", min=0.05, max=30.0),
    servername: Optional[str] = typer.Option(None, "--servername"),
    warn_days: int = typer.Option(30, "--warn-days", min=0, max=3650),
    min_tls: Optional[str] = typer.Option(None, "--min-tls"),
    no_verify: bool = typer.Option(False, "--no-verify"),
    ca_file: Optional[Path] = typer.Option(None, "--ca-file", exists=True, dir_okay=False, readable=True),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    if (host is None) == (from_file is None):
        raise typer.BadParameter("Provide either <host> or --from-file")

    verify = not no_verify
    ca_file_s = str(ca_file) if ca_file is not None else None

    if from_file is not None:
        targets = parse_tls_targets_file(from_file)
        payload = tls_check_batch(
            targets,
            default_port=port,
            timeout=timeout,
            verify=verify,
            ca_file=ca_file_s,
            warn_days=warn_days,
            min_tls=min_tls,
        )
    else:
        if host is None:
            raise typer.BadParameter("<host> is required")
        payload = tls_check_one(
            host,
            port,
            timeout=timeout,
            servername=servername,
            verify=verify,
            ca_file=ca_file_s,
            warn_days=warn_days,
            min_tls=min_tls,
        )

    if report is not None:
        write_tls_report(payload=payload, out_path=report, format=report_format, overwrite=overwrite_report)

    if report_dir is not None:
        written = write_tls_report_dir(
            payload=payload,
            out_dir=report_dir,
            formats=[x.strip() for x in report_formats.split(",")],
            overwrite=overwrite_report,
        )
        for p in written:
            err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(tls_exit_code(payload))

    if not verify:
        console.print("Warning: TLS verification is disabled (--no-verify).")

    if payload.get("type") == "tls_check_batch":
        rows = payload.get("results") or []
    else:
        rows = [payload]

    table = Table(title="TLS Check")
    table.add_column("Host")
    table.add_column("Port", justify="right")
    table.add_column("SNI")
    table.add_column("Days", justify="right")
    table.add_column("Not After")
    table.add_column("TLS")
    table.add_column("Status")

    for r in rows:
        if not isinstance(r, dict):
            continue
        target = r.get("target") or {}
        cert = r.get("certificate") or {}
        conn = r.get("connection") or {}
        status = r.get("status") or {}
        host_s = str(target.get("host") or "")
        port_s = str(target.get("port") or "")
        sni_s = str(target.get("servername") or "")
        days = cert.get("days_to_expiry")
        not_after = cert.get("not_after") or ""
        tls_v = conn.get("tls_version") or ""
        err = status.get("error")
        if err is not None:
            st = "error"
        elif status.get("warning"):
            st = "warning"
        else:
            st = "ok" if status.get("ok") else "unknown"
        table.add_row(
            host_s,
            port_s,
            sni_s,
            "" if days is None else str(days),
            str(not_after),
            str(tls_v),
            st,
        )

    console.print(table)

    code = tls_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


@jwt_app.command("inspect")
def jwt_inspect(
    token: Optional[str] = typer.Argument(None),
    from_file: Optional[Path] = typer.Option(None, "--from-file", exists=True, dir_okay=False, readable=True),
    skew_seconds: int = typer.Option(60, "--skew-seconds", min=0, max=86400),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    if (token is None) == (from_file is None):
        raise typer.BadParameter("Provide either <token> or --from-file")

    if from_file is not None:
        tokens = parse_jwt_tokens_file(from_file)
        payload = jwt_inspect_batch(tokens, skew_seconds=skew_seconds)
    else:
        if token is None:
            raise typer.BadParameter("<token> is required")
        payload = jwt_inspect_one(token, skew_seconds=skew_seconds)

    written = emit_output(
        payload,
        json_stdout=as_json,
        report=report,
        report_dir=report_dir,
        report_format=report_format,
        report_formats=parse_formats_csv(report_formats),
        overwrite=overwrite_report,
        write_report=write_jwt_report,
        write_report_dir=write_jwt_report_dir,
    )
    for p in written:
        if p is not None:
            err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(audit_exit_code(payload))

    if payload.get("type") == "jwt_inspect_batch":
        rows = payload.get("results") or []
        summary = payload.get("summary") or {}
        console.print(
            f"Summary: total={summary.get('total')} ok={summary.get('ok')} warning={summary.get('warning')} error={summary.get('error')}"
        )
    else:
        rows = [payload]

    table = Table(title="JWT Inspect")
    table.add_column("Alg")
    table.add_column("Kid")
    table.add_column("Iss")
    table.add_column("Sub")
    table.add_column("Exp")
    table.add_column("Status")
    for r in rows:
        if not isinstance(r, dict):
            continue
        claims = r.get("claims") or {}
        status = r.get("status") or {}
        err = status.get("error")
        if err is not None:
            st = "error"
        elif status.get("warning"):
            st = "warning"
        else:
            st = "ok" if status.get("ok") else "unknown"
        table.add_row(
            str(claims.get("alg") or ""),
            str(claims.get("kid") or ""),
            str(claims.get("iss") or ""),
            str(claims.get("sub") or ""),
            str(claims.get("exp_iso") or ""),
            st,
        )
    console.print(table)

    code = audit_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


@app.command("pwgen")
def pwgen(
    preset: str = typer.Option("site", "--preset"),
    length: Optional[int] = typer.Option(None, "--len", min=1, max=4096),
    nbytes: Optional[int] = typer.Option(None, "--bytes", min=1, max=4096),
    count: int = typer.Option(1, "--count", min=1, max=10000),
    no_ambiguous: bool = typer.Option(False, "--no-ambiguous"),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    p = (preset or "").strip().lower()
    if p == "site":
        if nbytes is not None:
            raise typer.BadParameter("--bytes is only valid for --preset hex/base64url")
    else:
        if length is not None:
            raise typer.BadParameter("--len is only valid for --preset site")

    payload = pwgen_payload(
        preset=p,
        length=length,
        nbytes=nbytes,
        count=count,
        no_ambiguous=no_ambiguous,
    )

    written = emit_output(
        payload,
        json_stdout=as_json,
        report=report,
        report_dir=report_dir,
        report_format=report_format,
        report_formats=parse_formats_csv(report_formats),
        overwrite=overwrite_report,
        write_report=write_pwgen_report,
        write_report_dir=write_pwgen_report_dir,
    )
    for pth in written:
        err_console.print(f"Wrote: {pth}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(audit_exit_code(payload))

    if payload.get("type") == "pwgen_batch":
        summary = payload.get("summary") or {}
        console.print(f"Generated: {summary.get('total')}")
        for v in payload.get("results") or []:
            console.print(str(v))
    else:
        console.print(str(payload.get("value") or ""))

    code = audit_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


def _resolve_secret(spec: str) -> tuple[bytes, str]:
    s = spec.strip()
    if not s:
        raise typer.BadParameter("--secret is required")

    if s.startswith("env:"):
        name = s[4:].strip()
        if not name:
            raise typer.BadParameter("env: requires a variable name")
        v = os.getenv(name)
        if v is None:
            raise typer.BadParameter(f"environment variable not set: {name}")
        return v.encode("utf-8"), f"env:{name}"

    if s == "prompt":
        v = typer.prompt("Secret", hide_input=True)
        return v.encode("utf-8"), "prompt"

    if s.startswith("vault:"):
        name = s[6:].strip()
        if not name:
            raise typer.BadParameter("vault: requires a service name")
        entry = get_entry(name)
        return entry.password.encode("utf-8"), f"vault:{name}"

    return s.encode("utf-8"), "literal"


def _read_payload(file: Optional[Path], stdin: bool) -> tuple[bytes, str]:
    if file is None and not stdin:
        raise typer.BadParameter("Provide one of --file or --stdin")
    if file is not None and stdin:
        raise typer.BadParameter("Provide only one of --file or --stdin")

    if file is not None:
        return read_payload_file(file), str(file)
    return sys.stdin.buffer.read(), "stdin"


@webhook_app.command("sign")
def webhook_sign(
    file: Optional[Path] = typer.Option(None, "--file", exists=True, dir_okay=False, readable=True),
    stdin: bool = typer.Option(False, "--stdin"),
    algo: str = typer.Option("sha256", "--algo"),
    secret: str = typer.Option(..., "--secret"),
    encoding: str = typer.Option("hex", "--encoding"),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    payload_b, payload_source = _read_payload(file, stdin)
    secret_b, secret_source = _resolve_secret(secret)

    payload = webhook_sign_one(
        payload_b,
        algo=algo,
        secret=secret_b,
        encoding=encoding,
        secret_source=secret_source,
        payload_source=payload_source,
    )

    written = emit_output(
        payload,
        json_stdout=as_json,
        report=report,
        report_dir=report_dir,
        report_format=report_format,
        report_formats=parse_formats_csv(report_formats),
        overwrite=overwrite_report,
        write_report=write_webhook_report,
        write_report_dir=write_webhook_report_dir,
    )
    for p in written:
        err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(audit_exit_code(payload))

    table = Table(title="Webhook Sign")
    table.add_column("Algo")
    table.add_column("Encoding")
    table.add_column("Payload SHA256")
    table.add_column("Signature")
    p = payload.get("payload") or {}
    table.add_row(
        str(payload.get("algo") or ""),
        str(payload.get("encoding") or ""),
        str(p.get("sha256") or ""),
        str(payload.get("signature") or ""),
    )
    console.print(table)

    code = audit_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


@webhook_app.command("verify")
def webhook_verify(
    signature: str = typer.Option(..., "--sig"),
    file: Optional[Path] = typer.Option(None, "--file", exists=True, dir_okay=False, readable=True),
    stdin: bool = typer.Option(False, "--stdin"),
    algo: str = typer.Option("sha256", "--algo"),
    secret: str = typer.Option(..., "--secret"),
    encoding: str = typer.Option("hex", "--encoding"),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    payload_b, payload_source = _read_payload(file, stdin)
    secret_b, secret_source = _resolve_secret(secret)

    payload = webhook_verify_one(
        payload_b,
        signature=signature,
        algo=algo,
        secret=secret_b,
        encoding=encoding,
        secret_source=secret_source,
        payload_source=payload_source,
    )

    written = emit_output(
        payload,
        json_stdout=as_json,
        report=report,
        report_dir=report_dir,
        report_format=report_format,
        report_formats=parse_formats_csv(report_formats),
        overwrite=overwrite_report,
        write_report=write_webhook_report,
        write_report_dir=write_webhook_report_dir,
    )
    for p in written:
        err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(audit_exit_code(payload))

    sig = payload.get("signature") or {}
    table = Table(title="Webhook Verify")
    table.add_column("Algo")
    table.add_column("Encoding")
    table.add_column("Payload SHA256")
    table.add_column("Match")
    table.add_column("Status")
    p = payload.get("payload") or {}
    status = payload.get("status") or {}
    err = status.get("error")
    if err is not None:
        st = "error"
    else:
        st = "ok" if status.get("ok") else "unknown"
    table.add_row(
        str(payload.get("algo") or ""),
        str(payload.get("encoding") or ""),
        str(p.get("sha256") or ""),
        str(sig.get("match")),
        st,
    )
    console.print(table)

    code = audit_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


@headers_app.command("check")
def headers_check(
    url: Optional[str] = typer.Argument(None),
    from_file: Optional[Path] = typer.Option(None, "--from-file", exists=True, dir_okay=False, readable=True),
    timeout: float = typer.Option(5.0, "--timeout", min=0.1, max=60.0),
    method: str = typer.Option("HEAD", "--method"),
    as_json: bool = typer.Option(False, "--json"),
    report: Optional[Path] = typer.Option(None, "--report", dir_okay=False, writable=True),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", file_okay=False),
    report_format: str = typer.Option("json", "--report-format"),
    report_formats: str = typer.Option("json,md,csv", "--report-formats"),
    overwrite_report: bool = typer.Option(False, "--overwrite-report"),
) -> None:
    if (url is None) == (from_file is None):
        raise typer.BadParameter("Provide either <url> or --from-file")

    if from_file is not None:
        urls = parse_headers_targets_file(from_file)
        payload = headers_check_batch(urls, timeout=timeout, method=method)
    else:
        if url is None:
            raise typer.BadParameter("<url> is required")
        payload = headers_check_one(url, timeout=timeout, method=method)

    written = emit_output(
        payload,
        json_stdout=as_json,
        report=report,
        report_dir=report_dir,
        report_format=report_format,
        report_formats=parse_formats_csv(report_formats),
        overwrite=overwrite_report,
        write_report=write_headers_report,
        write_report_dir=write_headers_report_dir,
    )
    for p in written:
        err_console.print(f"Wrote: {p}")

    if as_json:
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(audit_exit_code(payload))

    if payload.get("type") == "headers_check_batch":
        rows = payload.get("results") or []
        summary = payload.get("summary") or {}
        console.print(
            f"Summary: total={summary.get('total')} ok={summary.get('ok')} warning={summary.get('warning')} error={summary.get('error')}"
        )
    else:
        rows = [payload]

    table = Table(title="Headers Check")
    table.add_column("URL")
    table.add_column("HTTP", justify="right")
    table.add_column("Method")
    table.add_column("Missing")
    table.add_column("Status")

    for r in rows:
        if not isinstance(r, dict):
            continue
        target = r.get("target") or {}
        resp = r.get("response") or {}
        status = r.get("status") or {}
        missing = r.get("missing") or []
        err = status.get("error")
        if err is not None:
            st = "error"
        elif status.get("warning"):
            st = "warning"
        else:
            st = "ok" if status.get("ok") else "unknown"
        table.add_row(
            str(target.get("final_url") or target.get("url") or ""),
            str(resp.get("status") or ""),
            str(target.get("method") or ""),
            ",".join(missing) if isinstance(missing, list) else "",
            st,
        )

    console.print(table)

    code = audit_exit_code(payload)
    if code != 0:
        raise typer.Exit(code)


@profiles_app.command("path")
def profiles_path() -> None:
    console.print(str(profiles_file_path()))


@profiles_app.command("set")
def profiles_set(
    name: str = typer.Argument(...),
    target: str = typer.Option(..., "--target", "-t"),
    ports: str = typer.Option("1-1024", "--ports", "-p"),
    concurrency: int = typer.Option(500, "--concurrency", "-c", min=1, max=5000),
    timeout: float = typer.Option(0.5, "--timeout", "--to", min=0.05, max=10.0),
) -> None:
    set_profile(
        PortScanProfile(
            name=name,
            target=target,
            ports=ports,
            concurrency=concurrency,
            timeout=timeout,
        )
    )
    console.print("Saved.")


@profiles_app.command("list")
def profiles_list() -> None:
    rows = list_profiles()
    table = Table(title="Profiles")
    table.add_column("Name")
    table.add_column("Target")
    table.add_column("Ports")
    table.add_column("Concurrency", justify="right")
    table.add_column("Timeout", justify="right")
    for p in rows:
        table.add_row(p.name, p.target, p.ports, str(p.concurrency), str(p.timeout))
    console.print(table)


@profiles_app.command("delete")
def profiles_delete(name: str = typer.Argument(...)) -> None:
    delete_profile(name)
    console.print("Deleted.")


@plugins_app.command("list")
def plugins_list() -> None:
    plugins = load_plugins()
    for name in sorted(plugins.keys()):
        console.print(name)


@plugins_app.command("run")
def plugins_run(
    name: str = typer.Argument(...),
    args: List[str] = typer.Argument(None),
) -> None:
    plugins = load_plugins()
    if name not in plugins:
        raise typer.BadParameter("unknown plugin")
    code = plugins[name].run(args or [])
    raise typer.Exit(code)


@plugins_app.command("scaffold")
def plugins_scaffold(
    name: str = typer.Argument(...),
    out_dir: Path = typer.Option(Path("."), "--out", "-o", file_okay=False),
    overwrite: bool = typer.Option(False, "--overwrite"),
) -> None:
    created = create_plugin_skeleton(plugin_name=name, out_dir=out_dir, overwrite=overwrite)
    console.print(str(created))


@vault_app.command("init")
def vault_init() -> None:
    path = init_vault()
    console.print(f"Vault initialized at: {path}")


@vault_app.command("add")
def vault_add(
    service: str = typer.Argument(...),
    username: str = typer.Option(..., "--username", "-u"),
    password: Optional[str] = typer.Option(None, "--password", "-p", hide_input=True),
) -> None:
    if password is None:
        password = typer.prompt("Password", hide_input=True, confirmation_prompt=True)
    add_entry(service=service, username=username, password=password)
    console.print("Saved.")


@vault_app.command("get")
def vault_get(
    service: str = typer.Argument(...),
    show_password: bool = typer.Option(False, "--show-password"),
) -> None:
    entry = get_entry(service)
    console.print(f"service: {entry.service}")
    console.print(f"username: {entry.username}")
    if show_password:
        console.print(f"password: {entry.password}")


@vault_app.command("list")
def vault_list() -> None:
    services = list_services()
    for s in services:
        console.print(s)


@crypto_app.command("encrypt")
def crypto_encrypt(
    in_path: Path = typer.Option(..., "--input", "-i", exists=True, dir_okay=False, readable=True),
    out_path: Path = typer.Option(..., "--output", "-o", dir_okay=False, writable=True),
    password: Optional[str] = typer.Option(None, "--password", hide_input=True),
    overwrite: bool = typer.Option(False, "--overwrite"),
) -> None:
    if password is None:
        password = typer.prompt("Password", hide_input=True, confirmation_prompt=True)
    encrypt_file(in_path, out_path, password, overwrite=overwrite)
    console.print(f"Wrote: {out_path}")


@crypto_app.command("decrypt")
def crypto_decrypt(
    in_path: Path = typer.Option(..., "--input", "-i", exists=True, dir_okay=False, readable=True),
    out_path: Path = typer.Option(..., "--output", "-o", dir_okay=False, writable=True),
    password: Optional[str] = typer.Option(None, "--password", hide_input=True),
    overwrite: bool = typer.Option(False, "--overwrite"),
) -> None:
    if password is None:
        password = typer.prompt("Password", hide_input=True)
    decrypt_file(in_path, out_path, password, overwrite=overwrite)
    console.print(f"Wrote: {out_path}")


@hash_app.command("text")
def hash_text_cmd(
    text: str = typer.Argument(...),
    algo: str = typer.Option("sha256", "--algo", "-a"),
) -> None:
    console.print(hash_text(algo, text))


@hash_app.command("file")
def hash_file_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    algo: str = typer.Option("sha256", "--algo", "-a"),
) -> None:
    with Progress(transient=True) as progress:
        task = progress.add_task("hashing", total=None)
        digest = hash_file(algo, path)
        progress.update(task, completed=1)
    console.print(digest)


@hash_app.command("verify")
def hash_verify_cmd(
    expected: str = typer.Option(..., "--hash"),
    algo: str = typer.Option("sha256", "--algo", "-a"),
    text: Optional[str] = typer.Option(None, "--text"),
    path: Optional[Path] = typer.Option(None, "--file", exists=True, dir_okay=False, readable=True),
) -> None:
    if (text is None) == (path is None):
        raise typer.BadParameter("Provide exactly one of --text or --file")

    if text is not None:
        actual = hash_text(algo, text)
    else:
        if path is None:
            raise typer.BadParameter("--file is required")
        actual = hash_file(algo, path)
    if actual.lower() == expected.strip().lower():
        console.print("OK")
    else:
        console.print("MISMATCH")
        raise typer.Exit(1)
