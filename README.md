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

## 🐳 Docker Quick Start

```bash
# Clone and run
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new
docker compose up -d

# Check status
docker compose ps

# Access dashboard
http://localhost:7860

Docker vs VM Installation
Method	Command	Best For
VM (install.sh)	curl ... | bash	Production VMs, systemd integration
Docker	docker compose up -d	Container environments, quick testing


---

## 🔧 **Step 2: Update INSTALL.md**

Add a new section after the manual installation:

```markdown
## 🐳 Docker Installation

### Prerequisites
- Docker Engine 20.10+
- Docker Compose (or Docker with compose plugin)

### Steps

```bash
# Clone the repository
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new

# Start the services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

Configuration
Set environment variables in docker-compose.yml:

environment:
  - DOCKER_HOST=unix:///var/run/docker.sock  # Local Docker
  - AGENT_INTERVAL=30
  - LOG_LEVEL=INFO


---

## 🔧 **Step 3: Update ARCHITECTURE.md**

Add a Docker architecture section:

```markdown
## 🐳 Docker Architecture


┌─────────────────────────────────────────────────────────────────┐
│ Docker Compose Setup │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ containerguard-agent (container) │ │
│ │ - Monitors Docker via mounted socket │ │
│ │ - Auto-restarts exited containers │ │
│ └─────────────────────────────────────────────────────────┘ │
│ │ │
│ ▼ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ containerguard-dashboard (container) │ │
│ │ - Gradio web UI on port 7860 │ │
│ │ - Reads shared history file │ │
│ └─────────────────────────────────────────────────────────┘ │
│ │ │
│ ▼ │
│ /var/run/docker.sock │
│ │ │
│ ▼ │
│ Docker Engine (host) │
└─────────────────────────────────────────────────────────────────┘




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
