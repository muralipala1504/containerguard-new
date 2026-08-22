# 🔐 ContainerGuard

**Autonomous Docker Agent** - Monitors containers and performs auto-healing, cleanup, and scaling without human intervention.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

---

## 📖 Overview

ContainerGuard is a lightweight, autonomous agent that monitors Docker containers and automatically takes corrective actions. It acts as your personal **sysadmin**, handling common container failures without human intervention.

### 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Health Monitoring** | Continuously checks container health status |
| 🔄 **Auto-Heal** | Automatically restarts crashed/exited containers |
| 🧹 **Auto-Cleanup** | Removes unused images, volumes, and dangling resources |
| 📊 **Dashboard** | Web UI with container status and action history |
| 📜 **Persistent History** | All actions logged to JSON file for audit |
| 🔔 **Alerts** | Send notifications via Slack, Discord, or Email (coming soon) |
| 🐳 **Docker Native** | Works with Docker and Docker Compose |
| 🔒 **SELinux Ready** | Automatically configures SELinux contexts |

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────────────────────────┐
│ ContainerGuard System │
│ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ User Interface Layer │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Gradio │ │ CLI │ │ REST API │ │ │
│ │ │ Dashboard │ │ Commands │ │ (Future) │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Agent Core Layer │ │
│ │ │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Scheduler │→│ Decision │→│ Action │ │ │
│ │ │ (Timer) │ │ Engine │ │ Executor │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ │ │ │ │ │ │
│ │ ▼ ▼ ▼ │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │ Persistent History (JSON) │ │ │
│ │ │ - All agent actions │ │ │
│ │ │ - Timestamps │ │ │
│ │ │ - Success/failure status │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Integration Layer │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Docker │ │ Alerts │ │ Metrics │ │ │
│ │ │ SDK │ │ (Slack) │ │ (Prometheus)│ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────┐
│ Docker Engine │
│ (Remote/Local) │
└─────────────────────┘

---

## ⚡ Quick Start

### One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/master/install.sh | bash
What Happens Automatically
The installer will:

✅ Clone the repository

✅ Create a Python virtual environment

✅ Install all dependencies

✅ Configure SELinux (if enforcing)

✅ Set up the agent as a systemd service

✅ Open firewall port 7860

✅ Start the web dashboard

🌐 Dashboard
Access the web dashboard at http://<your-ip>:7860:

Container Status: Real-time view of all containers

Action History: Persistent audit log of all actions

Manual Controls: Restart/stop containers manually

📁 Persistent History
All agent actions are logged to /tmp/containerguard_history.json:
[
  {
    "timestamp": "2026-08-24T05:35:57.986681",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  }
]
This file is shared between the agent and dashboard, ensuring consistent history display.
🔧 Systemd Service
The agent runs as a systemd service:
# Check status
sudo systemctl status containerguard

# View logs
sudo journalctl -u containerguard -f

# Stop/Start/Restart
sudo systemctl {stop|start|restart} containerguard
📋 Requirements
Component	Version
OS	AlmaLinux 8+, Ubuntu 20.04+, RHEL 8+
Docker	20.10+
Python	3.9+
CPU	2 cores
RAM	2 GB
🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/amazing)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing)

Open a Pull Request

📄 License
MIT License - see LICENSE for details

📞 Support
Issues: GitHub Issues

Discussions: GitHub Discussions

Built with ❤️ for the Docker community
