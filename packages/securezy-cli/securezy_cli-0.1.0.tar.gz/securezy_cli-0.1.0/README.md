# Securezy CLI (`securezy-cli`)

Securezy is a modernized, pip-installable Python CLI toolkit built on top of the original (legacy) Tkinter “Penetration Testing Framework” project.

PyPI distribution name: `securezy-cli`

Import/module name: `securezy`

The repo contains the modern `securezy` CLI package.

## Install (recommended)

Create a virtualenv and install editable:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -U pip setuptools wheel
.\.venv\Scripts\python -m pip install -e ".[dev,crypto,vault]"
```

Install from PyPI:

```powershell
py -m pip install "securezy-cli[crypto,vault]"
```

## CLI quickstart

Show commands:

```powershell
.\.venv\Scripts\python -m securezy --help
```

### Fast port scanning

```powershell
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 22,80,443 --timeout 0.8 --concurrency 800
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --json
```

### Scan reporting/export (JSON/CSV/Markdown)

Single report file:

```powershell
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.json --report-format json
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.md --report-format md
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.csv --report-format csv
```

Report bundle directory:

```powershell
.\.venv\Scripts\python -m securezy scan ports -t 127.0.0.1 -p 1-1024 --report-dir .\reports --report-formats json,md,csv
```

### Profiles (saved scan configs)

Create and use a profile:

```powershell
.\.venv\Scripts\python -m securezy profiles set local -t 127.0.0.1 -p 1-1024 --timeout 0.5 --concurrency 500
.\.venv\Scripts\python -m securezy profiles list
.\.venv\Scripts\python -m securezy scan ports --profile local
```

Show where profiles are stored:

```powershell
.\.venv\Scripts\python -m securezy profiles path
```

To store profiles in a custom location (useful for CI/tests):

```powershell
$env:SECUREZY_HOME = "C:\\temp\\securezy"
```

### Plugins

List and run plugins:

```powershell
.\.venv\Scripts\python -m securezy plugins list
.\.venv\Scripts\python -m securezy plugins run hello "hello from plugin"
```

Plugins are discovered via Python entrypoints group `securezy.plugins`.

Generate a new plugin skeleton:

```powershell
.\.venv\Scripts\python -m securezy plugins scaffold my-plugin -o .
```

Then install it:

```powershell
cd .\securezy-plugin-my-plugin
py -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e .
```

And verify it shows up:

```powershell
.\.venv\Scripts\python -m securezy plugins list
.\.venv\Scripts\python -m securezy plugins run my-plugin "it works"
```

### Vault (encrypted credential storage)

```powershell
.\.venv\Scripts\python -m securezy vault init
.\.venv\Scripts\python -m securezy vault add github -u akash
.\.venv\Scripts\python -m securezy vault get github --show-password
.\.venv\Scripts\python -m securezy vault list
```

### Crypto (file encryption/decryption)

```powershell
.\.venv\Scripts\python -m securezy crypto encrypt -i secret.txt -o secret.txt.sz
.\.venv\Scripts\python -m securezy crypto decrypt -i secret.txt.sz -o secret.txt
```

### Hashing + verify

```powershell
.\.venv\Scripts\python -m securezy hash text --algo sha256 "hello"
.\.venv\Scripts\python -m securezy hash file --algo sha256 .\somefile.iso
.\.venv\Scripts\python -m securezy hash verify --algo sha256 --hash <expected> --file .\somefile.iso
```

## Development

```powershell
.\.venv\Scripts\python -m ruff check securezy tests
.\.venv\Scripts\python -m pytest -q
```

## Publishing (TestPyPI / PyPI)

This repo includes a GitHub Actions workflow at `.github/workflows/release.yml`.

### Required GitHub secrets

Create these secrets in your GitHub repo settings:

- `PYPI_API_TOKEN`
- `TEST_PYPI_API_TOKEN`

### Publish to TestPyPI (recommended first)

Use GitHub Actions `Release` workflow → `Run workflow` → choose `testpypi`.

### Publish to PyPI

Option A (recommended): push a tag like `v0.1.0`:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Option B: run the GitHub Actions workflow manually and choose `pypi`.
