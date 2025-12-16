# TLS Check

`securezy tls check` inspects a remote TLS endpoint and reports certificate expiry and connection details.

## Command

- `securezy tls check <host>`
- `securezy tls check --from-file <path>`

## Examples

```powershell
securezy tls check example.com
securezy tls check example.com --warn-days 30
securezy tls check example.com --port 8443 --timeout 5
securezy tls check example.com --no-verify
securezy tls check --from-file .\hosts.txt --warn-days 30 --report .\tls-report.json
securezy tls check --from-file .\hosts.txt --warn-days 30 --report-dir .\reports --report-formats json,md,csv
```

## Flags

### Connection

- `--port` (default: `443`)
- `--timeout` (default: `3.0`)
- `--servername` (SNI override)
- `--min-tls` (optional: `1.2` or `1.3`)

### Verification

- default: verify certificate chain + hostname
- `--no-verify` disables verification and prints a warning
- `--ca-file` uses a custom CA bundle (useful for corporate/internal CAs)

### Batch input

`--from-file` supports:

- `example.com`
- `example.com:8443`
- `example.com:443,api.example.com` (host,port,servername)
- blank lines and `# comments` are ignored

## Output + reporting

- `--json` prints JSON to stdout
- `--report` writes a single report file
- `--report-dir` writes a report bundle directory
- `--report-format` supports: `json`, `csv`, `md`
- `--report-formats` supports: `json,md,csv`
- `--overwrite-report` overwrites existing report files

## Exit codes (CI-friendly)

- `0`: all OK
- `1`: any warning (expiry <= `--warn-days`, default 30)
- `2`: any error (connect/handshake/verify/parsing)

## Safety guardrails

- TLS verification is enabled by default
- No PEM/private key material is printed
- Timeouts are always applied
