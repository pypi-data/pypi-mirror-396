# Securezy CLI (`securezy-cli`) - Production Guide

## 1) Overview

This repository contains:

- A modernized, pip-installable Python package distributed as `securezy-cli` (module name: `securezy`)

The modern package provides:

- `securezy scan ports`: fast bounded-concurrency TCP port scanning
- `securezy tls check`: TLS certificate expiry and verification checks
- `securezy vault`: encrypted local credential vault stored per-user
- `securezy crypto`: file encryption/decryption using password-based keys
- `securezy hash`: hashing utilities for text/files

## 2) Recommended environment

- Python: 3.10+ (3.9 is supported)
- OS: Windows/Linux/macOS
- Run inside a project virtual environment (`.venv`)

## 3) Install

From the repo root (editable install):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev,crypto,vault]"
```

Install from PyPI:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install "securezy-cli[crypto,vault]"
```

Verify the CLI:

```powershell
securezy --help
```

Notes:

- `dev` installs test/lint tooling
- `crypto` installs cryptography dependency for encryption/decryption
- `vault` installs cryptography dependency for the vault

## 4) Quickstart

### 4.1 Fast port scan

```powershell
securezy scan ports -t 127.0.0.1 -p 1-1024
securezy scan ports -t scanme.nmap.org -p 22,80,443 --timeout 0.8 --concurrency 800
securezy scan ports -t 127.0.0.1 -p 1-1024 --json
```

### 4.2 TLS checks

```powershell
securezy tls check example.com
securezy tls check --from-file .\hosts.txt --warn-days 30
```

### 4.3 Vault

```powershell
securezy vault init
securezy vault add github -u akash
securezy vault list
securezy vault get github --show-password
```

Vault storage location:

- Windows: `%APPDATA%\securezy\vault.db`

### 4.3 File encryption

```powershell
securezy crypto encrypt -i secret.txt -o secret.txt.sz
securezy crypto decrypt -i secret.txt.sz -o secret.txt
```

### 4.4 Hashing

```powershell
securezy hash text --algo sha256 "hello"
securezy hash file --algo sha256 .\somefile.iso
securezy hash verify --algo sha256 --hash <expected> --file .\somefile.iso
```

## 5) Safety notes

- Only scan systems you own or have explicit permission to test.
- The vault is encrypted, but your security still depends on your master password.
- Do not commit secrets (`vault.db`, `pw.db`, `key.key`) or private wordlists.
- Large wordlists can contain sensitive data; treat them as restricted artifacts.

## 6) Development workflow

### 6.1 Run tests

```powershell
python -m pytest -q
```

### 6.2 Lint

```powershell
python -m ruff check securezy tests
```

## 7) Packaging and release workflow

### 7.1 Versioning

- Update `version` in `pyproject.toml`
- Tag releases using `vX.Y.Z`

### 7.2 Build

```powershell
python -m pip install -U build
python -m build
```

### 7.3 Publish

- Use GitHub Actions or publish manually:

```powershell
python -m pip install -U twine
python -m twine upload dist/*
```
