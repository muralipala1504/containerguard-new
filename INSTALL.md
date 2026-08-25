# 🔧 ContainerGuard Installation Guide

Detailed step-by-step instructions for installing ContainerGuard on AlmaLinux 9, Ubuntu 22.04+, or RHEL-based systems.

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

### Docker Auto-Installation

If Docker is not installed on your system, the installer will:
1. ✅ Detect your OS (AlmaLinux, RHEL, CentOS, Ubuntu, Debian)
2. ✅ Install Docker using the official repositories
3. ✅ Start Docker and enable it on boot
4. ✅ Add your user to the `docker` group

**No manual Docker installation needed!**

### Check Your System

```bash
# Check OS version
cat /etc/os-release

# Check Docker version
docker --version

# Check Python version
python3 --version

# Check available memory
free -h
🚀 Quick Install (Recommended)
One-Line Installation
curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/master/install.sh | bash
The installer will:

✅ Check prerequisites (Docker, Python, OS)

✅ Clone the repository

✅ Create Python virtual environment

✅ Install dependencies (including Gradio 4.36.1)

✅ Configure SELinux context (if enforcing)

✅ Ask for Docker configuration (local/remote)

✅ Ask for dashboard installation

✅ Install systemd service

✅ Open firewall port 7860

✅ Start the dashboard

📦 Manual Installation (Advanced)
1. Clone the Repository
cd ~
git clone https://github.com/muralipala1504/containerguard-new.git
cd containerguard-new
2. Create Virtual Environment
# Create Python virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify Python path
which python
# Should show: /home/username/containerguard-new/venv/bin/python
3. Install Dependencies
# Install Python packages (pinned versions for compatibility)
pip install -r requirements.txt

# Verify installation
python -c "import docker; print('✅ Docker SDK installed')"
python -c "import gradio; print('✅ Gradio installed')"
4. Configure SELinux (if enabled)
# Check SELinux status
getenforce

# If enforcing, apply context rules
sudo chcon -R -t bin_t venv/bin/
sudo semanage fcontext -a -t bin_t "/home/ruser/containerguard-new/venv/bin(/.*)?"
sudo restorecon -Rv venv/bin/
5. Configure Docker Connection
Option A: Local Docker (Same Machine)
# Use default Docker socket
export DOCKER_HOST=unix:///var/run/docker.sock
Option B: Remote Docker (Different Machine)
# Enable Docker API on the worker machine
# On the worker machine, create override file:
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/override.conf <<'DOCKEREOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
DOCKEREOF
sudo systemctl daemon-reload
sudo systemctl restart docker

# On the agent machine, set the DOCKER_HOST
export DOCKER_HOST=tcp://YOUR_WORKER_IP:2375
# Replace YOUR_WORKER_IP with the actual IP address
6. Test the Agent
# Run a quick test
python agent/core.py

# Expected output:
# ✅ Connected to Docker
# 📋 Container Status Summary:
#   - test-app: running
#   - test-postgres: exited
#   - test-redis: running
#   - test-nginx: running
7. Set Up as Systemd Service
# Copy the service file
sudo cp deploy/containerguard.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable containerguard

# Start the service
sudo systemctl start containerguard

# Check status
sudo systemctl status containerguard
Expected output:
● containerguard.service - ContainerGuard Agent - Autonomous Docker Monitoring
     Loaded: loaded (/etc/systemd/system/containerguard.service; enabled)
     Active: active (running) since Sat 2026-08-24 05:36:58 +04
   Main PID: 5499 (python)
      Tasks: 1 (limit: 22905)
     Memory: 16.1M
     CGroup: /system.slice/containerguard.service
             └─5499 /home/ruser/containerguard-new/venv/bin/python /home/ruser/containerguard-new/agent/runner.py
8. Start the Dashboard
# Run the dashboard in the background
cd ~/containerguard-new
source venv/bin/activate
nohup python dashboard/app.py > dashboard.log 2>&1 &

# Expected output:
# Running on local URL:  http://0.0.0.0:7860
9. Open Firewall Port (if needed)
# Allow port 7860 (firewalld)
sudo firewall-cmd --add-port=7860/tcp --permanent
sudo firewall-cmd --reload

# Or for UFW
sudo ufw allow 7860/tcp

# Verify
sudo firewall-cmd --list-ports
🔧 Configuration
Agent Configuration
Edit agent/runner.py to customize:
# In agent/runner.py
# Change monitoring interval (seconds)
AGENT_INTERVAL = 30  # Default is 30

# Change Docker host
DOCKER_HOST = 'tcp://192.168.217.163:2375'  # Replace with your Docker host
Dashboard Configuration
Edit dashboard/app.py:
# Change port
demo.launch(server_name="0.0.0.0", server_port=7860)
# Change to port 8080 if needed
Persistent History
History is stored in /tmp/containerguard_history.json:
[
  {
    "timestamp": "2026-08-24T05:35:57.986681",
    "action": "restart",
    "container": "test-postgres",
    "status": "success"
  }
]
🐛 Troubleshooting
Issue: Service fails with "Permission denied"
# Fix SELinux context
sudo chcon -R -t bin_t /home/ruser/containerguard-new/venv/bin/
sudo semanage fcontext -a -t bin_t "/home/ruser/containerguard-new/venv/bin(/.*)?"
sudo restorecon -Rv /home/ruser/containerguard-new/venv/bin/
## 🐛 Troubleshooting

### SELinux Blocking Execution

If the agent or dashboard fails with `status=203/EXEC` or `Permission denied`:

```bash
# Try SELinux permissive mode first
sudo setenforce 0
sudo systemctl restart containerguard
sudo systemctl restart containerguard-dashboard

