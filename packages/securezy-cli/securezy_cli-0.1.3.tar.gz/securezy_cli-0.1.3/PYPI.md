# Securezy CLI (`securezy-cli`)

Securezy CLI is a lightweight, pip-installable Python command-line toolkit for common security tasks: fast TCP port scanning, encrypted vault storage, file encryption, hashing, scan reports, and plugins.

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

## Plugins

Plugins are discovered via Python entry points group `securezy.plugins`.

```bash
securezy plugins list
securezy plugins scaffold my-plugin -o .
```
