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
| **Docker** | 20.10+ | Latest |
| **Python** | 3.9+ | 3.9+ |

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
🚀 Installation Methods
Method 1: One-Line Install (Recommended)
# Download and run the installer
curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/main/install.sh | bash
Method 2: Manual Installation
📦 Manual Installation Steps
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
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import docker; print('✅ Docker SDK installed')"
python -c "import gradio; print('✅ Gradio installed')"
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import docker; print('✅ Docker SDK installed')"
python -c "import gradio; print('✅ Gradio installed')"
4. Configure Docker Connection
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
5. Test the Agent
# Run a quick test
python agent/core.py

# Expected output:
# ✅ Connected to Docker at tcp://<worker-ip>:2375
# 📋 Container Status Summary:
#   - test-app: running
#   - test-postgres: exited
#   - test-redis: running
#   - test-nginx: running
# Run a quick test
python agent/core.py

# Expected output:
# ✅ Connected to Docker at tcp://<worker-ip>:2375
# 📋 Container Status Summary:
#   - test-app: running
#   - test-postgres: exited
#   - test-redis: running
#   - test-nginx: running
# Run a quick test
python agent/core.py

# Expected output:
# ✅ Connected to Docker at tcp://<worker-ip>:2375
# 📋 Container Status Summary:
#   - test-app: running
#   - test-postgres: exited
#   - test-redis: running
#   - test-nginx: running
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
     Active: active (running) since Sat 2026-08-22 05:32:19 +04
   Main PID: 3668 (python)
      Tasks: 1 (limit: 22905)
     Memory: 15.9M
     CGroup: /system.slice/containerguard.service
             └─3668 /home/ruser/containerguard-new/venv/bin/python /home/ruser/containerguard-new/agent/runner.py
7. Start the Dashboard
# Run the dashboard
python dashboard/app.py

# Expected output:
# Running on local URL:  http://0.0.0.0:7860
# Run the dashboard
python dashboard/app.py

# Expected output:
# Running on local URL:  http://0.0.0.0:7860
8. Open Firewall Port (for Dashboard)
# Allow port 7860
sudo firewall-cmd --add-port=7860/tcp --permanent
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-ports
[200~🔧 Configuration
Agent Configuration
Edit agent/runner.py to customize:~
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
🐛 Troubleshooting
Issue: "Permission denied" on /var/log/containerguard.log
# Fix permissions
sudo rm -f /var/log/containerguard.log
sudo touch /var/log/containerguard.log
sudo chown root:root /var/log/containerguard.log
sudo chmod 644 /var/log/containerguard.log
sudo systemctl restart containerguard
Issue: SELinux blocking execution
# Check SELinux status
getenforce

# Add context rule
sudo chcon -R -t bin_t /home/ruser/containerguard-new/venv/bin/
sudo semanage fcontext -a -t bin_t "/home/ruser/containerguard-new/venv/bin(/.*)?"
sudo restorecon -Rv /home/ruser/containerguard-new/venv/bin/

# Restart service
sudo systemctl restart containerguard
Issue: Dashboard not accessible
# Check if dashboard is running
ps aux | grep dashboard/app.py

# Check port binding
sudo netstat -tlnp | grep 7860

# Check firewall
sudo firewall-cmd --list-ports

# If not running, start it
python dashboard/app.py
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
sudo cat /var/log/containerguard.log | tail -20
Expected output:
2026-08-22 05:48:16,415 - INFO - 🚀 ContainerGuard Agent - Continuous Mode Started
2026-08-22 05:48:16,415 - INFO - ⏱️  Monitoring interval: 30 seconds
2026-08-22 05:48:16,430 - INFO - ✅ Connected to Docker at tcp://192.168.217.163:2375
2026-08-22 05:48:16,430 - INFO - 🔄 Cycle 1 starting...
Verify Dashboard
Open browser: http://<agent-ip>:7860

Should see container status and history

Try clicking "Refresh Status"
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
