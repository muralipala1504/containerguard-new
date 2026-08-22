#!/bin/bash
# ContainerGuard - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/muralipala1504/containerguard-new/main/install.sh | bash

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo "═══════════════════════════════════════════════════════════════"
echo "  🔐 ContainerGuard - Autonomous Docker Agent"
echo "  Version: 1.0.0"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if running as root (sudo)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root - this is not recommended"
    print_info "Using user: $SUDO_USER"
    INSTALL_USER=$SUDO_USER
else
    INSTALL_USER=$USER
fi

print_info "Installing for user: $INSTALL_USER"

# Check prerequisites
print_info "Checking prerequisites..."

# Check OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    print_info "Detected OS: $OS $VER"
else
    print_error "Cannot detect OS. Only AlmaLinux, RHEL, and Ubuntu are supported."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    print_info "Visit: https://docs.docker.com/engine/install/"
    exit 1
else
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_success "Docker found: $DOCKER_VERSION"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+."
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python found: $PYTHON_VERSION"
fi

# Set install directory
INSTALL_DIR="/home/$INSTALL_USER/containerguard-new"
print_info "Installation directory: $INSTALL_DIR"

# Step 1: Clone or update repository
if [[ -d "$INSTALL_DIR" ]]; then
    print_warning "Directory already exists: $INSTALL_DIR"
    read -p "Remove existing installation? (y/N) " -n 1 -r
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

# Step 2: Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
# After "Creating Python virtual environment..." section

# Fix permissions and SELinux context
print_info "Configuring file permissions and SELinux..."
sudo chown -R $INSTALL_USER:$INSTALL_USER "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR/venv/bin/"

# SELinux context (if enforcing)
if command -v getenforce &> /dev/null && [[ $(getenforce) == "Enforcing" ]]; then
    print_info "SELinux is enforcing - applying context rules..."
    sudo chcon -R -t bin_t "$INSTALL_DIR/venv/bin/"
    if command -v semanage &> /dev/null; then
        sudo semanage fcontext -a -t bin_t "$INSTALL_DIR/venv/bin(/.*)?" 2>/dev/null || true
        sudo restorecon -Rv "$INSTALL_DIR/venv/bin/" 2>/dev/null || true
    fi
fi
# Step 3: Install dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Step 4: Test agent connection
print_info "Testing Docker connection..."
if python -c "import docker; c=docker.DockerClient(base_url='unix:///var/run/docker.sock'); c.ping()" 2>/dev/null; then
    print_success "Docker connection successful"
else
    print_warning "Cannot connect to local Docker. If using remote Docker, configure DOCKER_HOST."
fi

# Step 5: Ask about Docker configuration
echo ""
print_info "Docker Configuration:"
echo "  1) Local Docker (same machine) - Default"
echo "  2) Remote Docker (different machine)"
echo "  3) Skip (configure manually later)"
read -p "Choose option (1-3): " DOCKER_OPTION

case $DOCKER_OPTION in
    1)
        print_info "Using local Docker (unix:///var/run/docker.sock)"
        ;;
    2)
        read -p "Enter remote Docker IP: " REMOTE_IP
        print_info "Setting DOCKER_HOST=tcp://$REMOTE_IP:2375"
        echo "export DOCKER_HOST=tcp://$REMOTE_IP:2375" >> "$INSTALL_DIR/.env"
        ;;
    3)
        print_info "Skipping Docker configuration. Configure manually later."
        ;;
    *)
        print_warning "Invalid option. Using local Docker."
        ;;
esac
# Start dashboard in background
if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    print_info "Starting dashboard in background..."
    cd "$INSTALL_DIR"
    nohup venv/bin/python dashboard/app.py > dashboard.log 2>&1 &
    
    # 🔥 ADD THIS: Open firewall for dashboard
    print_info "Opening firewall port 7860..."
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --add-port=7860/tcp --permanent 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        print_success "Firewall port 7860 opened"
    elif command -v ufw &> /dev/null; then
        sudo ufw allow 7860/tcp 2>/dev/null || true
        print_success "Firewall port 7860 opened (ufw)"
    else
        print_warning "Firewall not detected. Please open port 7860 manually."
    fi
    
    # Get the IP for the summary
    DASHBOARD_IP=$(hostname -I | awk '{print $1}')
    print_success "Dashboard started on http://$DASHBOARD_IP:7860"
fi
# Step 6: Ask about dashboard installation
echo ""
print_info "Install Gradio Dashboard?"
echo "  1) Yes (recommended)"
echo "  2) No (agent only)"
read -p "Choose option (1-2): " DASHBOARD_OPTION

# Step 7: Install systemd service
print_info "Installing systemd service..."
sudo cp deploy/containerguard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable containerguard
sudo systemctl start containerguard

# Check service status
if sudo systemctl is-active --quiet containerguard; then
    print_success "ContainerGuard service is running"
else
    print_error "Service failed to start. Check logs: sudo journalctl -u containerguard"
    exit 1
fi

# Step 8: Firewall for dashboard AND start it
if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    print_info "Configuring firewall and starting dashboard..."
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --add-port=7860/tcp --permanent 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        print_success "Port 7860 opened in firewall"
    else
        print_warning "firewalld not found. Open port 7860 manually if needed."
    fi
    
    # Start the dashboard in the background
    cd "$INSTALL_DIR"
    nohup venv/bin/python dashboard/app.py > dashboard.log 2>&1 &
    print_success "Dashboard started on http://$(hostname -I | awk '{print $1}'):7860"
fi
# Step 9: Create .env file for configuration
cat > "$INSTALL_DIR/.env" << 'ENVEOF'
# ContainerGuard Environment Configuration
DOCKER_HOST=unix:///var/run/docker.sock
AGENT_INTERVAL=30
LOG_LEVEL=INFO
ENVEOF

# Step 10: Set permissions
sudo chown -R $INSTALL_USER:$INSTALL_USER "$INSTALL_DIR"

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
print_success "✅ ContainerGuard Installation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Installation Summary:"
echo "  📁 Location: $INSTALL_DIR"
echo "  🔧 Service: containerguard (systemd)"
echo "  📊 Dashboard: http://$(hostname -I | awk '{print $1}'):7860"
echo "  📝 Logs: /var/log/containerguard.log"
echo "  🔐 Status: sudo systemctl status containerguard"
echo ""
echo "📚 Useful Commands:"
echo "  sudo systemctl status containerguard  # Check service status"
echo "  sudo journalctl -u containerguard -f  # View logs"
echo "  python dashboard/app.py               # Start dashboard manually"
echo ""
echo "📖 Documentation:"
echo "  README.md      - Project overview"
echo "  INSTALL.md     - Detailed installation"
echo "  ARCHITECTURE.md - Technical design"
echo "  API.md         - API reference"
echo ""
echo "🔗 GitHub: https://github.com/muralipala1504/containerguard-new"
echo "═══════════════════════════════════════════════════════════════"
