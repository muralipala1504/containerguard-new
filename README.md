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

## 💎 Pro Features

## 💎 Pro Features

| Feature | Free | Pro |
|---------|------|-----|
| Container monitoring | ✅ Unlimited | ✅ Unlimited |
| Auto-restart | ✅ | ✅ |
| Web dashboard | ✅ | ✅ |
| **Action history** | 7 days | ✅ **Unlimited** |
| **Slack alerts** | ❌ | ✅ |
| **Auto-cleanup** | ❌ | ✅ |
| **Multi-Host** | ❌ | ✅ |
| Email alerts | ❌ | Coming soon |

### Activate Pro

During installation, you'll be prompted to choose between Free and Pro:

```bash
Pro License Configuration:
  1) Free tier (7-day history, no Slack alerts)
  2) Pro tier (Unlimited history + Slack alerts)
Choose option (1-2):
Pro Features Setup
Slack Alerts (Pro)
Create a Slack app and get a webhook URL

Add the webhook to the service:
sudo tee -a /etc/systemd/system/containerguard.service << 'EOF'
Environment="SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
EOF

sudo systemctl daemon-reload
sudo systemctl restart containerguard

Auto-Cleanup (Pro)
Auto-cleanup removes unused Docker images, dangling volumes, and build cache automatically.

# Trigger cleanup manually
python -c "
from agent.actions import ContainerActions
import docker
client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
actions = ContainerActions(client)
result = actions.run_cleanup()
print('Cleanup result:', result)
"

# Trigger cleanup manually
python -c "
from agent.actions import ContainerActions
import docker
client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
actions = ContainerActions(client)
result = actions.run_cleanup()
print('Cleanup result:', result)
"

Multi-Host (Pro)
Monitor multiple Docker hosts from one dashboard:

sudo mkdir -p /etc/containerguard
sudo tee /etc/containerguard/hosts.conf << 'EOF'
{
  "hosts": [
    {"name": "host1", "host": "unix:///var/run/docker.sock"},
    {"name": "host2", "host": "tcp://192.168.1.100:2375"}
  ]
}
EOF

sudo systemctl restart containerguard



---




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

### Remote Docker Monitoring (Two VMs)

If your containers run on a separate VM, set `DOCKER_HOST` in `docker-compose.yml`:

```yaml
environment:
  - DOCKER_HOST=tcp://<worker-ip>:2375

For detailed setup, see INSTALL.md.


---

## 🎯 **What to Tell Me**

After running Step 1, tell me:
- **"INSTALL.md committed and pushed"**

Then we'll update README.md. 🚀


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

## 🔐 Authentication (B2B)

ContainerGuard supports GitHub OAuth for secure multi-user authentication, making it enterprise-ready.

### Setup GitHub OAuth

1. Create a GitHub OAuth app at https://github.com/settings/applications/new
2. Set **Authorization callback URL** to `http://your-ip:7861/oauth2/callback`
3. Configure environment variables:

```bash
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
Restart the auth server:
python auth.py
Access
Auth Server: http://your-ip:7861

Dashboard: http://your-ip:7860 (after login)
📜 Audit Logs
All user actions are automatically logged for compliance and debugging.

What's Logged
User login/logout

Container restarts (manual + auto-heal)

Configuration changes

Export actions

Log Location
Audit logs are stored at /tmp/containerguard_audit.json:
{
  "timestamp": "2026-09-08T03:53:36.239894",
  "user": "user",
  "action": "restart",
  "resource": "test-nginx",
  "status": "success"
}
Export
Export audit logs from the dashboard:

CSV: Download as comma-separated values

JSON: Download as JSON format

💎 B2B Features
Feature	Description
Authentication	GitHub OAuth login
Audit Logs	Full audit trail of user actions
Export	CSV/JSON export for compliance
Multi-Host	Monitor multiple Docker hosts
Auto-Heal	Automatic container recovery
Slack Alerts	Real-time notifications (Pro)
Auto-Cleanup	Automated disk space management (Pro)

---

## 📝 **Step 2: Update INSTALL.md**

```bash
cat >> /home/ruser/containerguard-new/INSTALL.md << 'EOF'

## 🔐 GitHub OAuth Setup (B2B)

### Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/applications/new
2. **Application name**: `ContainerGuard`
3. **Homepage URL**: `http://your-ip:7861`
4. **Authorization callback URL**: `http://your-ip:7861/oauth2/callback`
5. Click **"Register application"**
6. Copy **Client ID** and **Client Secret**

### Step 2: Configure Environment

```bash
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
Step 3: Start Auth Server
cd /home/ruser/containerguard-new
source venv/bin/activate
python auth.py
Step 4: Access
Login: http://your-ip:7861

Dashboard: http://your-ip:7860 (after login)
📜 Audit Logs
Audit logs track all user actions for compliance.

Log Location
/tmp/containerguard_audit.json
Export
Export logs as CSV or JSON from the dashboard.

View Logs
cat /tmp/containerguard_audit.json | jq
🔧 Troubleshooting (B2B)
Auth Server Not Running
cd /home/ruser/containerguard-new
source venv/bin/activate
python auth.py
Audit Logs Not Showing
# Check if audit file exists
ls -la /tmp/containerguard_audit.json

# Trigger an action (restart a container)
# Then check the file
cat /tmp/containerguard_audit.json
