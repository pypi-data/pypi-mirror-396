# Securezy CLI (`securezy-cli`) - Production Guide

## 1) Overview

This repository contains:

- A modernized, pip-installable Python package distributed as `securezy-cli` (module name: `securezy`)

The modern package provides:

- `securezy scan ports`: fast bounded-concurrency TCP port scanning
- `securezy vault`: encrypted local credential vault stored per-user
- `securezy crypto`: file encryption/decryption using password-based keys
- `securezy hash`: hashing utilities for text/files

## 2) Recommended environment

- Python: 3.10+ (3.9 is supported)
- OS: Windows/Linux/macOS
- Run inside a project virtual environment (`.venv`)

## 3) Install (local development)

From the repo root:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -U pip setuptools wheel
.\.venv\Scripts\python -m pip install -e ".[dev,crypto,vault]"
```

Install from PyPI:

```powershell
py -m pip install "securezy-cli[crypto,vault]"
```

Notes:

- `dev` installs test/lint tooling
- `crypto` installs cryptography dependency for encryption/decryption
- `vault` installs cryptography dependency for the vault

## 4) Quickstart

### 4.1 Fast port scan

```powershell
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024
.\.venv\Scripts\python -m securezy scan ports -t scanme.nmap.org -p 22,80,443 --timeout 0.8 --concurrency 800
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --json
```

### 4.2 Vault

```powershell
.\.venv\Scripts\python -m securezy vault init
.\.venv\Scripts\python -m securezy vault add github -u akash
.\.venv\Scripts\python -m securezy vault list
.\.venv\Scripts\python -m securezy vault get github --show-password
```

Vault storage location:

- Windows: `%APPDATA%\securezy\vault.db`

### 4.3 File encryption

```powershell
.\.venv\Scripts\python -m securezy crypto encrypt -i secret.txt -o secret.txt.sz
.\.venv\Scripts\python -m securezy crypto decrypt -i secret.txt.sz -o secret.txt
```

### 4.4 Hashing

```powershell
.\.venv\Scripts\python -m securezy hash text --algo sha256 "hello"
.\.venv\Scripts\python -m securezy hash file --algo sha256 .\somefile.iso
.\.venv\Scripts\python -m securezy hash verify --algo sha256 --hash <expected> --file .\somefile.iso
```

## 5) Security and safety notes

- Only scan systems you own or have explicit permission to test.
- The vault is encrypted, but your security still depends on your master password.
- Do not commit secrets (`vault.db`, `pw.db`, `key.key`) or private wordlists.
- Large wordlists can contain sensitive data; treat them as restricted artifacts.

## 6) Development workflow

### 6.1 Run tests

```powershell
.\.venv\Scripts\python -m pytest -q
```

### 6.2 Lint

```powershell
.\.venv\Scripts\python -m ruff check securezy tests
```

## 7) Packaging and release workflow

### 7.1 Versioning

- Update `version` in `pyproject.toml`
- Tag releases using `vX.Y.Z`

### 7.2 Build

```powershell
.\.venv\Scripts\python -m pip install -U build
.\.venv\Scripts\python -m build
```

### 7.3 Publish

- Use GitHub Actions or publish manually:

```powershell
.\.venv\Scripts\python -m pip install -U twine
.\.venv\Scripts\python -m twine upload dist/*
```
