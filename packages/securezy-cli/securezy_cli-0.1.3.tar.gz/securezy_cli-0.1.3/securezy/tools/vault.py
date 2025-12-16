from __future__ import annotations

import base64
import os
import sqlite3
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class VaultEntry:
    service: str
    username: str
    password: str


def _get_app_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "securezy"
    return Path.home() / ".securezy"


def _vault_db_path() -> Path:
    return _get_app_dir() / "vault.db"


def _require_crypto():
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        return Fernet, hashes, PBKDF2HMAC
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "cryptography is required for vault features. Install with: pip install 'securezy[vault]'"
        ) from e


def _derive_fernet_key(master_password: str, salt: bytes) -> bytes:
    Fernet, hashes, PBKDF2HMAC = _require_crypto()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
    return key


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_vault(db_path: Optional[Path] = None) -> Path:
    db_path = db_path or _vault_db_path()
    if db_path.exists():
        return db_path

    salt = os.urandom(16)
    conn = _connect(db_path)
    try:
        conn.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v BLOB NOT NULL)")
        conn.execute("CREATE TABLE entries (service TEXT PRIMARY KEY, username TEXT NOT NULL, secret BLOB NOT NULL)")
        conn.execute("INSERT INTO meta (k, v) VALUES ('salt', ?) ", (salt,))
        conn.commit()
    finally:
        conn.close()

    return db_path


def _get_salt(conn: sqlite3.Connection) -> bytes:
    row = conn.execute("SELECT v FROM meta WHERE k='salt'").fetchone()
    if not row:
        raise RuntimeError("vault is not initialized")
    return row[0]


def add_entry(service: str, username: str, password: str, *, db_path: Optional[Path] = None) -> None:
    db_path = db_path or _vault_db_path()
    conn = _connect(db_path)
    try:
        salt = _get_salt(conn)
        master = getpass("Master password: ")
        key = _derive_fernet_key(master, salt)
        Fernet, _, _ = _require_crypto()
        f = Fernet(key)
        secret = f.encrypt(password.encode("utf-8"))
        conn.execute(
            "INSERT INTO entries(service, username, secret) VALUES(?, ?, ?) "
            "ON CONFLICT(service) DO UPDATE SET username=excluded.username, secret=excluded.secret",
            (service, username, secret),
        )
        conn.commit()
    finally:
        conn.close()


def get_entry(service: str, *, db_path: Optional[Path] = None) -> VaultEntry:
    db_path = db_path or _vault_db_path()
    conn = _connect(db_path)
    try:
        salt = _get_salt(conn)
        row = conn.execute("SELECT service, username, secret FROM entries WHERE service=?", (service,)).fetchone()
        if not row:
            raise KeyError(service)

        master = getpass("Master password: ")
        key = _derive_fernet_key(master, salt)
        Fernet, _, _ = _require_crypto()
        f = Fernet(key)
        password = f.decrypt(row[2]).decode("utf-8")
        return VaultEntry(service=row[0], username=row[1], password=password)
    finally:
        conn.close()


def list_services(*, db_path: Optional[Path] = None) -> list[str]:
    db_path = db_path or _vault_db_path()
    conn = _connect(db_path)
    try:
        salt = _get_salt(conn)
        _ = salt
        rows = conn.execute("SELECT service FROM entries ORDER BY service").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()
