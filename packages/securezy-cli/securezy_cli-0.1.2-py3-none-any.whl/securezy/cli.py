from __future__ import annotations

from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from pathlib import Path

from .tools.portscan import parse_ports, result_to_json, scan_ports_sync
from .tools.vault import add_entry, get_entry, init_vault, list_services
from .tools.crypto import decrypt_file, encrypt_file
from .tools.hashing import hash_file, hash_text
from .tools.plugins import load_plugins
from .tools.plugin_scaffold import create_plugin_skeleton
from .tools.profiles import PortScanProfile, delete_profile, get_profile, list_profiles, profiles_file_path, set_profile
from .tools.reporting import write_portscan_report, write_portscan_report_dir

app = typer.Typer(add_completion=True, no_args_is_help=True)
console = Console()
scan_app = typer.Typer(add_completion=True, no_args_is_help=True)
app.add_typer(scan_app, name="scan")
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
            console.print(f"Wrote: {p}")

    if as_json:
        console.print(result_to_json(result))
        return

    table = Table(title=f"Open ports on {result.target}")
    table.add_column("Port", justify="right")
    for p in result.open_ports:
        table.add_row(str(p))
    console.print(table)
    console.print(f"Found {len(result.open_ports)} open ports")


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
