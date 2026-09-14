# 🔌 ContainerGuard API Reference

Complete API documentation for ContainerGuard (Free tier) internal interfaces, persistent history, and extensibility points.

> **💎 Need Multi-Host or Slack API?** Those are Pro features. See [Upgrade to Pro](#-upgrade-to-containerGuard-pro) at the end.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agent API](#agent-api)
3. [Container Actions API](#container-actions-api)
4. [Dashboard API](#dashboard-api)
5. [Persistent History API](#persistent-history-api)
6. [Audit Log API](#audit-log-api)
7. [Error Codes](#error-codes)
8. [Examples](#examples)

---

## Overview

ContainerGuard provides several interfaces for integration:

| Interface | Purpose | Protocol |
|-----------|---------|----------|
| **Agent Core** | Monitoring and actions | Python API |
| **Container Actions** | Docker container management | Python API |
| **Dashboard** | Web UI | HTTP (Gradio) |
| **Persistent History** | Action logging | JSON file |

---

## Agent API

### ContainerGuardAgent Class

```python
class ContainerGuardAgent:
    def __init__(self, docker_host='unix:///var/run/docker.sock'):
        """
        Initialize the agent with a Docker host.

        Args:
            docker_host (str): Docker daemon URL
                - Local: 'unix:///var/run/docker.sock'
                - Remote: 'tcp://host:2375'  (Pro feature)
        """
        pass

    def get_all_containers(self) -> list:
        """
        Get all containers (including stopped).

        Returns:
            list: List of Docker container objects
        """
        pass

    def check_and_heal(self) -> tuple:
        """
        Check container health and heal if needed.

        Returns:
            tuple: (status_report, restarted_count)
                - status_report: list of dicts with 'name' and 'status'
                - restarted_count: number of containers restarted
        """
        pass

    def run_once(self) -> list:
        """
        Run a single monitoring cycle.

        Returns:
            list: Container status reports
        """
        pass
```

### Usage Example

```python
from agent.core import ContainerGuardAgent

# Initialize agent (local Docker)
agent = ContainerGuardAgent('unix:///var/run/docker.sock')

# Run a monitoring cycle
results = agent.run_once()

# Output container status
for container in results:
    print(f"{container['name']}: {container['status']}")
```

---

## Container Actions API

### ContainerActions Class

```python
from agent.actions import ContainerActions
import docker

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
actions = ContainerActions(client)
```

### Methods

#### restart_container()

```python
def restart_container(self, container_id: str) -> bool:
    """
    Restart a container.

    Args:
        container_id (str): Container ID or name

    Returns:
        bool: True if successful, False otherwise
    """
```

#### stop_container()

```python
def stop_container(self, container_id: str) -> bool:
    """
    Stop a running container.

    Args:
        container_id (str): Container ID or name

    Returns:
        bool: True if successful, False otherwise
    """
```

#### get_history()

```python
def get_history(self) -> list:
    """
    Get action history from JSON file.

    Returns:
        list: List of action dicts with timestamp, action, container, status
    """
```

### Usage Example

```python
from agent.actions import ContainerActions
import docker

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
actions = ContainerActions(client)

# Restart a container
if actions.restart_container('test-nginx'):
    print("✅ Container restarted successfully")
else:
    print("❌ Failed to restart container")

# Get action history
history = actions.get_history()
for action in history[-5:]:
    print(f"{action['timestamp']}: {action['action']} {action['container']}")
```

---

## Dashboard API

### Gradio Endpoints

The dashboard exposes the following functions internally:

#### refresh()

```python
def refresh():
    """
    Fetch latest container status and action history from JSON.

    Returns:
        tuple: (status_text, history_text)
            - status_text: Markdown formatted container list
            - history_text: Markdown formatted recent actions
    """
    pass
```

#### restart_container()

```python
def restart_container(name: str) -> str:
    """
    Manually restart a container.

    Args:
        name (str): Name of container to restart

    Returns:
        str: Success/failure message
    """
    pass
```

#### export_json() / export_csv()

```python
def export_json() -> str:
    """Export audit logs as JSON."""

def export_csv() -> str:
    """Export audit logs as CSV."""
```

### HTTP Interface (Gradio)

```bash
# Access the dashboard
GET http://<agent-ip>:7860/

# Components are served via:
# - / (main page)
# - /gradio/ (Gradio static assets)
# - /api/ (Gradio API endpoints)
```

---

## Persistent History API

### History File Location

```bash
/tmp/containerguard_history.json
```

### File Format

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

> **Note:** Free tier retains 7 days of history. Pro tier retains unlimited.

### Reading History

```python
import json

def get_history():
    """Read history from JSON file"""
    try:
        with open('/tmp/containerguard_history.json', 'r') as f:
            return json.load(f)
    except:
        return []
```

### Writing History

```python
import json
from datetime import datetime

def add_action(action_type, container_name, status):
    """Add an action to history"""
    history = get_history()
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action_type,
        'container': container_name,
        'status': status
    }
    history.append(entry)
    with open('/tmp/containerguard_history.json', 'w') as f:
        json.dump(history, f, indent=2)
```

### Action Types

| Action | Description |
|--------|-------------|
| `restart` | Container restarted |
| `stop` | Container stopped (manual) |
| `error` | An error occurred |

---

## Audit Log API

### Audit File Location

```bash
/tmp/containerguard_audit.json
```

### File Format

```json
[
  {
    "timestamp": "2026-09-14T07:18:44.566260",
    "user": "system",
    "action": "auto-heal",
    "resource": "test-nginx",
    "details": "Container auto-restarted",
    "status": "success"
  }
]
```

### API Functions

```python
from audit import log_action, get_audit_logs, export_audit_logs_json, export_audit_logs_csv

# Log an action
log_action(
    user="user",
    action="restart",
    resource="test-nginx",
    details="Manual restart from dashboard",
    status="success"
)

# Get recent logs
logs = get_audit_logs(limit=10)
for log in logs:
    print(f"{log['timestamp']} - {log['user']} - {log['action']} {log['resource']}")

# Export as JSON
json_output = export_audit_logs_json()

# Export as CSV
csv_output = export_audit_logs_csv()
```

### CSV Format

```
Timestamp,User,Action,Resource,Status,Details
2026-09-14T07:18:44.566260,test-user,restart,test-nginx,success,Manual test action
```

---

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `E001` | Docker connection failed | Check `DOCKER_HOST` and network |
| `E002` | Container not found | Verify container name/ID |
| `E003` | Permission denied | Check SELinux/file permissions |
| `E004` | Action cooldown active | Wait for cooldown to expire |
| `E005` | JSON history read/write error | Check `/tmp` permissions |
| `E006` | Configuration error | Validate JSON syntax |

---

## Examples

### Example 1: Basic Monitoring

```python
from agent.core import ContainerGuardAgent

# Initialize agent
agent = ContainerGuardAgent('unix:///var/run/docker.sock')

# Run a monitoring cycle
results = agent.run_once()

# Print results
for r in results:
    print(f"Container: {r['name']}")
    print(f"Status: {r['status']}")
    print("---")
```

### Example 2: Reading Audit Logs

```python
from audit import get_audit_logs

# Get last 10 actions
logs = get_audit_logs(10)
for log in logs:
    print(f"{log['timestamp']}: {log['user']} - {log['action']} {log['resource']}")
```

### Example 3: Manual Container Management

```python
from agent.actions import ContainerActions
import docker

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
actions = ContainerActions(client)

# Restart a container
if actions.restart_container('test-postgres'):
    print("✅ Container restarted successfully")
else:
    print("❌ Failed to restart container")
```

### Example 4: Custom Rule Extension

```python
from agent.core import ContainerGuardAgent

class CustomAgent(ContainerGuardAgent):
    def check_and_heal(self):
        """Custom monitoring logic"""
        containers = self.get_all_containers()
        restarted_count = 0

        for container in containers:
            status = container.status

            # Custom rule: Restart containers running > 24h
            if status == 'running':
                uptime = container.attrs['State']['StartedAt']
                if uptime > 24 * 60 * 60:  # 24 hours
                    self.actions.restart_container(container.id)
                    restarted_count += 1

            # Standard auto-heal for exited containers
            elif status == 'exited':
                self.actions.restart_container(container.id)
                restarted_count += 1

        return restarted_count
```

---

## Integration Patterns

### Pattern 1: Agent as a Library

```python
# embed.py
from agent.core import ContainerGuardAgent
import time

def my_application():
    agent = ContainerGuardAgent()
    while True:
        results = agent.run_once()
        process_results(results)
        time.sleep(60)
```

### Pattern 2: Agent as a Service

```bash
# Using systemd
sudo systemctl start containerguard
sudo systemctl status containerguard
sudo journalctl -u containerguard -f
```

### Pattern 3: Reading Audit Logs from External Script

```python
# monitor_audit.py
import json
import time

def tail_audit():
    """Continuously monitor audit file"""
    last_count = 0
    while True:
        try:
            with open('/tmp/containerguard_audit.json', 'r') as f:
                audit = json.load(f)
            if len(audit) > last_count:
                new_actions = audit[last_count:]
                for action in new_actions:
                    print(f"New action: {action}")
                last_count = len(audit)
        except:
            pass
        time.sleep(5)

if __name__ == "__main__":
    tail_audit()
```

---

## 💎 Upgrade to ContainerGuard Pro

The Pro version extends this API with:

| Pro API | Description |
|---------|-------------|
| **Multi-Host Agent** | Connect to remote Docker hosts via `hosts.conf` |
| **SlackAlert Class** | Send formatted alerts to Slack |
| **AutoCleanup Class** | Automated image/volume cleanup |
| **License API** | `check_license()` for Pro gating |
| **GitHub OAuth** | Enterprise authentication |

### 🔓 Get Pro Access

- 📧 Contact: **muralipala15@gmail.com**
- 📝 Include your GitHub username

---

## 📚 Related Documentation

- **README.md** — Project overview
- **INSTALL.md** — Installation guide
- **ARCHITECTURE.md** — Technical architecture

---

## 🤝 Contributing

If you'd like to extend the API, please:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write tests
5. Submit a Pull Request

---

**Built with ❤️ for the Docker community**
