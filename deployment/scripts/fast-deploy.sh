#!/bin/bash
# Fast deployment script using rsync
# Usage: ./fast-deploy.sh <VM_IP> [SSH_KEY_PATH]

VM_IP=${1:-"3.234.106.218"}
SSH_KEY=${2:-"~/.ssh/artevoke-key.pem"}

# Expand ~ in SSH_KEY path
SSH_KEY="${SSH_KEY/#\~/$HOME}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBAPP_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)/webapp"

echo "🚀 Fast deploying webapp to $VM_IP..."

# Create remote directory
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP "mkdir -p ~/artevoke/webapp && sudo chown -R ubuntu:ubuntu ~/artevoke"

# Use rsync for fast, incremental transfers
# Excludes common files that don't need to be transferred
rsync -avz --delete \
  --progress \
  -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
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

