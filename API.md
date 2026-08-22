# 🔌 ContainerGuard API Reference

Complete API documentation for ContainerGuard's internal interfaces, webhook integration, and extensibility points.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agent API](#agent-api)
3. [Dashboard API](#dashboard-api)
4. [Webhook Integration](#webhook-integration)
5. [Configuration API](#configuration-api)
6. [Database Schema](#database-schema)
7. [Error Codes](#error-codes)
8. [Examples](#examples)

---

## Overview

ContainerGuard provides several interfaces for integration:

| Interface | Purpose | Protocol |
|-----------|---------|----------|
| **Agent Core** | Monitoring and actions | Python API |
| **Dashboard** | Web UI | HTTP (Gradio) |
| **Webhooks** | Alerts/Notifications | HTTP (Future) |
| **Configuration** | User settings | YAML/JSON |

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
                - Remote: 'tcp://host:2375'
                - SSH: 'ssh://user@host'
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
ContainerActions Class
class ContainerActions:
    def __init__(self, docker_client):
        """Initialize actions with a Docker client."""
        pass
    
    def restart_container(self, container_id: str) -> bool:
        """
        Restart an exited container.
        
        Args:
            container_id (str): Container ID or name
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def stop_container(self, container_id: str) -> bool:
        """
        Stop a running container.
        
        Args:
            container_id (str): Container ID or name
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def get_history(self) -> list:
        """
        Get action history.
        
        Returns:
            list: List of action dicts with timestamp, action, container, status
        """
        pass
Usage Example
from agent.core import ContainerGuardAgent

# Initialize agent
agent = ContainerGuardAgent('tcp://192.168.1.100:2375')

# Run a monitoring cycle
results = agent.run_once()

# Output container status
for container in results:
    print(f"{container['name']}: {container['status']}")

# Check action history
history = agent.actions.get_history()
for action in history:
    print(f"{action['timestamp']}: {action['action']} {action['container']}")
Dashboard API
Gradio Endpoints
The dashboard exposes the following functions internally:

Refresh Status
def refresh_dashboard():
    """
    Fetch latest container status and action history.
    
    Returns:
        tuple: (status_text, history_text)
            - status_text: Markdown formatted container list
            - history_text: Markdown formatted action history
    """
    pass
Manual Controls
def restart_container(container_name: str) -> str:
    """
    Manually restart a container.
    
    Args:
        container_name (str): Name of container to restart
        
    Returns:
        str: Success/failure message
    """
    pass

def stop_container(container_name: str) -> str:
    """
    Manually stop a container.
    
    Args:
        container_name (str): Name of container to stop
        
    Returns:
        str: Success/failure message
    """
    pass
HTTP Interface (Gradio)
The dashboard uses Gradio's built-in HTTP server:
# Access the dashboard
GET http://<agent-ip>:7860/

# Components are served via:
# - / (main page)
# - /gradio/ (Gradio static assets)
# - /api/ (Gradio API endpoints)
REST API (Planned)
Future REST API endpoints:

Endpoint	Method	Description
/api/containers	GET	List all containers
/api/containers/{name}	GET	Get container status
/api/containers/{name}/restart	POST	Restart container
/api/containers/{name}/stop	POST	Stop container
/api/history	GET	Get action history
/api/health	GET	Agent health check
Webhook Integration
Slack Webhooks (Future)
Configuration:
# config.yaml
alerts:
  slack:
    webhook_url: "https://hooks.slack.com/services/XXX/YYY/ZZZ"
    channel: "#alerts"
    username: "ContainerGuard"
Message Format:
{
    "text": "🚨 Container Restart Alert",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Container:* `test-postgres`\n*Action:* Restarted\n*Time:* 2026-08-22 05:48:16"
            }
        }
    ]
}
Discord Webhooks (Future)
Configuration:
# config.yaml
alerts:
  discord:
    webhook_url: "https://discord.com/api/webhooks/XXX/YYY"
    username: "ContainerGuard"
Message Format:
{
    "content": "🚨 Container Restart Alert",
    "embeds": [
        {
            "title": "Action Performed",
            "fields": [
                {"name": "Container", "value": "test-postgres"},
                {"name": "Action", "value": "Restarted"},
                {"name": "Time", "value": "2026-08-22 05:48:16"}
            ],
            "color": 16711680
        }
    ]
}
Custom Webhook (Future)
Configuration:
# config.yaml
alerts:
  webhook:
    url: "https://my-api.example.com/events"
    headers:
      Authorization: "Bearer XXX"
    format: "json"
Payload Format:
{
    "event": "container_restart",
    "timestamp": "2026-08-22T05:48:16Z",
    "container": {
        "name": "test-postgres",
        "status": "running",
        "image": "postgres:latest"
    },
    "agent": {
        "version": "1.0.0",
        "host": "vm1-agent"
    }
}
Configuration API
YAML Configuration (Planned)
config.yaml:
# Global settings
agent:
  interval: 30  # seconds between checks
  cooldown: 60  # seconds between restarts
  log_level: INFO

# Docker connection
docker:
  host: tcp://192.168.217.163:2375
  tls_verify: false
  cert_path: /path/to/certs

# Rules
rules:
  - name: "Restart exited containers"
    condition: "status == 'exited'"
    action: "restart"
    cooldown: 60

  - name: "Cleanup unused images"
    condition: "disk_usage > 80%"
    action: "cleanup"
    schedule: "daily"

# Alerts
alerts:
  slack:
    webhook_url: "https://hooks.slack.com/services/XXX/YYY/ZZZ"
    channel: "#alerts"
    events: ["restart", "cleanup", "error"]

  discord:
    webhook_url: "https://discord.com/api/webhooks/XXX/YYY"
    events: ["restart", "cleanup"]
Loading Configuration
import yaml

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

# Usage
config = load_config()
interval = config['agent']['interval']
docker_host = config['docker']['host']
Database Schema
SQLite Tables
Action History Table:
CREATE TABLE action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,  -- restart, stop, cleanup
    container TEXT NOT NULL,
    status TEXT NOT NULL,  -- success, failed
    error TEXT DEFAULT NULL
);
Container Status Table (Planned):
CREATE TABLE container_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,  -- running, exited, paused
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    restart_count INTEGER DEFAULT 0,
    last_restart TIMESTAMP
);
Accessing the Database
import sqlite3

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('containerguard.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_recent_actions(limit=10):
    """Get recent actions from history"""
    conn = get_db_connection()
    cursor = conn.execute(
        'SELECT * FROM action_history ORDER BY timestamp DESC LIMIT ?',
        (limit,)
    )
    return cursor.fetchall()
Error Codes
Code	Description	Resolution
E001	Docker connection failed	Check DOCKER_HOST and network
E002	Container not found	Verify container name/ID
E003	Permission denied	Check SELinux/file permissions
E004	Action cooldown active	Wait for cooldown to expire
E005	Configuration error	Validate YAML/JSON syntax
E006	Database error	Check SQLite permissions
E007	Webhook failed	Check webhook URL and network
Examples
Example 1: Basic Monitoring
from agent.core import ContainerGuardAgent

# Initialize agent
agent = ContainerGuardAgent('tcp://192.168.217.163:2375')

# Run a monitoring cycle
results = agent.run_once()

# Print results
for r in results:
    print(f"Container: {r['name']}")
    print(f"Status: {r['status']}")
    print("---")
Example 2: Action History
from agent.actions import ContainerActions
import docker

# Connect to Docker
client = docker.DockerClient(base_url='tcp://192.168.217.163:2375')
actions = ContainerActions(client)

# Get action history
history = actions.get_history()

# Print last 5 actions
for action in history[-5:]:
    print(f"{action['timestamp']}: {action['action']} {action['container']}")
    print(f"  Status: {action['status']}")
Example 3: Manual Container Management
from agent.actions import ContainerActions
import docker

client = docker.DockerClient(base_url='tcp://192.168.217.163:2375')
actions = ContainerActions(client)

# Restart a container
if actions.restart_container('test-postgres'):
    print("✅ Container restarted successfully")
else:
    print("❌ Failed to restart container")

# Stop a container
if actions.stop_container('test-nginx'):
    print("✅ Container stopped successfully")
else:
    print("❌ Failed to stop container")
Example 4: Custom Webhook Integration
import requests
from agent.core import ContainerGuardAgent

agent = ContainerGuardAgent('tcp://192.168.217.163:2375')

def send_event(event_data):
    """Send event to external API"""
    webhook_url = 'https://my-api.example.com/events'
    requests.post(webhook_url, json=event_data)

# Run monitoring cycle
results = agent.run_once()

# Send events for exited containers
for r in results:
    if r['status'] == 'exited':
        send_event({
            'event': 'container_exited',
            'container': r['name'],
            'timestamp': datetime.now().isoformat()
        })
Example 5: Custom Rule Extension
from agent.core import ContainerGuardAgent

class CustomAgent(ContainerGuardAgent):
    def check_and_heal(self):
        """Custom monitoring logic"""
        containers = self.get_all_containers()
        restarted_count = 0
        
        for container in containers:
            status = container.status
            name = container.name
            
            # Custom rule: Restart containers that have been running > 24h
            if status == 'running':
                # Check uptime
                uptime = container.attrs['State']['StartedAt']
                if uptime > 24 * 60 * 60:  # 24 hours
                    self.actions.restart_container(container.id)
                    restarted_count += 1
            
            # Standard auto-heal for exited containers
            elif status == 'exited':
                self.actions.restart_container(container.id)
                restarted_count += 1
        
        return restarted_count
Integration Patterns
Pattern 1: Agent as a Library
# embed.py
from agent.core import ContainerGuardAgent

def my_application():
    # Initialize agent
    agent = ContainerGuardAgent()
    
    # Use agent for monitoring
    while True:
        results = agent.run_once()
        # Custom processing
        process_results(results)
        time.sleep(60)
Pattern 2: Agent as a Service
# Using systemd
sudo systemctl start containerguard
sudo systemctl status containerguard
sudo journalctl -u containerguard -f
Pattern 3: Agent in a Container
# Dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "agent/runner.py"]
# Build and run
docker build -t containerguard .
docker run -d --name containerguard \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containerguard
Future API Extensions
Prometheus Exporter
# prometheus.yml
scrape_configs:
  - job_name: 'containerguard'
    static_configs:
      - targets: ['localhost:8000']
RESTful API
GET    /api/v1/containers          # List all containers
GET    /api/v1/containers/{id}     # Get container details
POST   /api/v1/containers/{id}/restart
POST   /api/v1/containers/{id}/stop
GET    /api/v1/history             # Get action history
GET    /api/v1/health              # Health check
GraphQL API (Planned)
query {
    containers {
        name
        status
        image
        uptime
        restartCount
    }
    history(limit: 10) {
        timestamp
        action
        container
        status
    }
}
Testing
# test_api.py
import unittest
from agent.core import ContainerGuardAgent

class TestAgentAPI(unittest.TestCase):
    def setUp(self):
        self.agent = ContainerGuardAgent('tcp://192.168.217.163:2375')
    
    def test_get_containers(self):
        containers = self.agent.get_all_containers()
        self.assertGreater(len(containers), 0)
    
    def test_check_and_heal(self):
        results, count = self.agent.check_and_heal()
        self.assertIsInstance(results, list)
        self.assertIsInstance(count, int)
📚 Related Documentation
README.md - Project overview

INSTALL.md - Installation guide

ARCHITECTURE.md - Technical architecture
🤝 Contributing
If you'd like to extend the API, please:

Fork the repository

Create a feature branch

Add your changes

Write tests

Submit a pull request

📄 License
MIT License - see LICENSE for details
