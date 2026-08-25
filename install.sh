#!/bin/bash
# ContainerGuard - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/master/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "═══════════════════════════════════════════════════════════════"
echo "  🔐 ContainerGuard - Autonomous Docker Agent"
echo "  Version: 1.0.0"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root - this is not recommended"
    INSTALL_USER=$SUDO_USER
else
    INSTALL_USER=$USER
fi
print_info "Installing for user: $INSTALL_USER"

print_info "Checking prerequisites..."
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    print_info "Detected OS: $ID $VERSION_ID"
else
    print_error "Cannot detect OS."
    exit 1
fi
# Check and install Docker if missing
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Installing..."
    
    # Detect OS and install Docker
    if [[ "$ID" == "almalinux" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "centos" ]]; then
        sudo dnf install -y dnf-utils
        sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io
    elif [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
        sudo apt update
        sudo apt install -y docker.io
    else
        print_error "Unsupported OS. Please install Docker manually."
        exit 1
    fi
    
    sudo systemctl enable --now docker
    sudo usermod -aG docker $INSTALL_USER
    print_success "Docker installed successfully"
else
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_success "Docker found: $DOCKER_VERSION"
fi
print_success "Docker found: $(docker --version | cut -d' ' -f3 | tr -d ',')"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    exit 1
fi
print_success "Python found: $(python3 --version | cut -d' ' -f2)"

INSTALL_DIR="/home/$INSTALL_USER/containerguard-new"
print_info "Installation directory: $INSTALL_DIR"

if [[ -d "$INSTALL_DIR" ]]; then
    print_warning "Directory exists: $INSTALL_DIR"
    read -p "Remove existing installation? (y/N) " -n 1 -r </dev/tty
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    else
        print_error "Installation cancelled."
        exit 1
    fi
fi

print_info "Cloning repository..."
git clone https://github.com/muralipala1504/containerguard-new.git "$INSTALL_DIR"
cd "$INSTALL_DIR"

print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_info "Configuring file permissions and SELinux..."
sudo chown -R $INSTALL_USER:$INSTALL_USER "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR/venv/bin/"

if command -v getenforce &> /dev/null && [[ $(getenforce) == "Enforcing" ]]; then
    print_info "SELinux is enforcing - applying context rules..."
    sudo chcon -R -t bin_t "$INSTALL_DIR/venv/bin/"
    if command -v semanage &> /dev/null; then
        sudo semanage fcontext -a -t bin_t "$INSTALL_DIR/venv/bin(/.*)?" 2>/dev/null || true
        sudo restorecon -Rv "$INSTALL_DIR/venv/bin/" 2>/dev/null || true
    fi
fi

print_info "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

print_info "Testing Docker connection..."
if python -c "import docker; c=docker.DockerClient(base_url='unix:///var/run/docker.sock'); c.ping()" 2>/dev/null; then
    print_success "Docker connection successful"
else
    print_warning "Cannot connect to local Docker. If using remote Docker, configure DOCKER_HOST."
fi

echo ""
print_info "Docker Configuration:"
echo "  1) Local Docker (same machine) - Default"
echo "  2) Remote Docker (different machine)"
echo "  3) Skip (configure manually later)"
read -p "Choose option (1-3): " DOCKER_OPTION </dev/tty

case $DOCKER_OPTION in
    1) print_info "Using local Docker" ;;
    2) read -p "Enter remote Docker IP: " REMOTE_IP </dev/tty
       echo "export DOCKER_HOST=tcp://$REMOTE_IP:2375" >> "$INSTALL_DIR/.env" ;;
    3) print_info "Skipping Docker configuration." ;;
    *) print_warning "Invalid option. Using local Docker." ;;
esac

echo ""
print_info "Install Gradio Dashboard?"
echo "  1) Yes (recommended)"
echo "  2) No (agent only)"
read -p "Choose option (1-2): " DASHBOARD_OPTION </dev/tty

print_info "Installing systemd service..."
sudo cp deploy/containerguard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable containerguard
sudo systemctl start containerguard

if sudo systemctl is-active --quiet containerguard; then
    print_success "ContainerGuard service is running"
else
    print_error "Service failed to start. Check logs: sudo journalctl -u containerguard"
    exit 1
fi

if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    print_info "Installing dashboard service..."
    sudo cp deploy/containerguard-dashboard.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable containerguard-dashboard
    sudo systemctl start containerguard-dashboard
    print_success "Dashboard service started"

    # Open firewall for dashboard
    print_info "Configuring firewall for dashboard..."
    if ! systemctl is-active --quiet firewalld 2>/dev/null; then
        print_info "Starting firewalld..."
        sudo systemctl start firewalld 2>/dev/null || true
        sudo systemctl enable firewalld 2>/dev/null || true
    fi
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --add-port=7860/tcp --permanent 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        print_success "Firewall port 7860 opened"
    else
        print_warning "firewalld not found. Please open port 7860 manually."
    fi
fi

cat > "$INSTALL_DIR/.env" << 'ENVEOF'
DOCKER_HOST=unix:///var/run/docker.sock
AGENT_INTERVAL=30
LOG_LEVEL=INFO
ENVEOF

sudo chown -R $INSTALL_USER:$INSTALL_USER "$INSTALL_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════════"
print_success "✅ ContainerGuard Installation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Installation Summary:"
echo "  📁 Location: $INSTALL_DIR"
echo "  🔧 Service: containerguard (systemd)"
if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    echo "  📊 Dashboard: http://$(hostname -I | awk '{print $1}'):7860"
else
    echo "  📊 Dashboard: Not installed"
fi
echo "  📝 Logs: /var/log/containerguard.log"
echo "  🔐 Status: sudo systemctl status containerguard"
echo ""
echo "📚 Useful Commands:"
echo "  sudo systemctl status containerguard  # Check service status"
echo "  sudo journalctl -u containerguard -f  # View logs"
if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    echo "  sudo systemctl status containerguard-dashboard  # Dashboard status"
fi
echo ""
echo "📖 Documentation:"
echo "  README.md      - Project overview"
echo "  INSTALL.md     - Detailed installation"
echo "  ARCHITECTURE.md - Technical design"
echo "  API.md         - API reference"
echo ""
echo "🔗 GitHub: https://github.com/muralipala1504/containerguard-new"
echo "═══════════════════════════════════════════════════════════════"
