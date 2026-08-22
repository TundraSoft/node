# Security

## 🔒 Our commitment to security

We take security seriously. This repository implements comprehensive, automated security scanning to protect against vulnerabilities, secrets exposure, and security threats. Our multi-layered security approach includes container scanning, code analysis, dependency checking, and continuous monitoring.

Images are rebuilt weekly for the five newest Node.js **LTS** releases on each supported Alpine branch, so those tags pick up Alpine and Node security patches automatically. Our primary focus is always the newest LTS release (the `latest` and `<major>` tags), as upstream patches are typically available there first; older tags stop being rebuilt once they fall out of the five-newest window.

**Security is everyone's responsibility.** We encourage all contributors to:
- Report security issues responsibly using GitHub's private vulnerability reporting
- Review security scan results before merging pull requests  
- Keep dependencies updated and follow security best practices
- Never commit secrets, passwords, or sensitive information

For critical security vulnerabilities, please use [GitHub's private vulnerability reporting](https://github.com/TundraSoft/node/security/advisories/new).

---

## Automated tools used

### 1. Trivy (Container & Dependency Scanner)
- **Purpose**: Scans Docker images and filesystems for vulnerabilities
- **Coverage**: Container images, dependencies, OS packages
- **Runs**: After build completion, on-demand (manual trigger), and daily
- **Results**: Available in GitHub Security tab; the container scan fails the build on fixable HIGH/CRITICAL findings (documented exceptions live in `.trivyignore`)

### 2. CodeQL (Code Security Analysis)
- **Purpose**: Identifies security vulnerabilities in code
- **Coverage**: JavaScript, Python, and other supported languages
- **Runs**: After build completion, on-demand (manual trigger), and daily
- **Results**: Available in GitHub Security tab

### 3. GitLeaks (Secret Scanner)
- **Purpose**: Detects secrets, passwords, and API keys
- **Coverage**: Git history, current files, commits
- **Runs**: Early in build workflow (as backup) and on manual/scheduled security scans
- **Results**: Fails build if secrets found

### 4. Grype (Vulnerability Scanner)
- **Purpose**: Alternative container vulnerability scanner
- **Coverage**: Container images, OS packages
- **Runs**: After build completion, on-demand (manual trigger), and daily
- **Results**: Available in GitHub Security tab

### 5. Semgrep (SAST Scanner)
- **Purpose**: Static Application Security Testing
- **Coverage**: Security patterns, code quality, secrets
- **Runs**: After build completion, on-demand (manual trigger), and daily
- **Results**: Available in GitHub Security tab

### 6. Licensee (License Compliance)
- **Purpose**: Detects and validates open source licenses
- **Coverage**: Project licenses, dependency licenses
- **Runs**: After build completion, on-demand (manual trigger), and daily
- **Results**: Available in workflow summary
