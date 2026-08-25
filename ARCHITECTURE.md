# 🏗️ ContainerGuard Architecture

Technical deep dive into ContainerGuard's design, components, and data flow.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Persistent History](#persistent-history)
6. [Decision Engine](#decision-engine)
7. [Security Model](#security-model)
8. [Performance Considerations](#performance-considerations)
9. [Extending ContainerGuard](#extending-containerguard)

---

## Overview

ContainerGuard is a **lightweight, autonomous monitoring agent** designed to run on Linux systems with Docker. It continuously monitors container health and automatically takes corrective actions based on configurable rules.

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Simplicity** | Single binary, minimal dependencies, easy to deploy |
| **Autonomy** | Operates without human intervention |
| **Observability** | Full visibility into agent decisions and actions |
| **Extensibility** | Easy to add new actions and rules |
| **Security** | Runs with least privilege, secure communication |
| **Persistence** | All actions logged to JSON for audit |

---

## High-Level Architecture

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
│ │ │ /tmp/containerguard_history.json │ │ │
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

## Component Breakdown

### 1. Agent Core (`agent/core.py`)

The brain of ContainerGuard. Responsible for:

- **Docker Connection**: Manages connection to Docker daemon
- **Container Discovery**: Lists all containers (running + stopped)
- **Health Monitoring**: Checks container status
- **Action Coordination**: Triggers actions based on decisions

```python
class ContainerGuardAgent:
    def __init__(self, docker_host):
        self.client = docker.DockerClient(base_url=docker_host)
        self.actions = ContainerActions(self.client)
    
    def check_and_heal(self):
        # 1. Get all containers
        # 2. Check each container's status
        # 3. If exited → trigger restart
        # 4. Log the action to JSON
2. Action Executor (agent/actions.py)
Executes actions on containers and logs to persistent JSON:

Action	Description	History Entry
restart_container()	Restarts a stopped/exited container	{"action":"restart","container":"name","status":"success"}
stop_container()	Stops a running container	{"action":"stop","container":"name","status":"success"}
cleanup_exited()	Removes exited containers	{"action":"cleanup","containers":[...]}
3. Persistent History (/tmp/containerguard_history.json)
All actions are logged to a shared JSON file:
[
  {
    "timestamp": "2026-08-24T05:35:57.986681",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  }
]
Why JSON?

✅ Human-readable

✅ Shared between agent and dashboard

✅ Survives service restarts

✅ Easy to parse and extend

4. Continuous Runner (agent/runner.py)
Manages the agent's lifecycle:

Infinite Loop: Runs the agent every N seconds

Graceful Shutdown: Handles SIGINT/SIGTERM

Error Recovery: Continues running even if a cycle fails

Logging: Writes structured logs to file

5. Gradio Dashboard (dashboard/app.py)
Web-based user interface:

Status View: Real-time container status

Action History: Reads from persistent JSON

Manual Controls: Restart/stop containers manually

Auto-Refresh: Updates every 10 seconds

6. Systemd Service (deploy/containerguard.service)
Production deployment:

Auto-Start: Starts on boot

Auto-Restart: Restarts if the agent crashes

Log Rotation: Manages log files

Resource Limits: CPU/memory constraints

Data Flow
Monitoring Cycle
┌─────────────────────────────────────────────────────────────────────────┐
│                       Agent Monitoring Cycle                           │
│                                                                         │
│  1. Timer triggers (every 30 seconds)                                  │
│         ↓                                                               │
│  2. Agent queries Docker API for all containers                        │
│         ↓                                                               │
│  3. For each container:                                                │
│     ├─ If status == "running" → OK                                     │
│     ├─ If status == "exited" → RESTART                                │
│     └─ If status == "paused" → LOG (no action)                        │
│         ↓                                                               │
│  4. Action executor performs restarts                                 │
│         ↓                                                               │
│  5. Action logged to JSON file                                        │
│         ↓                                                               │
│  6. Sleep until next interval                                          │
└─────────────────────────────────────────────────────────────────────────┘
Dashboard Data Flow
┌─────────────────────────────────────────────────────────────────────────┐
│                        Dashboard Data Flow                             │
│                                                                         │
│  Browser → Gradio Server → Agent → Docker API                         │
│     ↑           ↓            ↓        ↓                                │
│     │      Render HTML   Fetch Data  Return Status                     │
│     └──────────┴────────────┴──────────┘                              │
│                                                                         │
│  History Flow:                                                         │
│  Dashboard reads /tmp/containerguard_history.json                     │
│     ↑                                                                  │
│     └── Shared JSON file (agent writes, dashboard reads)              │
│                                                                         │
│  Manual Control Flow:                                                  │
│  Browser → Click Button → Gradio → Agent → Docker API                 │
│     ↑           ↓             ↓         ↓        ↓                    │
│     │      Show Result  Execute   Restart   Return                    │
│     └──────────┴────────────┴──────────┴────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
Persistent History
Why JSON?
Requirement	Solution
Shared between processes	File-based storage
Survives restarts	Written to disk
Human-readable	JSON format
Easy to extend	Append-only structure
History File Format

[
  {
    "timestamp": "2026-08-24T05:35:57.986681",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  },
  {
    "timestamp": "2026-08-24T05:36:28.429983",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  }
]
Adding New Action Types
self.action_history.append({
    'timestamp': datetime.now().isoformat(),
    'action': 'stop',  # New action
    'container': container.name,
    'status': 'success',
    'reason': 'manual_request'  # Additional metadata
})
self._save_history()
Decision Engine
Rule Evaluation Logic
def evaluate_decision(container):
    status = container.status
    name = container.name
    history = get_history(name)
    
    # Rule 1: Exited containers should be restarted
    if status == 'exited':
        if time_since_last_restart(name) > COOLDOWN_SECONDS:
            return 'restart'
    
    # Rule 2: Long-running containers with high CPU (future)
    if status == 'running':
        if cpu_usage(name) > 90 and duration > 5 * 60:
            return 'scale_up'
    
    # Rule 3: Unused images should be cleaned (future)
    if disk_usage() > 80:
        return 'cleanup'
    
    # Default: No action needed
    return None
Action Cooldowns
To prevent action loops, ContainerGuard implements cooldowns:

Action	Cooldown	Purpose
Restart	60 seconds	Prevent restart loops
Cleanup	1 hour	Avoid unnecessary operations
Scaling	5 minutes	Prevent thrashing
Security Model
Authentication & Authorization
Layer	Security Measure
Docker API	Unix socket (local) or TLS (remote)
Dashboard	No auth by default (add nginx proxy for auth)
Systemd	Runs as root or dedicated user
Network	Firewall rules recommended
Remote Docker Security
# Recommended: Use SSH tunnel instead of TCP
export DOCKER_HOST=ssh://user@worker-vm

# Or use TLS certificates
export DOCKER_HOST=tcp://worker-vm:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/certs
SELinux Support
ContainerGuard automatically configures SELinux contexts:
# Context required for Python execution
sudo chcon -R -t bin_t /path/to/containerguard/venv/bin/
sudo semanage fcontext -a -t bin_t "/path/to/containerguard/venv/bin(/.*)?"
sudo restorecon -Rv /path/to/containerguard/venv/bin/
Performance Considerations
Resource Usage
Component	CPU	Memory	Disk
Agent Core	< 1%	~20 MB	N/A
Gradio Dashboard	< 1%	~50 MB	N/A
JSON History	N/A	~5 MB	~10 MB/year
Systemd Service	< 1%	~20 MB	N/A
Scalability
ContainerGuard can monitor:

Single Host: 100+ containers (tested)

Multiple Hosts: 5+ workers (via multiple DOCKER_HOST configs)

Metrics: 1000+ events per day with minimal impact

Optimization Tips
Increase interval if monitoring many containers

Use SSH instead of TCP for remote connections

Rotate logs weekly to prevent disk filling

Manage JSON history - clean up old entries periodically

Extending ContainerGuard
Adding New Actions
Add method to agent/actions.py:
def send_webhook(self, container_name, event):
    """Send a webhook notification"""
    import requests
    webhook_url = os.getenv('WEBHOOK_URL')
    requests.post(webhook_url, json={
        'event': event,
        'container': container_name,
        'timestamp': datetime.now().isoformat()
    })
    # Log to history
    self.action_history.append({
        'timestamp': datetime.now().isoformat(),
        'action': 'webhook',
        'container': container_name,
        'status': 'sent'
    })
    self._save_history()
Call it from agent/core.py:
if action == 'restart':
    self.actions.restart_container(container.id)
    self.actions.send_webhook(container.name, 'restarted')
Adding New Rules
Add rule logic to agent/core.py:
# In check_and_heal()
if status == 'running' and container.cpu_percent > 90:
    logger.warning(f"⚠️ {name}: High CPU detected")
    self.actions.scale_container(container.id, +1)
# In check_and_heal()
if status == 'running' and container.cpu_percent > 90:
    logger.warning(f"⚠️ {name}: High CPU detected")
    self.actions.scale_container(container.id, +1)
# In check_and_heal()
if status == 'running' and container.cpu_percent > 90:
    logger.warning(f"⚠️ {name}: High CPU detected")
    self.actions.scale_container(container.id, +1)
Adding New Alert Channels
Create new alert class in agent/alerts.py:
class DiscordAlert:
    def send(self, message):
        import requests
        webhook = os.getenv('DISCORD_WEBHOOK')
        requests.post(webhook, json={'content': message})
Deployment Topologies
## Worker Node Setup (Remote Docker)

### Enable Docker API on Worker

For remote Docker monitoring, the worker node must expose the Docker API:

```bash
# On worker node (where containers run)
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# Open firewall port
sudo firewall-cmd --add-port=2375/tcp --permanent
sudo firewall-cmd --reload

Connect Agent to Worker
During installation, when prompted:

Docker Configuration:
  1) Local Docker (same machine) - Default
  2) Remote Docker (different machine)
  3) Skip (configure manually later)
Choose option (1-3): 2
Enter remote Docker IP: 192.168.1.100

The agent will then monitor containers on the remote worker node.

Security Note
⚠️ For production: Use TLS certificates or SSH tunneling instead of plain TCP.


---

## 🧪 **Step 5: Verify ARCHITECTURE.md**

```bash
cat ~/containerguard-new/ARCHITECTURE.md | grep -A 15 "Worker Node Setup"



Single Host (Local Docker)
┌─────────────────────────────────────┐
│        Host Machine                 │
│  ┌─────────────────────────────┐   │
│  │  ContainerGuard Agent       │   │
│  │  - Monitors local Docker    │   │
│  │  - Dashboard on port 7860  │   │
│  │  - JSON history in /tmp    │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Docker Engine              │   │
│  │  - Containers               │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
Agent + Worker (Remote Docker)
┌─────────────────────┐     ┌─────────────────────┐
│   Agent VM          │     │   Worker VM         │
│  ┌───────────────┐  │     │  ┌───────────────┐  │
│  │ ContainerGuard │  │     │  │  Docker       │  │
│  │  - Agent       │  │────▶│  │  Engine       │  │
│  │  - Dashboard   │  │     │  │  - Containers │  │
│  │  - JSON history│  │     │  └───────────────┘  │
│  └───────────────┘  │     └─────────────────────┘
└─────────────────────┘
Monitoring & Observability
Logs
Log File	Content	Rotation
/var/log/containerguard.log	All agent logs	Daily
/var/log/containerguard-error.log	Error-only logs	Daily
/tmp/containerguard_history.json	Action history	Manual
Metrics (Planned)

# Prometheus metrics endpoint (future)
containerguard_containers_total{status="running"}
containerguard_containers_total{status="exited"}
containerguard_actions_total{action="restart"}
containerguard_uptime_seconds
Appendix
Environment Variables
Variable	Default	Description
DOCKER_HOST	unix:///var/run/docker.sock	Docker daemon URL
AGENT_INTERVAL	30	Monitoring interval (seconds)
LOG_LEVEL	INFO	Logging level
HISTORY_FILE	/tmp/containerguard_history.json	History file path
History File Location
The history file is stored in /tmp/ to ensure:

✅ Write access for both agent and dashboard

✅ Persistence across service restarts

✅ Easy cleanup (if needed)

Next: API.md - API reference and integration guide
