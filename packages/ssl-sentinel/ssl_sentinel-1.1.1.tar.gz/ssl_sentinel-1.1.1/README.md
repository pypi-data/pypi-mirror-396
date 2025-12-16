# SSL Sentinel

A command-line tool for checking SSL/TLS certificate validity and expiration dates. Ideal for monitoring multiple domains and identifying certificates that require attention.

## Installation

You can install `ssl-sentinel` directly from PyPI using `pip`.

```bash
pip install ssl-sentinel
```

## Usage

### Check a Single Domain

Use the `-H` or `--hostname` flag to check a specific domain.

```bash
ssl-sentinel --hostname google.com
```

### Check Multiple Domains from a File

Use the `-f` or `--file` flag to provide a text file with one domain per line.

```bash
ssl-sentinel --file domains.txt
```

### Show Only Expiring Certificates

Add the `--expiring-soon` flag to filter the output and show only certificates that have expired or will expire within the next 30 days. This works with both single-host and file mode.

```bash
ssl-sentinel --file domains.txt --expiring-soon
```
### Changing the Threshold

Add the `-t` flag to change the threshold.
```bash
ssl-sentinel --file domains.txt --expiring-soon -t 60
```

### Interactive Mode

If you run the command without any arguments, it will prompt you to enter a domain name.

```bash
ssl-sentinel
```

## License

MIT License
