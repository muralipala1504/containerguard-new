# 🏗️ ContainerGuard Architecture

Technical deep dive into ContainerGuard's design, components, and data flow.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Decision Engine](#decision-engine)
6. [Security Model](#security-model)
7. [Performance Considerations](#performance-considerations)
8. [Extending ContainerGuard](#extending-containerguard)

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

---

## High-Level Architecture

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
│ │ │ State Store (SQLite) │ │ │
│ │ │ - Container status history │ │ │
│ │ │ - Action logs │ │ │
│ │ │ - Agent configuration │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Integration Layer │ │
│ │ │ │
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
        # 4. Log the action
2. Action Executor (agent/actions.py)
Executes actions on containers:

Action	Description
restart_container()	Restarts a stopped/exited container
stop_container()	Stops a running container
remove_container()	Removes a container permanently
cleanup_images()	Removes unused Docker images
cleanup_volumes()	Removes unused volumes
3. Continuous Runner (agent/runner.py)
Manages the agent's lifecycle:

Infinite Loop: Runs the agent every N seconds

Graceful Shutdown: Handles SIGINT/SIGTERM

Error Recovery: Continues running even if a cycle fails

Logging: Writes structured logs to file

4. Gradio Dashboard (dashboard/app.py)
Web-based user interface:

Status View: Real-time container status

Action History: Timeline of agent actions

Manual Controls: Restart/stop containers manually

Auto-Refresh: Updates every 10 seconds

5. Systemd Service (deploy/containerguard.service)
Production deployment:

Auto-Start: Starts on boot

Auto-Restart: Restarts if the agent crashes

Log Rotation: Manages log files

Resource Limits: CPU/memory constraints

Data Flow
Monitoring Cycle
┌─────────────────────────────────────────────────────────────┐
│                    Agent Monitoring Cycle                   │
│                                                             │
│  1. Timer triggers (every 30 seconds)                      │
│         ↓                                                   │
│  2. Agent queries Docker API for all containers            │
│         ↓                                                   │
│  3. For each container:                                    │
│     ├─ If status == "running" → OK                         │
│     ├─ If status == "exited" → RESTART                    │
│     └─ If status == "paused" → LOG (no action)            │
│         ↓                                                   │
│  4. Action executor performs restarts                     │
│         ↓                                                   │
│  5. Action logged to SQLite + log file                    │
│         ↓                                                   │
│  6. Sleep until next interval                              │
└─────────────────────────────────────────────────────────────┘
Dashboard Data Flow
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard Data Flow                      │
│                                                             │
│  Browser → Gradio Server → Agent → Docker API             │
│     ↑           ↓            ↓        ↓                    │
│     │      Render HTML   Fetch Data  Return Status         │
│     └──────────┴────────────┴──────────┘                   │
│                                                             │
│  Manual Control Flow:                                      │
│  Browser → Click Button → Gradio → Agent → Docker API     │
│     ↑           ↓             ↓         ↓        ↓         │
│     │      Show Result  Execute   Restart   Return        │
│     └──────────┴────────────┴──────────┴────────┘         │
└─────────────────────────────────────────────────────────────┘
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
    
    # Rule 2: Long-running containers with high CPU
    if status == 'running':
        if cpu_usage(name) > 90 and duration > 5 * 60:
            return 'scale_up'
    
    # Rule 3: Unused images should be cleaned
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
ContainerGuard is tested on SELinux-enforcing systems:
# Context required for Python execution
sudo chcon -R -t bin_t /path/to/containerguard/venv/bin/
sudo semanage fcontext -a -t bin_t "/path/to/containerguard/venv/bin(/.*)?"
sudo restorecon -Rv /path/to/containerguard/venv/bin/
Performance Considerations
Resource Usage
Component	CPU	Memory	Disk
Agent Core	< 1%	~20 MB	N/A
Gradio Dashboard	< 1%	~50 MB	N/A
SQLite	N/A	~5 MB	~10 MB/year
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

Use SQLite WAL mode for better concurrency

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
Adding New Alert Channels
Create new alert class in agent/alerts.py:
class DiscordAlert:
    def send(self, message):
        import requests
        webhook = os.getenv('DISCORD_WEBHOOK')
        requests.post(webhook, json={'content': message})
Deployment Topologies
Single Host (Local Docker)
┌─────────────────────────────────────┐
│        Host Machine                 │
│  ┌─────────────────────────────┐   │
│  │  ContainerGuard Agent       │   │
│  │  - Monitors local Docker    │   │
│  │  - Dashboard on port 7860  │   │
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
│  └───────────────┘  │     │  └───────────────┘  │
└─────────────────────┘     └─────────────────────┘
Multi-Worker (Enterprise)
┌─────────────────────┐
│   Agent VM          │
│  ┌───────────────┐  │
│  │ ContainerGuard │  │
│  │  - Agent       │  │
│  │  - Dashboard   │  │
│  └───────────────┘  │
└─────────┬───────────┘
          │
    ┌─────┴─────┬─────────┐
    ▼           ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│Worker1 │ │Worker2 │ │Worker3 │
│Docker  │ │Docker  │ │Docker  │
└────────┘ └────────┘ └────────┘
Development Roadmap
Phase 1: Core Agent (✅ Done)
☑ Docker connection
☑ Container discovery
☑ Health monitoring
☑ Auto-restart
Phase 2: Production Ready (✅ Done)
☑ Systemd service
☑ Logging
☑ SELinux support
☑ Error handling
Phase 3: UI & Visibility (✅ Done)
☑ Gradio dashboard
☑ Action history
☑ Manual controls
Phase 4: Advanced Features (🚧 Planned)
□ Alerting (Slack/Discord)
□ Prometheus metrics
□ Auto-scaling
□ Image auto-update
□ Multi-host support
Monitoring & Observability
Logs
Log File	Content	Rotation
/var/log/containerguard.log	All agent logs	Daily
/var/log/containerguard-error.log	Error-only logs	Daily
Metrics (Planned)

# Prometheus metrics endpoint (future)
containerguard_containers_total{status="running"}
containerguard_containers_total{status="exited"}
containerguard_actions_total{action="restart"}
containerguard_uptime_seconds
Contributing
Development Environment
# Clone
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black agent/ dashboard/

# Lint
flake8 agent/ dashboard/
Code Standards
Python: PEP 8

Documentation: Google style docstrings

Commits: Conventional commits

Testing: Unit tests for core logic

Appendix
Docker API Reference
Endpoint	Method	Description
/containers/json	GET	List containers
/containers/{id}/start	POST	Start container
/containers/{id}/restart	POST	Restart container
/containers/{id}/stop	POST	Stop container
/system/df	GET	Disk usage
Environment Variables
Variable	Default	Description
DOCKER_HOST	unix:///var/run/docker.sock	Docker daemon URL
AGENT_INTERVAL	30	Monitoring interval (seconds)
LOG_LEVEL	INFO	Logging level
SQLITE_PATH	containerguard.db	Database location
Next: API.md - API reference and integration guide
