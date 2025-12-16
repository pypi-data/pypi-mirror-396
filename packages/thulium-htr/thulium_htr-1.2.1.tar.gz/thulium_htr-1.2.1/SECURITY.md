# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Thulium, please report it
responsibly.

### How to Report

1. **Do not** open a public issue
2. Email security concerns to: security@thulium-dev.io
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Resolution**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: Next release

### Disclosure Policy

- We follow responsible disclosure practices
- Reporters will be credited (unless anonymity requested)
- CVE will be requested for confirmed vulnerabilities

## Security Best Practices

When using Thulium:

1. **Validate inputs** — Don't process untrusted images without validation
2. **Use latest version** — Security fixes are only in supported versions
3. **Verify model integrity** — Check model hashes when downloading
4. **Sandbox execution** — Run untrusted workloads in containers
