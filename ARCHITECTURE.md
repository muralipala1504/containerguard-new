# 🏗️ ContainerGuard Architecture

Technical design and data flow documentation for ContainerGuard (Free tier).

> **💎 Looking for Multi-Host architecture?** That's a Pro feature. See [Upgrade to Pro](#-upgrade-to-containerGuard-pro) at the end.

---

## 📋 Overview

ContainerGuard is a lightweight, autonomous Docker monitoring and healing agent built with Python. It runs as two systemd services on a single host:

| Service | Purpose |
|---------|---------|
| `containerguard` | Monitors Docker containers, auto-heals exited ones |
| `containerguard-dashboard` | Gradio web UI for monitoring and control |

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ContainerGuard System                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    User Interface Layer                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │   │
│  │  │   Gradio        │  │   CLI Commands  │  │   REST API      │ │   │
│  │  │   Dashboard     │  │   (Manual)      │  │   (Future)      │ │   │
│  │  │   Port: 7860    │  │                 │  │                 │ │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Agent Core Layer                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │  Scheduler  │→ │  Decision   │→ │  Action     │            │   │
│  │  │  (30s)      │  │  Engine     │  │  Executor   │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │           Persistent History (JSON)                     │   │   │
│  │  │  /tmp/containerguard_history.json                       │   │   │
│  │  │  (7-day retention in Free tier)                         │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Integration Layer                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │   Docker    │  │   Systemd   │  │   Alerts    │            │   │
│  │  │   SDK       │  │   Service   │  │  (Slack -   │            │   │
│  │  │ (Local)     │  │   (Daemon)  │  │   Pro only) │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │   Local Docker Engine       │
                    │   (unix:///var/run/docker)  │
                    └─────────────────────────────┘
```

---

## 📂 Project Structure

```
containerguard-new/
├── agent/
│   ├── actions.py          # Core action execution (restart)
│   ├── core.py             # Main agent engine
│   ├── runner.py           # Entry point for systemd service
│   └── __init__.py
├── dashboard/
│   ├── app.py              # Gradio web dashboard
│   └── run.sh              # Dashboard wrapper script
├── deploy/
│   ├── containerguard.service           # Systemd service for agent
│   └── containerguard-dashboard.service # Systemd service for dashboard
├── audit.py                # Audit log helper
├── auth.py                 # Auth helper
├── license.py              # License validation
├── install.sh              # One-line installer
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (never commit!)
```

---

## 🔐 SELinux Integration

ContainerGuard is compatible with SELinux-enforcing systems (AlmaLinux, RHEL).

### SELinux Context Requirements

| File/Directory | Context | Command |
|----------------|---------|---------|
| `venv/bin/*` | `bin_t` | `sudo chcon -R -t bin_t venv/bin/` |
| `dashboard/run.sh` | `bin_t` | `sudo chcon -t bin_t dashboard/run.sh` |

### Why Wrapper Scripts?

Systemd services running on SELinux-enforcing systems need proper context. The wrapper scripts:

1. Source environment variables (`.env` file)
2. Activate the virtual environment
3. Execute the Python scripts with the correct SELinux context

---

## 🔄 Data Flow

### Agent Monitoring Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Cycle (30s)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                               │
│  │  Timer      │  → Triggered every 30 seconds                │
│  └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Connect to │  → Local Docker socket                        │
│  │  Docker     │  → unix:///var/run/docker.sock               │
│  └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Check      │  → List all containers                        │
│  │  Containers │  → Check status (RUNNING/EXITED/PAUSED)      │
│  └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Decision Engine                                        │   │
│  │  - EXITED → Auto-heal (restart)                        │   │
│  │  - FAILED → Log error                                  │   │
│  │  - RUNNING → Continue monitoring                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Log Action │  → Write to /tmp/containerguard_history.json │
│  │  to History │  → (Slack alert if Pro enabled)             │
│  └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Wait 30s   │  → Repeat cycle                              │
│  └─────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Data Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User → Browser → http://<ip>:7860                            │
│                    │                                            │
│                    ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Gradio Dashboard (app.py)                              │   │
│  │  - Reads /tmp/containerguard_history.json              │   │
│  │  - Fetches live container status from Docker           │   │
│  │  - Displays unified view                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Service Management

### Systemd Service Configuration

**Agent Service** (`/etc/systemd/system/containerguard.service`):

```ini
[Unit]
Description=ContainerGuard Agent - Autonomous Docker Monitoring
After=docker.service network.target
Wants=docker.service

[Service]
Type=simple
User=<your-user>
Group=<your-user>
WorkingDirectory=/home/<your-user>/containerguard-new
Environment="PATH=/home/<your-user>/containerguard-new/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/<your-user>/containerguard-new/agent/runner.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/containerguard.log
StandardError=append:/var/log/containerguard-error.log

[Install]
WantedBy=multi-user.target
```

**Dashboard Service** (`/etc/systemd/system/containerguard-dashboard.service`):

```ini
[Unit]
Description=ContainerGuard Dashboard
After=network.target containerguard.service
Wants=containerguard.service

[Service]
Type=simple
User=<your-user>
Group=<your-user>
WorkingDirectory=/home/<your-user>/containerguard-new
Environment="PATH=/home/<your-user>/containerguard-new/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/<your-user>/containerguard-new/dashboard/run.sh
Restart=always
RestartSec=10
StandardOutput=append:/var/log/containerguard-dashboard.log
StandardError=append:/var/log/containerguard-dashboard-error.log

[Install]
WantedBy=multi-user.target
```

---

## 📊 Data Persistence

### Action History Schema (`/tmp/containerguard_history.json`)

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

---

## 🔒 Security Considerations

1. **.env files never committed** — Added to `.gitignore`
2. **SELinux enforcement** — Proper contexts applied via `chcon`
3. **User separation** — Services run as installing user, not `root`

---

## 📈 Performance Characteristics

| Metric | Value |
|--------|-------|
| **Memory Usage** | ~15-20 MB per agent |
| **CPU Usage** | ~1-2% during monitoring |
| **API Calls** | 1 per cycle (30s) |
| **Log Size** | ~50 MB/day (rotated) |

---

## 💎 Upgrade to ContainerGuard Pro

For **Multi-Host monitoring**, **Slack alerts**, **Auto-cleanup**, and **GitHub OAuth**, upgrade to ContainerGuard Pro.

| Feature | Free | **Pro** |
|---------|:----:|:-------:|
| Multi-Host (control + workers) | ❌ | ✅ |
| Slack alerts | ❌ | ✅ |
| Auto-cleanup | ❌ | ✅ |
| Unlimited history | ❌ | ✅ |
| GitHub OAuth | ❌ | ✅ |

**Pro architecture adds:**
- Central control node monitoring multiple worker nodes
- Aggregated dashboard view across all hosts
- Per-host auto-heal with Slack notifications
- License validation and Pro feature gating

### 🔓 Get Pro Access

- 📧 Contact: **muralipala15@gmail.com**
- 📝 Include your GitHub username

---

## 📚 Related Documentation

- **README.md** — Project overview
- **INSTALL.md** — Installation guide
- **API.md** — API reference

---

**Built with ❤️ for the Docker community**
