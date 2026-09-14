# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Active |
| < 1.0   | ❌ Not supported |

---

## Reporting a Vulnerability

We take the security of ContainerGuard seriously. If you believe you've
found a security vulnerability, please report it responsibly.

### 🔒 How to Report

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, report via:

- 📧 **Email:** muralipala15@gmail.com
- 📝 **Subject line:** `[SECURITY] ContainerGuard - <brief description>`

### 📋 What to Include

Please provide:

- **Description** — Clear explanation of the vulnerability
- **Steps to reproduce** — Detailed steps to trigger it
- **Impact** — What an attacker could accomplish
- **Affected versions** — Which versions are impacted
- **Proof of concept** — If available (sanitized)
- **Suggested fix** — Optional

---

## Response Timeline

| Stage | Timeframe |
|-------|-----------|
| **Initial response** | Within 48 hours |
| **Triage & confirmation** | Within 5 business days |
| **Fix development** | Depends on severity |
| **Public disclosure** | Coordinated with reporter |

---

## What to Expect

1. **Acknowledgment** — We'll confirm receipt of your report
2. **Assessment** — We'll investigate and validate the issue
3. **Resolution** — We'll develop and test a fix
4. **Credit** — We'll credit you in the security advisory (if desired)
5. **Disclosure** — Coordinated public disclosure after fix is released

---

## Scope

### In Scope

- ContainerGuard agent (`agent/`)
- Web dashboard (`dashboard/`)
- Installer script (`install.sh`)
- Any code in this repository

### Out of Scope

- Vulnerabilities in Docker itself (report to Docker)
- Vulnerabilities in Python or dependencies (report upstream)
- Misconfiguration by users (e.g., exposing dashboard publicly without auth)
- Social engineering attacks
- Denial of service from resource exhaustion

---

## Security Best Practices

When deploying ContainerGuard, we recommend:

- ✅ Run the agent as a **non-root user** (default)
- ✅ Keep **Docker** and **Python** up to date
- ✅ Use **firewall rules** to restrict access to port 7860
- ✅ Enable **SELinux** if available (AlmaLinux/RHEL)
- ✅ **Do not** expose the dashboard to the public internet without auth
- ✅ **Do not** expose Docker API on port 2375 to the internet (Multi-Host Pro feature)
- ✅ Store `.env` files securely (never commit them)

---

## Known Security Considerations

### Dashboard Access

The Gradio dashboard (port 7860) has **no built-in authentication** in the
Free tier. Deploy it in a trusted network only.

> **💎 Pro tier** includes **GitHub OAuth** authentication for production use.

### Docker Socket Access

The agent requires access to `/var/run/docker.sock` — effectively root-level
access to the Docker daemon. Only install ContainerGuard on trusted systems.

### Multi-Host Docker API

The Pro tier supports connecting to remote Docker APIs over TCP (port 2375).
**Never expose port 2375 to the public internet.** Use TLS or SSH tunneling
for remote connections.

---

## 💎 Pro Tier Security

For the Pro tier (Multi-Host, Slack, Auto-cleanup, GitHub OAuth):

- Same disclosure process — email **muralipala15@gmail.com**
- Priority support for licensees
- Subject line: `[SECURITY-PRO] <description>`

---

## Acknowledgments

We thank the following researchers for responsibly disclosing issues:

*(None yet — be the first!)*

---

**Last Updated:** 2026-09-15
