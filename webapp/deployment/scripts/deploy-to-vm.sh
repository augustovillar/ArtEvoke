#!/bin/bash
set -e

# Script to deploy ArtEvoke to the VM
# Usage: ./deploy-to-vm.sh <VM_IP> <SSH_KEY_PATH>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBAPP_DIR="$(cd "$DEPLOYMENT_DIR/.." && pwd)"  # Should be /path/to/webapp

VM_IP=${1:-""}
SSH_KEY=${2:-""}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$VM_IP" ]; then
  echo -e "${RED}Error: VM IP address required${NC}"
  echo "Usage: $0 <VM_IP> [SSH_KEY_PATH]"
  echo ""
  echo "Get VM IP from Terraform:"
  echo "  cd terraform && terraform output instance_public_ip"
  exit 1
fi

if [ -z "$SSH_KEY" ]; then
  # Try to find key from terraform output
  SSH_KEY=$(cd "$DEPLOYMENT_DIR/terraform" && terraform output -raw ssh_command 2>/dev/null | grep -oP '(?<=-i\s)\S+' || echo "")
  if [ -z "$SSH_KEY" ]; then
    echo -e "${YELLOW}Warning: SSH key not specified. Using default: ~/.ssh/id_rsa${NC}"
    SSH_KEY="$HOME/.ssh/id_rsa"
  fi
fi

if [ ! -f "$SSH_KEY" ]; then
  echo -e "${RED}Error: SSH key not found: $SSH_KEY${NC}"
  exit 1
fi

echo -e "${BLUE}Deploying ArtEvoke to VM: $VM_IP${NC}"
echo -e "${BLUE}Using SSH key: $SSH_KEY${NC}"

# Check if webapp directory exists
if [ ! -d "$WEBAPP_DIR" ]; then
  echo -e "${RED}Error: Webapp directory not found: $WEBAPP_DIR${NC}"
  exit 1
fi

# Debug: Show detected paths
echo -e "${BLUE}Detected paths:${NC}"
echo -e "  WEBAPP_DIR: $WEBAPP_DIR"

# Create remote directory (use home directory instead of /opt for permissions)
echo -e "${BLUE}Creating remote directory...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP "mkdir -p ~/artevoke/webapp"

# Check if data directory exists
if [ ! -d "$WEBAPP_DIR/data" ]; then
  echo -e "${YELLOW}Warning: data directory not found at $WEBAPP_DIR/data${NC}"
  echo -e "${YELLOW}Skipping data transfer...${NC}"
  SKIP_DATA=true
else
  SKIP_DATA=false
fi

# Create or use existing zip of data directory in webapp
DATA_ZIP="$WEBAPP_DIR/data.zip"
ARCHIVE_TYPE="zip"

if [ "$SKIP_DATA" = false ]; then
  if [ -f "$DATA_ZIP" ]; then
    echo -e "${GREEN}Using existing data.zip in webapp directory${NC}"
  else
    echo -e "${BLUE}Creating zip archive of data directory in webapp...${NC}"
    cd "$WEBAPP_DIR"
    # Use tar.gz for faster compression (faster than zip)
    DATA_ZIP="$WEBAPP_DIR/data.tar.gz"
    ARCHIVE_TYPE="tar.gz"
    tar -czf "$DATA_ZIP" data/ 2>/dev/null || {
      echo -e "${YELLOW}tar.gz failed, trying zip...${NC}"
      DATA_ZIP="$WEBAPP_DIR/data.zip"
      ARCHIVE_TYPE="zip"
      zip -rq "$DATA_ZIP" data/ 2>/dev/null || {
        echo -e "${RED}Error: Could not create archive of data directory${NC}"
        exit 1
      }
    }
    echo -e "${GREEN}✓ Archive created: $DATA_ZIP${NC}"
  fi
fi

# Copy data archive to VM (only if data exists)
if [ "$SKIP_DATA" = false ]; then
  echo -e "${BLUE}Transferring data archive to VM...${NC}"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$DATA_ZIP" ubuntu@$VM_IP:~/artevoke/data-archive.$ARCHIVE_TYPE

  # Extract data on VM (fast extraction)
  echo -e "${BLUE}Extracting data on VM (fast mode)...${NC}"
  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP << ENDSSH
cd ~/artevoke/webapp
mkdir -p data
cd data

# Fast extraction based on archive type
if [[ "$ARCHIVE_TYPE" == "zip" ]]; then
  # Install unzip if needed (silent, fast)
  if ! command -v unzip &> /dev/null; then
    sudo apt-get update -qq > /dev/null 2>&1 && sudo apt-get install -y -qq unzip > /dev/null 2>&1
  fi
  # Fast unzip: no output, no verification, overwrite existing
  unzip -qo ~/artevoke/data-archive.$ARCHIVE_TYPE
else
  # tar.gz is faster - extract without verification
  tar -xzf ~/artevoke/data-archive.$ARCHIVE_TYPE --strip-components=1 2>/dev/null || tar -xzf ~/artevoke/data-archive.$ARCHIVE_TYPE
