#!/bin/bash
# Deploy NAS Control to Raspberry Pi
# Usage: ./deploy/deploy.sh [raspberry_pi_ip] [user]

set -e

# Configuration
RASPI_IP="${1:-192.168.1.54}"
RASPI_USER="${2:-jitrack}"
RASPI_DEPLOY_DIR="/home/$RASPI_USER/NASControl"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SSH_CONTROL_PATH="/tmp/ssh-deploy-$$"

# SSH ControlMaster for connection reuse (single password prompt)
export SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CONTROL_PATH -o ControlPersist=10m"

cleanup() {
    ssh $SSH_OPTS -O exit "$RASPI_USER@$RASPI_IP" 2>/dev/null || true
    rm -f "$SSH_CONTROL_PATH" 2>/dev/null || true
}
trap cleanup EXIT

echo "═══════════════════════════════════════════════════════"
echo "  NAS Control – Deploy to Raspberry Pi"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Local:  $LOCAL_DIR"
echo "  Remote: $RASPI_USER@$RASPI_IP:$RASPI_DEPLOY_DIR"
echo ""

# 1. Check connectivity
echo "1. Checking Raspberry Pi connectivity..."
if ! ping -c 1 -W 2 "$RASPI_IP" > /dev/null 2>&1; then
    echo "   ✗ Cannot reach $RASPI_IP"
    exit 1
fi
echo "   ✓ Raspberry Pi reachable"
echo ""

# 2. Establish SSH connection
echo "2. Establishing SSH connection..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" 'echo "   ✓ SSH connection established"'
echo ""

# 3. Create deployment directory
echo "3. Creating deployment directory..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" "mkdir -p $RASPI_DEPLOY_DIR"
echo "   ✓ $RASPI_DEPLOY_DIR"
echo ""

# 4. Sync project files
echo "4. Syncing project files..."
rsync -avz --delete \
    -e "ssh $SSH_OPTS" \
    --exclude 'PythonEnv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude '.gitignore' \
    --exclude '*.log' \
    --exclude '*.db' \
    --exclude 'deploy/' \
    "$LOCAL_DIR/" "$RASPI_USER@$RASPI_IP:$RASPI_DEPLOY_DIR/"
echo "   ✓ Files synced"
echo ""

# 5. Setup Python environment
echo "5. Setting up Python environment..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" << ENDSSH
cd $RASPI_DEPLOY_DIR

if ! command -v python3 &> /dev/null; then
    echo "   Installing Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

if [ ! -d "PythonEnv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv PythonEnv
fi

echo "   Installing dependencies..."
source PythonEnv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "   ✓ Python environment ready"
ENDSSH
echo ""

# 6. Setup systemd service
echo "6. Setting up systemd service..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" << ENDSSH
sudo tee /etc/systemd/system/nas-control.service > /dev/null << EOF
[Unit]
Description=NAS Control Web Application
After=network.target

[Service]
Type=simple
User=$RASPI_USER
WorkingDirectory=$RASPI_DEPLOY_DIR
Environment="PATH=$RASPI_DEPLOY_DIR/PythonEnv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$RASPI_DEPLOY_DIR/PythonEnv/bin/python $RASPI_DEPLOY_DIR/server/app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable nas-control.service
echo "   ✓ Systemd service configured"
ENDSSH
echo ""

# 7. Restart service
echo "7. Restarting NAS Control service..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" "sudo systemctl restart nas-control.service"
sleep 2
echo ""

# 8. Check status
echo "8. Checking service status..."
ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" "sudo systemctl status nas-control.service --no-pager -l" || true
echo ""

RASPI_LOCAL_IP=$(ssh $SSH_OPTS "$RASPI_USER@$RASPI_IP" "hostname -I | awk '{print \$1}'")

echo "═══════════════════════════════════════════════════════"
echo "  ✓ Deployment Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Access:  http://$RASPI_LOCAL_IP:5000"
echo "           http://$RASPI_IP:5000"
echo ""
echo "  Logs:    ssh $RASPI_USER@$RASPI_IP 'sudo journalctl -u nas-control -f'"
echo ""