# If it works, apply the permanent fix
sudo chcon -R -t bin_t /home/ruser/containerguard-new/venv/bin/
sudo setenforce 1
sudo systemctl restart containerguard
sudo systemctl restart containerguard-dashboard

Dashboard Service Fails with Permission Denied
If the dashboard service fails with Permission denied on /var/log/containerguard.log:

sudo tee /etc/systemd/system/containerguard-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=ContainerGuard Dashboard
After=network.target containerguard.service
Wants=containerguard.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/ruser/containerguard-new
Environment="PATH=/home/ruser/containerguard-new/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ruser/containerguard-new/venv/bin/python /home/ruser/containerguard-new/dashboard/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/containerguard-dashboard.log
StandardError=append:/var/log/containerguard-dashboard-error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart containerguard-dashboard

Service Fails with "Permission denied" on /var/log/containerguard.log

sudo touch /var/log/containerguard.log
sudo chown ruser:ruser /var/log/containerguard.log
sudo chmod 644 /var/log/containerguard.log
sudo systemctl restart containerguard


---

## 🧪 **Step 7: Verify INSTALL.md**

```bash
cat ~/containerguard-new/INSTALL.md | grep -A 15 "SELinux Blocking"

# Restart service
sudo systemctl restart containerguard
Issue: Dashboard shows "No actions recorded"
# Check if history file exists
cat /tmp/containerguard_history.json

# If empty, restart the agent
sudo systemctl restart containerguard

# Wait 60 seconds and check again
sleep 60
cat /tmp/containerguard_history.json
Issue: Dashboard not accessible
# Check if dashboard is running
ps aux | grep dashboard/app.py

# Check port binding
sudo netstat -tlnp | grep 7860

# Check firewall
sudo firewall-cmd --list-ports

# If not running, start it
cd ~/containerguard-new
source venv/bin/activate
nohup python dashboard/app.py > dashboard.log 2>&1 &
Issue: Agent not monitoring containers
# Check logs
sudo journalctl -u containerguard -f

# Check Docker connection
python -c "import docker; c=docker.DockerClient(base_url='tcp://YOUR_IP:2375'); print(c.containers.list())"
✅ Verification
Verify Agent is Running
# Check service status
sudo systemctl status containerguard

# Check logs
sudo tail -20 /var/log/containerguard.log
Expected output:
2026-08-24 05:36:58 - INFO - ✅ Connected to Docker at tcp://192.168.217.163:2375
2026-08-24 05:36:58 - INFO - 🔄 Cycle 1 starting...
2026-08-24 05:36:58 - INFO - ✅ test-app: RUNNING
2026-08-24 05:36:58 - WARNING - ⚠️ test-postgres: EXITED - Attempting restart...
2026-08-24 05:36:58 - INFO - ✅ Restarted container: test-postgres
Verify Dashboard
Open browser: http://<agent-ip>:7860

Should see container status and action history

Try clicking "Refresh Status"
Verify Persistent History
# Check history file
cat /tmp/containerguard_history.json
📦 Uninstallation
# Stop and disable service
sudo systemctl stop containerguard
sudo systemctl disable containerguard

# Remove service file
sudo rm /etc/systemd/system/containerguard.service
sudo systemctl daemon-reload

# Remove installation directory
rm -rf ~/containerguard-new

# Remove logs
sudo rm -f /var/log/containerguard*.log
📚 Next Steps
□ Configure alerts (Slack/Discord)
□ Customize monitoring rules
□ Scale to multiple Docker hosts
□ Integrate with Prometheus
🆘 Need Help?
GitHub Issues: https://github.com/muralipala1504/containerguard-new/issues

Discussions: https://github.com/muralipala1504/containerguard-new/discussions

Next: ARCHITECTURE.md - Technical design and data flow
