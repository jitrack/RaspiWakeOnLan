#!/bin/bash
# Setup SSH key for passwordless deployment
# Usage: ./deploy/setup-ssh-key.sh [raspberry_pi_ip] [user]

set -e

RASPI_IP="${1:-192.168.1.54}"
RASPI_USER="${2:-jitrack}"
KEY_PATH="$HOME/.ssh/id_ed25519"

echo "═══════════════════════════════════════════════════════"
echo "  SSH Key Setup for $RASPI_USER@$RASPI_IP"
echo "═══════════════════════════════════════════════════════"
echo ""

# Generate SSH key if needed
if [ ! -f "$KEY_PATH" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "deploy@nas-control"
    echo "   ✓ Key generated: $KEY_PATH"
else
    echo "   ✓ Key already exists: $KEY_PATH"
fi
echo ""

# Copy key to Raspberry Pi
echo "Copying key to Raspberry Pi (will ask for password one last time)..."
ssh-copy-id -i "$KEY_PATH" "$RASPI_USER@$RASPI_IP"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✓ SSH key installed!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  You can now deploy without password:"
echo "    ./deploy/deploy.sh"
echo ""
