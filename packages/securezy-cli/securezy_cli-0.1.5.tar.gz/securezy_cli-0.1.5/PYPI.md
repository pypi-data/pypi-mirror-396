# Securezy CLI (`securezy-cli`)

Securezy CLI is a lightweight, pip-installable Python command-line toolkit for common security tasks: port scanning, TLS checks, JWT inspection, webhook signing/verification, security headers auditing, password/token generation, vault storage, file crypto, hashing, reports, and plugins.

PyPI: `securezy-cli` (CLI command: `securezy`)

## Install

```bash
python -m pip install "securezy-cli[crypto,vault]"
securezy --help
```

## Quickstart

```bash
securezy scan ports -t 127.0.0.1 -p 1-1024
securezy tls check example.com
securezy vault init
securezy crypto encrypt -i secret.txt -o secret.txt.sz
securezy hash text --algo sha256 "hello"
```

## Examples (by feature)

### Port scan

```bash
securezy scan ports -t 127.0.0.1 -p 1-1024
securezy scan ports -t 127.0.0.1 -p 22,80,443 --json
```

### TLS certificate check

```bash
securezy tls check example.com
securezy tls check --from-file targets.txt --report-dir reports
```

### JWT inspection

```bash
securezy jwt inspect "<token>" --json
securezy jwt inspect --from-file tokens.txt --report jwt.md --report-format md
```

### Webhook signing and verification (HMAC)

```bash
echo -n '{"id": 1}' | securezy webhook sign --stdin --secret env:WEBHOOK_SECRET --encoding hex
securezy webhook verify --sig "<signature>" --file payload.json --secret vault:stripe --encoding hex
```

### Security headers audit

```bash
securezy headers check https://example.com --json
securezy headers check --from-file urls.txt --report-dir reports
```

### Password / token generator

```bash
securezy pwgen --preset site --len 24 --no-ambiguous
securezy pwgen --preset base64url --bytes 32 --count 5 --json
```

### Vault, crypto, and hashing

```bash
securezy vault init
securezy vault add github --username akash --password prompt
securezy vault get github
securezy crypto encrypt -i secret.txt -o secret.txt.sz
securezy crypto decrypt -i secret.txt.sz -o secret.txt
securezy hash file -i secret.txt --algo sha256
```

## Reports and automation

Most audit-style commands support:

```bash
--json
--report <path> --report-format json|md|csv
--report-dir <dir> --report-formats "json,md,csv"
--overwrite-report
```

## Plugins

Plugins are discovered via Python entry points group `securezy.plugins`.

```bash
securezy plugins list
securezy plugins scaffold my-plugin -o .
```
