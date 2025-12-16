# Securezy CLI (`securezy-cli`)

Securezy CLI is a lightweight, pip-installable Python toolkit for common security tasks: fast TCP port scanning, TLS certificate checks, encrypted vault storage, file encryption, hashing, scan reports, and plugins.

- **PyPI distribution**: `securezy-cli`
- **CLI command**: `securezy`
- **Import/module name**: `securezy`

The PyPI “Project description” is sourced from `PYPI.md`. This `README.md` is for the repository/codebase.

## Install

### From PyPI

```powershell
python -m pip install "securezy-cli[crypto,vault]"
securezy --help
```

### Local development (editable)

```powershell
python -m pip install -e ".[dev,crypto,vault]"
securezy --help
```

## Quickstart

Once your environment is set up (and your venv is activated, if you use one), commands are just:

```powershell
securezy --help
```

### Port scanning

```powershell
securezy scan ports -t 127.0.0.1 -p 1-1024
securezy scan ports -t 127.0.0.1 -p 22,80,443 --timeout 0.8 --concurrency 800
securezy scan ports -t 127.0.0.1 -p 1-1024 --json
```

### TLS certificate checks

```powershell
securezy tls check example.com
securezy tls check example.com --warn-days 30
securezy tls check --from-file .\hosts.txt --warn-days 30 --report .\tls-report.json
```

See: `docs/tls_check.md`

### Reports

```powershell
securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.json --report-format json
securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.md --report-format md
securezy scan ports -t 127.0.0.1 -p 1-1024 --report .\report.csv --report-format csv
securezy scan ports -t 127.0.0.1 -p 1-1024 --report-dir .\reports --report-formats json,md,csv
```

### Profiles

```powershell
securezy profiles set local -t 127.0.0.1 -p 1-1024 --timeout 0.5 --concurrency 500
securezy profiles list
securezy scan ports --profile local
securezy profiles path
```

To store profiles in a custom location:

```powershell
$env:SECUREZY_HOME = "C:\\temp\\securezy"
```

### Plugins

Plugins are discovered via Python entry points group `securezy.plugins`.

```powershell
securezy plugins list
securezy plugins run hello "hello from plugin"
securezy plugins scaffold my-plugin -o .
```

### Vault

```powershell
securezy vault init
securezy vault add github -u akash
securezy vault get github --show-password
securezy vault list
```

### Crypto

```powershell
securezy crypto encrypt -i secret.txt -o secret.txt.sz
securezy crypto decrypt -i secret.txt.sz -o secret.txt
```

### Hashing

```powershell
securezy hash text --algo sha256 "hello"
securezy hash file --algo sha256 .\somefile.iso
securezy hash verify --algo sha256 --hash <expected> --file .\somefile.iso
```

## Development

```powershell
python -m ruff check securezy tests
python -m pytest -q
```

## Publishing (TestPyPI / PyPI)

This repo includes a GitHub Actions workflow at `.github/workflows/release.yml`.

### Required GitHub secrets

- `PYPI_API_TOKEN`
- `TEST_PYPI_API_TOKEN`

### Publish to TestPyPI

Use GitHub Actions `Release` workflow → `Run workflow` → choose `testpypi`.

### Publish to PyPI

Option A (recommended): push a tag like `vX.Y.Z`:

```powershell
git tag vX.Y.Z
git push origin vX.Y.Z
```

Option B: run the GitHub Actions workflow manually and choose `pypi`.
