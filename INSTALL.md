# 🔧 ContainerGuard Installation Guide

Detailed step-by-step instructions for installing ContainerGuard (Free tier) on AlmaLinux 9, Ubuntu 22.04+, or RHEL-based systems.

> **💎 Looking for Multi-Host, Slack alerts, or Auto-cleanup?** See [Upgrade to Pro](#-upgrade-to-containerGuard-pro) section at the end.

---

## 📋 Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | AlmaLinux 8+, Ubuntu 20.04+ | AlmaLinux 9 |
| **CPU** | 2 cores | 4 cores |
| **RAM** | 2 GB | 4 GB |
| **Disk** | 10 GB | 20 GB |
| **Docker** | **Auto-installed by installer** | Latest |
| **Python** | 3.9+ | 3.9+ |

> **Note**: The installer **automatically installs Docker** if it's not present. You don't need to install Docker manually.

---

## 🚀 Quick Install (Recommended)

### One-Line Installation

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
- ✅ Install systemd services (`containerguard` + `containerguard-dashboard`)
- ✅ Open firewall port 7860
- ✅ Start the agent and dashboard services

---

## 📦 Manual Installation (Advanced)

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate

# Verify Python path
which python
# Should show: /home/<username>/containerguard-new/venv/bin/python
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import docker; print('✅ Docker SDK installed')"
python -c "import gradio; print('✅ Gradio installed')"
```

### 4. Configure SELinux (if enabled)

⚠️ **Critical Step for AlmaLinux/RHEL:**

```bash
# Check SELinux status
getenforce

# If enforcing, apply context rules to venv binaries
sudo chcon -R -t bin_t venv/bin/

# Apply context to wrapper scripts
sudo chcon -t bin_t agent/runner.sh 2>/dev/null || true
sudo chcon -t bin_t dashboard/run.sh

# Verify
ls -Z venv/bin/python
# Should show: unconfined_u:object_r:bin_t:s0
```

### 5. Configure Docker Connection (Local Only)

```bash
# Use default Docker socket (local Docker)
export DOCKER_HOST=unix:///var/run/docker.sock
```

> **💎 Multi-Host?** Monitor containers on a **remote worker VM** — that's a Pro feature. See [Upgrade to Pro](#-upgrade-to-containerGuard-pro).

### 6. Set Up as Systemd Services

**Step 1: Copy service files**

```bash
sudo cp deploy/containerguard.service /etc/systemd/system/
sudo cp deploy/containerguard-dashboard.service /etc/systemd/system/
```

**Step 2: Reload and start services**

```bash
sudo systemctl daemon-reload
sudo systemctl enable containerguard
sudo systemctl enable containerguard-dashboard
sudo systemctl start containerguard
sudo systemctl start containerguard-dashboard
```

**Step 3: Verify services**

```bash
sudo systemctl status containerguard
sudo systemctl status containerguard-dashboard
```

### 7. Open Firewall Port

```bash
# Firewalld
sudo firewall-cmd --add-port=7860/tcp --permanent
sudo firewall-cmd --reload

# UFW
sudo ufw allow 7860/tcp

# Verify
sudo firewall-cmd --list-ports
```

---

## 🌐 Dashboard Access

```bash
# Access the dashboard
http://<your-ip>:7860

# Check if dashboard is running
sudo systemctl status containerguard-dashboard

# View dashboard logs
sudo journalctl -u containerguard-dashboard -f
```

---

## 🔍 Verification

### Verify Agent is Running

```bash
# Check service status
sudo systemctl status containerguard

# Check logs
sudo tail -20 /var/log/containerguard.log
```

**Expected output:**

```
2026-09-14 11:25:53,482 - INFO - ✅ test-app: RUNNING
2026-09-14 11:25:53,483 - INFO - 📊 Monitored containers across 1 host, restarted 0
2026-09-14 11:25:53,483 - INFO - ✅ Monitoring cycle completed
```

### Verify Dashboard

```bash
# Check HTTP response
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://<your-ip>:7860
# Expected: HTTP: 200

# Check port is listening
sudo netstat -tlnp | grep 7860
```

### Verify Persistent History

```bash
cat /tmp/containerguard_history.json
```

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

## 🐛 Common Issues & Solutions

### SELinux Blocking Execution

**Symptoms:** Service fails with `status=203/EXEC` or `Permission denied`

**Solution:**

```bash
# Apply SELinux context to venv binaries
sudo chcon -R -t bin_t $HOME/containerguard-new/venv/bin/

# Apply to wrapper scripts
sudo chcon -t bin_t $HOME/containerguard-new/dashboard/run.sh

# Restart services
sudo systemctl restart containerguard
sudo systemctl restart containerguard-dashboard
```

### Service Fails to Start

**Symptoms:** Service shows errors about missing files or paths

**Solution:**

```bash
# Check the actual error
sudo journalctl -u containerguard -n 20 --no-pager

# Verify service file is correct
cat /etc/systemd/system/containerguard.service | grep -E "User|Group|WorkingDirectory|ExecStart"

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart containerguard
sudo systemctl restart containerguard-dashboard
```

### Dashboard Shows "No actions recorded"

**Solution:**

```bash
# Check if history file exists
cat /tmp/containerguard_history.json

# If empty, restart the agent
sudo systemctl restart containerguard

# Wait 60 seconds and check again
sleep 60
cat /tmp/containerguard_history.json
```

### Gradio Import Error (HfFolder)

**Symptoms:** `ImportError: cannot import name 'HfFolder' from 'huggingface_hub'`

**Solution:**

```bash
cd $HOME/containerguard-new && source venv/bin/activate
pip install gradio==4.44.1 huggingface-hub==0.23.4
sudo systemctl restart containerguard-dashboard
```

---

## 📁 Persistent History

History is stored in `/tmp/containerguard_history.json`:

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

> **Note:** Free tier keeps 7 days of history. **Pro tier** keeps unlimited history.

---

## 📦 Uninstallation

```bash
# Stop and disable services
sudo systemctl stop containerguard
sudo systemctl stop containerguard-dashboard
sudo systemctl disable containerguard
sudo systemctl disable containerguard-dashboard

# Remove service files
sudo rm /etc/systemd/system/containerguard.service
sudo rm /etc/systemd/system/containerguard-dashboard.service
sudo systemctl daemon-reload

# Remove installation directory
rm -rf $HOME/containerguard-new

# Remove logs
sudo rm -f /var/log/containerguard*.log
```

---

## 💎 Upgrade to ContainerGuard Pro

Ready for production? ContainerGuard Pro adds:

| Feature | Free | **Pro** |
|---------|:----:|:-------:|
| Container monitoring | ✅ | ✅ |
| Auto-restart | ✅ | ✅ |
| Web dashboard | ✅ | ✅ |
| Action history | 7 days | ✅ **Unlimited** |
| **Multi-Host** (control + workers) | ❌ | ✅ |
| **Slack alerts** | ❌ | ✅ |
| **Auto-cleanup** | ❌ | ✅ |
| **GitHub OAuth** | ❌ | ✅ |

### 🔓 Get Pro Access

- 📧 Contact: **muralipala15@gmail.com**
- 📝 Include your GitHub username
- 🔑 Receive invite to the private Pro repository

---

## 📚 Next Steps

- [ ] Test auto-heal by stopping a container
- [ ] Configure monitoring interval
- [ ] (Optional) Upgrade to Pro for Multi-Host support

---

## 🆘 Need Help?

- **Issues**: https://github.com/muralipala1504/containerguard-new/issues
- **Discussions**: https://github.com/muralipala1504/containerguard-new/discussions
- **Pro Access**: muralipala15@gmail.com
