#!/bin/bash
# Deploy NAS Control to Raspberry Pi
# Usage: ./deploy.sh [raspberry_pi_ip] [user]

set -e

# Configuration
RASPI_IP="${1:-192.168.1.54}"  # Default Raspberry Pi IP, override with first argument
RASPI_USER="${2:-jitrack}"          # Default user, override with second argument  
RASPI_DEPLOY_DIR="/home/$RASPI_USER/NASControl"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SSH_CONTROL_PATH="/tmp/ssh-deploy-$$"

# Setup SSH ControlMaster for connection reuse (single password prompt)
export SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CONTROL_PATH -o ControlPersist=10m"

# Cleanup function to close SSH connection
cleanup() {
    ssh $SSH_OPTS -O exit raspi 2>/dev/null || true
    rm -f "$SSH_CONTROL_PATH" 2>/dev/null || true
}
trap cleanup EXIT

echo "═══════════════════════════════════════════════════════"
echo "  NAS Control - Deploy to Raspberry Pi"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Local:  $LOCAL_DIR"
echo "  Remote: raspi:$RASPI_DEPLOY_DIR"
echo ""
echo "💡 Tip: To avoid entering password, setup SSH keys:"
echo "   ssh-copy-id raspi"
echo ""

# Check if Raspberry Pi is reachable
echo "1. Checking Raspberry Pi connectivity..."
if ! ping -c 1 -W 2 "$RASPI_IP" > /dev/null 2>&1; then
    echo "   ✗ Error: Cannot reach Raspberry Pi at $RASPI_IP"
    echo "   Please check the IP address and network connection."
    exit 1
fi
echo "   ✓ Raspberry Pi is reachable"
echo ""

# Establish SSH connection (will prompt for password once)
echo "2. Establishing SSH connection..."
ssh $SSH_OPTS raspi 'echo "   ✓ SSH connection established"'
echo ""

# Create deployment directory on Raspberry Pi
echo "3. Creating deployment directory on Raspberry Pi..."
ssh $SSH_OPTS raspi "mkdir -p $RASPI_DEPLOY_DIR"
echo "   ✓ Directory created: $RASPI_DEPLOY_DIR"
echo ""

# Sync project files (excluding virtualenv, cache, logs)
echo "4. Syncing project files..."
rsync -avz --delete \
    -e "ssh $SSH_OPTS" \
    --exclude 'PythonEnv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude '.gitignore' \
    --exclude '*.log' \
    --exclude 'test_*.py' \
    --exclude 'truenas_*.sh' \
    --exclude 'check_nas_config.py' \
    --exclude 'diagnose.py' \
    "$LOCAL_DIR/" "raspi:$RASPI_DEPLOY_DIR/"
echo "   ✓ Files synced"
echo ""

# Install Python dependencies on Raspberry Pi
echo "5. Setting up Python environment on Raspberry Pi..."
ssh $SSH_OPTS raspi << ENDSSH
cd $RASPI_DEPLOY_DIR

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "   ✗ Python3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "PythonEnv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv PythonEnv
fi

# Activate and install dependencies
echo "   Installing dependencies..."
source PythonEnv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null

echo "   ✓ Python environment ready"
ENDSSH
echo ""

# Create/update systemd service file
echo "6. Setting up systemd service..."
ssh $SSH_OPTS raspi << ENDSSH
sudo tee /etc/systemd/system/nas-control.service > /dev/null << EOF
[Unit]
Description=NAS Control Web Application
After=network.target

[Service]
Type=simple
User=$RASPI_USER
WorkingDirectory=$RASPI_DEPLOY_DIR
Environment="PATH=$RASPI_DEPLOY_DIR/PythonEnv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$RASPI_DEPLOY_DIR/PythonEnv/bin/python $RASPI_DEPLOY_DIR/app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable nas-control.service
echo "   ✓ Systemd service installed and enabled"
ENDSSH
echo ""

# Restart the service
echo "7. Restarting NAS Control service..."
ssh $SSH_OPTS raspi "sudo systemctl restart nas-control.service"
sleep 2
echo ""

# Check service status
echo "8. Checking service status..."
ssh $SSH_OPTS raspi "sudo systemctl status nas-control.service --no-pager -l" || true
echo ""

# Get Raspberry Pi local IP
RASPI_LOCAL_IP=$(ssh $SSH_OPTS raspi "hostname -I | awk '{print \$1}'")

echo "═══════════════════════════════════════════════════════"
echo "  ✓ Deployment Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Service Commands:"
echo "  Start:   ssh raspi 'sudo systemctl start nas-control'"
echo "  Stop:    ssh raspi 'sudo systemctl stop nas-control'"
echo "  Restart: ssh raspi 'sudo systemctl restart nas-control'"
echo "  Status:  ssh raspi 'sudo systemctl status nas-control'"
echo "  Logs:    ssh raspi 'sudo journalctl -u nas-control -f'"
echo ""
echo "Access the web interface:"
echo "  http://$RASPI_LOCAL_IP:5000"
echo "  http://$RASPI_IP:5000"
echo ""
echo "Install PWA on your phone:"
echo "  1. Open the URL on your phone browser"
echo "  2. Tap the menu (⋮) and select 'Install app' or 'Add to Home Screen'"
echo "  3. The app will be installed like a native application"
echo ""
