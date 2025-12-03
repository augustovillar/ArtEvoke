#!/bin/bash
# Fast deployment script using rsync
# Usage: ./fast-deploy.sh <VM_IP> [SSH_KEY_PATH]

VM_IP=${1:-"54.204.24.131"}
SSH_KEY=${2:-"~/.ssh/artevoke-key.pem"}

# Expand ~ in SSH_KEY path
SSH_KEY="${SSH_KEY/#\~/$HOME}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBAPP_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)/webapp"

echo "🚀 Fast deploying webapp to $VM_IP..."

# Create remote directory with proper permissions
# First ensure the parent directory exists and has correct ownership
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP "
  mkdir -p ~/artevoke
  sudo chown -R ubuntu:ubuntu ~/artevoke 2>/dev/null || true
  chmod -R 755 ~/artevoke
  mkdir -p ~/artevoke/webapp
"

rsync -avz --delete \
  --progress \
  -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
  --include='env/' \
  --include='env/**' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='new_venv' \
  --exclude='build' \
  --exclude='dist' \
  --exclude='.DS_Store' \
  "$WEBAPP_DIR/" ubuntu@$VM_IP:~/artevoke/webapp/

echo "✅ Deployment complete!"

