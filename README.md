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
| 🔔 **Alerts** | Sends notifications via Slack, Discord, or Email |
| 📊 **Dashboard** | Web UI to view status and action history |
| ⚙️ **Configurable** | YAML-based rules and scheduling |
| 🐳 **Docker Native** | Works with Docker and Docker Compose |

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────────┐
│ ContainerGuard │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Agent │ │ Dashboard │ │ Alerts │ │
│ │ (Core) │ │ (Gradio) │ │ (Slack) │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Docker API Client │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────┐
│ Docker Engine │
│ (Remote/Local) │
└─────────────────────┘

---

## ⚡ Quick Start

### Prerequisites
- Linux (AlmaLinux 8/9, Ubuntu 20.04+, RHEL)
- Docker Engine 20.10+
- Python 3.9+
- 2 CPU, 4GB RAM (minimum)

### One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/main/install.sh | bash
Manual Installation
# Clone the repository
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Docker host (if remote)
export DOCKER_HOST=tcp://your-docker-host:2375

# Test the agent
python agent/core.py

# Start the agent as a service
sudo cp deploy/containerguard.service /etc/systemd/system/
sudo systemctl enable --now containerguard

# Start the dashboard
python dashboard/app.py
# Open http://your-server-ip:7860
📊 Dashboard Preview
Access the web dashboard at http://your-server-ip:7860:

Container Status - Real-time view of all containers

Action History - Audit log of all automated actions

Manual Controls - Restart/stop containers manually

Live Updates - Auto-refresh every 10 seconds

🔧 Configuration
Environment Variables
Variable	Description	Default
DOCKER_HOST	Docker daemon URL	unix:///var/run/docker.sock
AGENT_INTERVAL	Check interval (seconds)	30
LOG_LEVEL	Logging level	INFO
SLACK_WEBHOOK	Slack alert webhook	""
Agent Rules (YAML)
rules:
  - name: "Restart exited containers"
    condition: "status == 'exited'"
    action: "restart"
    cooldown: 60  # seconds between restarts

  - name: "Cleanup unused images"
    condition: "disk_usage > 80%"
    action: "cleanup"
    schedule: "daily"
rules:
  - name: "Restart exited containers"
    condition: "status == 'exited'"
    action: "restart"
    cooldown: 60  # seconds between restarts

  - name: "Cleanup unused images"
    condition: "disk_usage > 80%"
    action: "cleanup"
    schedule: "daily"
# Check status
sudo systemctl status containerguard

# View logs
sudo journalctl -u containerguard -f

# Stop/Start/Restart
sudo systemctl {stop|start|restart} containerguard
Log Files
/var/log/containerguard.log - Agent logs

/var/log/containerguard-error.log - Error logs
Log Files
/var/log/containerguard.log - Agent logs

/var/log/containerguard-error.log - Error logs
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Support
Issues: GitHub Issues

Discussions: GitHub Discussions

Email: muralipala1504@gmail.com
Built with ❤️ for the Docker community
