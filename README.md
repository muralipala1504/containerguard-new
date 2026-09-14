# 🔐 ContainerGuard

**Autonomous Docker Agent** - Monitors containers and performs auto-healing on a single Docker host without human intervention.

[![Release](https://img.shields.io/github/v/release/muralipala1504/containerguard-new?label=release&color=blue)](https://github.com/muralipala1504/containerguard-new/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

---

## 📖 Overview

ContainerGuard is a lightweight, autonomous agent that monitors Docker containers and automatically takes corrective actions. It acts as your personal **sysadmin**, handling common container failures without human intervention.

**This is the Free/Community edition** — monitoring a single Docker host with core auto-healing features.

---

## 🚀 Key Features (Free Tier)

| Feature | Description |
|---------|-------------|
| 🔍 **Health Monitoring** | Continuously checks container health status |
| 🔄 **Auto-Heal** | Automatically restarts crashed/exited containers |
| 📊 **Web Dashboard** | Gradio UI with container status and action history |
| 📜 **Persistent History** | 7-day action log for audit |
| 🐳 **Docker Native** | Works with Docker and Docker Compose |
| 🔒 **SELinux Ready** | Automatically configures SELinux contexts |

---

## 💎 Upgrade to ContainerGuard Pro

Want advanced features for production and multi-node environments?

| Feature | Free | **Pro** |
|---------|:----:|:-------:|
| Container monitoring | ✅ Unlimited | ✅ Unlimited |
| Auto-restart | ✅ | ✅ |
| Web dashboard | ✅ | ✅ |
| Action history | 7 days | ✅ **Unlimited** |
| **Multi-Host** (control + workers) | ❌ | ✅ |
| **Slack alerts** | ❌ | ✅ |
| **Auto-cleanup** (images, volumes) | ❌ | ✅ |
| **GitHub OAuth** authentication | ❌ | ✅ |

### 🔓 Get Pro Access

ContainerGuard Pro is distributed via private repository access.

**To request Pro access:**
- 📧 Contact: **muralipala15@gmail.com**
- 📝 Include your GitHub username
- 🔑 You'll receive an invite to the private Pro repository

**Pro includes:**
- Full source code (private repo)
- Interactive Multi-Host installer
- Complete documentation (6 docs incl. troubleshooting)
- Priority support

---

## ⚡ Quick Start

### One-Line Installation (Free Tier)

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/master/install.sh | bash
```

### What the Installer Does

The installer will:
- ✅ Check prerequisites (Docker, Python, OS)
- ✅ Auto-install Docker if missing
- ✅ Clone the repository
- ✅ Create Python virtual environment
- ✅ Install dependencies
- ✅ Configure SELinux context (if enforcing)
- ✅ Install systemd services
- ✅ Open firewall port 7860
- ✅ Start the agent and dashboard

---

## 🐳 Docker Installation

Alternatively, run ContainerGuard via Docker Compose:

```bash
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new
docker compose up -d
```

Access dashboard at: **http://localhost:7860**

---

## 🌐 Dashboard

Access the web dashboard at **http://<your-ip>:7860**:

- **Container Status** — Real-time view of all containers
- **Action History** — 7-day audit log (Unlimited in Pro)
- **Manual Controls** — Restart/stop containers manually

---

## 🔧 Systemd Service Management

```bash
# Check status
sudo systemctl status containerguard
sudo systemctl status containerguard-dashboard

# View logs
sudo journalctl -u containerguard -f
sudo journalctl -u containerguard-dashboard -f

# Stop/Start/Restart
sudo systemctl {stop|start|restart} containerguard
sudo systemctl {stop|start|restart} containerguard-dashboard

# Enable on boot
sudo systemctl enable containerguard
sudo systemctl enable containerguard-dashboard
```

---

## 📁 Persistent History

All agent actions are logged to `/tmp/containerguard_history.json`:

```json
[
  {
    "timestamp": "2026-09-14T05:35:57.986681",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  }
]
```

> **Note:** Free tier retains 7 days of history. **Pro tier** retains unlimited history.

---

## 📚 Documentation

- **[README.md](README.md)** — Project overview (this file)
- **[INSTALL.md](INSTALL.md)** — Detailed installation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Technical design
- **[API.md](API.md)** — API reference

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/muralipala1504/containerguard-new/issues)
- **Discussions:** [GitHub Discussions](https://github.com/muralipala1504/containerguard-new/discussions)
- **Pro Access:** muralipala15@gmail.com

---

**Built with ❤️ for the Docker community**