fi

# If archive created a 'data' subdirectory, move contents up
if [ -d data ]; then
  mv data/* . 2>/dev/null || true
  rmdir data 2>/dev/null || true
fi

# Cleanup archive on VM
rm -f ~/artevoke/data-archive.$ARCHIVE_TYPE
echo "Data extracted successfully"
ENDSSH

  echo -e "${GREEN}✓ Data directory transferred and extracted${NC}"
else
  echo -e "${YELLOW}⚠ Skipping data transfer (data directory not found)${NC}"
fi

# Copy FastAPI directory
if [ -d "$WEBAPP_DIR/FastAPI" ]; then
  echo -e "${BLUE}Copying FastAPI directory...${NC}"
  rsync -avz --progress \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.venv' \
    --exclude 'new_venv' \
    "$WEBAPP_DIR/FastAPI/" ubuntu@$VM_IP:~/artevoke/webapp/FastAPI/
else
  echo -e "${YELLOW}Warning: FastAPI directory not found${NC}"
fi

# Copy frontend directory
if [ -d "$WEBAPP_DIR/frontend" ]; then
  echo -e "${BLUE}Copying frontend directory...${NC}"
  rsync -avz --progress \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'build' \
    "$WEBAPP_DIR/frontend/" ubuntu@$VM_IP:~/artevoke/webapp/frontend/
else
  echo -e "${YELLOW}Warning: frontend directory not found${NC}"
fi

# Copy nginx directory
if [ -d "$WEBAPP_DIR/nginx" ]; then
  echo -e "${BLUE}Copying nginx directory...${NC}"
  rsync -avz --progress \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "$WEBAPP_DIR/nginx/" ubuntu@$VM_IP:~/artevoke/webapp/nginx/
else
  echo -e "${YELLOW}Warning: nginx directory not found${NC}"
fi

# Copy qdrant-startup.sh script
if [ -f "$WEBAPP_DIR/scripts/qdrant-startup.sh" ]; then
  echo -e "${BLUE}Copying qdrant-startup.sh...${NC}"
  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP "mkdir -p ~/artevoke/webapp/scripts"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "$WEBAPP_DIR/scripts/qdrant-startup.sh" \
    ubuntu@$VM_IP:~/artevoke/webapp/scripts/qdrant-startup.sh
else
  echo -e "${YELLOW}Warning: qdrant-startup.sh not found${NC}"
fi

# Copy docker-compose.yml (needed to run services)
if [ -f "$WEBAPP_DIR/docker-compose.yml" ]; then
  echo -e "${BLUE}Copying docker-compose.yml...${NC}"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "$WEBAPP_DIR/docker-compose.yml" \
    ubuntu@$VM_IP:~/artevoke/webapp/docker-compose.yml
else
  echo -e "${YELLOW}Warning: docker-compose.yml not found${NC}"
fi

# Check if .env files exist, if not create from examples
echo -e "${BLUE}Setting up environment files...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP << 'ENDSSH'
cd ~/artevoke/webapp

# Create env directory if it doesn't exist
mkdir -p env

# Copy example files if .env files don't exist
if [ ! -f env/.backend.env ]; then
  if [ -f env/.backend.env.example ]; then
    cp env/.backend.env.example env/.backend.env
    echo "Created env/.backend.env from example"
  else
    echo "Warning: env/.backend.env.example not found"
  fi
fi

if [ ! -f env/.mysql.env ]; then
  if [ -f env/.mysql.env.example ]; then
    cp env/.mysql.env.example env/.mysql.env
    echo "Created env/.mysql.env from example"
  else
    echo "Warning: env/.mysql.env.example not found"
  fi
fi

if [ ! -f env/.nginx.env ]; then
  if [ -f env/.nginx.env.example ]; then
    cp env/.nginx.env.example env/.nginx.env
    echo "Created env/.nginx.env from example"
  fi
fi
ENDSSH

# Start services
echo -e "${BLUE}Starting Docker services...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ubuntu@$VM_IP << 'ENDSSH'
cd ~/artevoke/webapp

# Make sure Docker is running
sudo systemctl start docker || true

# Start services
docker compose up -d --build

# Show status
echo ""
echo "Service status:"
docker compose ps

echo ""
echo "To view logs, run:"
echo "  docker compose logs -f"
ENDSSH

echo -e "${GREEN}✓ Deployment complete!${NC}"
echo -e "${GREEN}Application should be available at: http://$VM_IP${NC}"
echo ""
echo -e "${BLUE}To view logs:${NC}"
echo "  ssh -i $SSH_KEY ubuntu@$VM_IP 'cd ~/artevoke/webapp && docker compose logs -f'"
echo ""
echo -e "${BLUE}To SSH into the VM:${NC}"
echo "  ssh -i $SSH_KEY ubuntu@$VM_IP"

