# AWS VM Deployment Guide for ArtEvoke

Deploy ArtEvoke to a single AWS EC2 instance. Simple, fast, and cost-effective.

## Architecture

- **Single EC2 Instance**: Runs all services (frontend, backend, MySQL, Qdrant, Nginx)
- **GPU Support**: Configured for GPU instances (g4dn, g5, p3, p4) with NVIDIA drivers
- **Docker & Docker Compose**: All services run in containers with GPU passthrough
- **Public IP**: Directly accessible from the internet
- **Security Group**: Allows SSH (22), HTTP (80), HTTPS (443)

## Prerequisites

```bash
# Check installations
aws --version
terraform version

# Verify AWS credentials
aws sts get-caller-identity
```

### AWS Credentials Setup

1. Create AWS credentials file (e.g., `~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY_ID
   aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
   ```

2. Create a key pair in AWS (for SSH access):
   ```bash
   # Create key pair in AWS Console or via CLI
   aws ec2 create-key-pair --key-name artevoke-key --query 'KeyMaterial' --output text > ~/.ssh/artevoke-key.pem
   chmod 400 ~/.ssh/artevoke-key.pem
   ```

## Deployment Steps

### Step 1: Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

**Required in `terraform.tfvars`:**
- `key_pair_name`: Name of your AWS key pair (must exist in AWS)
- `instance_type`: EC2 instance type
  - **CPU-only instances**: `t3.large`, `t3.xlarge` (no GPU support)
- `aws_region`: AWS region (default: us-east-1)

**⚠️ Important**: GPU instances require:
1. **Paid AWS account** with billing enabled and a valid payment method on file
2. **vCPU limit increase** - New accounts have a vCPU limit of 0 for GPU instances

**To request vCPU limit increase:**
1. Go to [AWS Service Quotas Console](https://console.aws.amazon.com/servicequotas/)
2. Select "Amazon Elastic Compute Cloud (Amazon EC2)"
3. Search for "Running On-Demand G instances" (for g4dn, g4ad) or "Running On-Demand P instances" (for p3, p4)
4. Click "Request quota increase"
5. Request at least 4 vCPUs (for g4dn.xlarge) or 8 vCPUs (for larger instances)
6. Wait for approval (usually within a few hours, sometimes instant)

**Alternative**: Use the AWS CLI to check current limits:
```bash
aws service-quotas list-service-quotas --service-code ec2 --region us-east-1 | grep -i "g instance\|p instance"
```

### Step 2: Create Infrastructure

```bash
cd terraform

# Load AWS credentials
source use-credentials.sh
# Or manually:
# export AWS_SHARED_CREDENTIALS_FILE="../.aws-credentials"

terraform init
terraform plan
terraform apply
```

**What Terraform creates:**
- EC2 instance (Ubuntu 22.04 LTS)
- Security group (SSH, HTTP, HTTPS)
- Elastic IP (static public IP)
- Installs Docker and Docker Compose automatically

**Save outputs:**
- `instance_public_ip`: Your VM's public IP address
- `ssh_command`: Command to SSH into the VM
- `application_url`: URL to access your application

### Step 3: SSH into the VM

```bash
# Get the SSH command from Terraform output
cd terraform
terraform output ssh_command

# Or manually:
ssh -i ~/.ssh/your-key.pem ubuntu@<PUBLIC_IP>
```

### Step 4: Deploy Application on VM

Once connected to the VM:

```bash
# Create the project directory structure
mkdir -p ~/artevoke/webapp

# Fix permissions (if directory was created with wrong ownership)
sudo chown -R ubuntu:ubuntu ~/artevoke
chmod 755 ~/artevoke

# Clone your repository (or upload your code)
cd ~/artevoke
git clone <your-repo-url> .

# Or if you have the code locally, use rsync (RECOMMENDED - much faster):
# From your local machine (from webapp directory):
cd webapp/deployment/scripts
./fast-deploy.sh <PUBLIC_IP> ~/.ssh/your-key.pem

# Or use rsync directly (fastest, incremental transfers):
rsync -avz --progress \
  -e "ssh -i ~/.ssh/your-key.pem" \
  --exclude='node_modules' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.git' --exclude='build' --exclude='*.snapshot' \
  --exclude='data/static' --exclude='env/.backend.env' \
  /path/to/webapp/ ubuntu@<PUBLIC_IP>:~/artevoke/webapp/

# Or use SCP (slower, transfers everything):
scp -i ~/.ssh/your-key.pem -r /path/to/webapp/* ubuntu@<PUBLIC_IP>:~/artevoke/webapp/

# Navigate to webapp directory
cd webapp

# Start all services with Docker Compose
docker compose up -d --build

# Check logs
docker compose logs -f
```

### Step 5: Access Your Application

```bash
# Get the public IP
cd terraform
terraform output application_url
```

Visit `http://<PUBLIC_IP>` in your browser.

## Configuration

### Environment Variables

Create `.env` files in `webapp/env/`:

**`env/.backend.env`:**
```bash
DB_USER=admin
DB_PASSWORD=your_secure_password
DB_HOST=mysql
DB_PORT=3306
DB_NAME=artevoke
JWT_SECRET=your_jwt_secret_min_32_chars
MARITACA_API_KEY=your_maritaca_key
STATIC_DIR=/app/data/static
DATA_DIR=/app/data
```

**`env/.mysql.env`:**
```bash
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=artevoke
MYSQL_USER=admin
MYSQL_PASSWORD=your_secure_password
```

### Nginx Configuration

The application uses Nginx as a reverse proxy. Configuration files are in `webapp/nginx/`:
- `nginx-local.conf`: For HTTP (port 80)
- `nginx-prod.conf`: For HTTPS (port 443) - requires SSL certificates

## Common Commands

### View Logs
```bash
# On the VM
cd ~/artevoke/webapp
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
docker compose logs -f qdrant
```

### Restart Services
```bash
cd ~/artevoke/webapp
docker compose restart
```

### Stop Services
```bash
cd ~/artevoke/webapp
docker compose down
```

### Update Application
```bash
# On the VM
cd ~/artevoke/webapp
git pull
docker compose up -d --build
```

### Check Service Status
```bash
cd ~/artevoke/webapp
docker compose ps
```

## Troubleshooting

### Can't SSH into VM
1. Check security group allows SSH (port 22) from your IP
2. Verify key pair name matches in `terraform.tfvars`
3. Check key file permissions: `chmod 400 ~/.ssh/your-key.pem`

### Services won't start
1. Check Docker is running: `sudo systemctl status docker`
2. Check logs: `docker compose logs`
3. Verify environment variables are set correctly
4. Check disk space: `df -h`

### Can't access application
1. Check security group allows HTTP (port 80) and HTTPS (port 443)
2. Verify services are running: `docker compose ps`
3. Check Nginx logs: `docker compose logs nginx`
4. Verify public IP is correct

### Database connection issues
1. Check MySQL container is running: `docker compose ps mysql`
2. Verify database credentials in `.env` files
3. Check MySQL logs: `docker compose logs mysql`

### Permission denied when creating directories
If you get "Permission denied" when trying to create directories in `~/artevoke`:

```bash
# Check current permissions
ls -la ~/artevoke
ls -ld ~/artevoke

# Fix ownership (if directory is owned by root)
sudo chown -R ubuntu:ubuntu ~/artevoke

# Fix permissions
chmod 755 ~/artevoke

# Now create the directory
mkdir -p ~/artevoke/webapp
```

**Alternative: Start fresh**
```bash
# Remove directory if it has wrong permissions
sudo rm -rf ~/artevoke

# Create with correct permissions
mkdir -p ~/artevoke/webapp
sudo chown -R ubuntu:ubuntu ~/artevoke
```


```bash
cd terraform

# Load AWS credentials first
source use-credentials.sh
# Or manually:
# export AWS_SHARED_CREDENTIALS_FILE="../.aws-credentials"

terraform destroy
```

## Next Steps

- Set up SSL/TLS certificates (Let's Encrypt)
- Configure custom domain with Route 53
- Set up automated backups
- Configure CloudWatch monitoring
- Set up monitoring and alerts

## Support

For issues, check:
- Docker logs: `docker compose logs`
- System logs: `journalctl -u docker`
- Terraform state: `terraform show`
