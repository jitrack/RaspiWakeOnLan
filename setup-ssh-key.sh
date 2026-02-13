#!/bin/bash
# Setup SSH key authentication for password-less deployment
# Run this once to never type password again!

echo "═══════════════════════════════════════════════════════"
echo "  SSH Key Setup - Password-less Authentication"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_ed25519 ] && [ ! -f ~/.ssh/id_rsa ]; then
    echo "No SSH key found. Generating a new one..."
    echo ""
    ssh-keygen -t ed25519 -C "$(whoami)@$(hostname)" -f ~/.ssh/id_ed25519
    echo ""
    echo "✓ SSH key generated!"
    echo ""
else
    echo "✓ SSH key already exists"
    echo ""
fi

# Copy key to Raspberry Pi
echo "Now copying your SSH key to the Raspberry Pi..."
echo "You'll be asked for your password ONE LAST TIME:"
echo ""

ssh-copy-id raspi

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  ✓ Success!"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "SSH key authentication is now configured."
    echo "You can now run ./deploy.sh without entering a password!"
    echo ""
    echo "Test it:"
    echo "  ssh raspi 'echo \"Connection successful!\"'"
    echo ""
else
    echo ""
    echo "✗ Failed to copy SSH key."
    echo "Please check:"
    echo "  1. The Raspberry Pi is reachable"
    echo "  2. Your SSH password is correct"
    echo "  3. SSH is running on the Raspberry Pi"
    exit 1
fi
