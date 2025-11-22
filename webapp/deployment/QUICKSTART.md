# Quick Start Guide - VM Deployment

## 1. Create AWS Key Pair

```bash
aws ec2 create-key-pair --key-name artevoke-key --query 'KeyMaterial' --output text > ~/.ssh/artevoke-key.pem
chmod 400 ~/.ssh/artevoke-key.pem
```

## 2. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars:
#   - Set key_pair_name = "artevoke-key"
#   - instance_type = "g4dn.xlarge" (16GB VRAM) or "g4dn.2xlarge" for GPU
#   - Or use "t3.large" for CPU-only (no GPU support)
```

## 3. Request vCPU Limit Increase (Required for GPU Instances)

**⚠️ Important**: New AWS accounts have a vCPU limit of 0 for GPU instances. You must request an increase first:

1. Go to [AWS Service Quotas Console](https://console.aws.amazon.com/servicequotas/)
2. Select "Amazon Elastic Compute Cloud (Amazon EC2)"
3. Search for "Running On-Demand G instances"
4. Click "Request quota increase"
5. Request at least 4 vCPUs (for g4dn.xlarge/g4ad.xlarge)
6. Wait for approval (usually within a few hours)

## 4. Deploy Infrastructure

```bash
# Load AWS credentials
source use-credentials.sh
# Or manually:
# export AWS_SHARED_CREDENTIALS_FILE="../.aws-credentials"

terraform init
terraform apply
```

Save the output `instance_public_ip` - you'll need it!

## 5. Deploy Application (Option A: Automated)

```bash
cd ../scripts
./deploy-to-vm.sh <VM_IP> ~/.ssh/artevoke-key.pem
```

## 5. Deploy Application (Option B: Manual)

```bash
# SSH into VM
ssh -i ~/.ssh/artevoke-key.pem ubuntu@<VM_IP>

# On the VM:
cd ~/artevoke
git clone <your-repo-url> .

# Or upload files via SCP from your local machine:
# scp -i ~/.ssh/artevoke-key.pem -r /path/to/webapp/* ubuntu@<VM_IP>:~/artevoke/webapp/

cd webapp

# Setup environment files
cp env/.backend.env.example env/.backend.env
cp env/.mysql.env.example env/.mysql.env
# Edit these files with your values

# Start services
docker compose up -d --build

# Check logs
docker compose logs -f
```

## 6. Access Application

Visit: `http://<VM_IP>`

## That's it! 🎉

Your application is now running on a single VM with:
- Frontend (React)
- Backend (FastAPI) - with GPU support if using GPU instance
- MySQL Database
- Qdrant Vector DB
- Nginx Reverse Proxy

**Note**: If using a GPU instance (g4dn, g5, p3, p4), NVIDIA drivers are automatically installed. The backend service will have GPU access for ML/AI workloads.

## Useful Commands

```bash
# View logs
ssh -i ~/.ssh/artevoke-key.pem ubuntu@<VM_IP> 'cd ~/artevoke/webapp && docker compose logs -f'

# Restart services
ssh -i ~/.ssh/artevoke-key.pem ubuntu@<VM_IP> 'cd ~/artevoke/webapp && docker compose restart'

# Stop services
ssh -i ~/.ssh/artevoke-key.pem ubuntu@<VM_IP> 'cd ~/artevoke/webapp && docker compose down'

# Update application
ssh -i ~/.ssh/artevoke-key.pem ubuntu@<VM_IP> 'cd ~/artevoke/webapp && git pull && docker compose up -d --build'
```

