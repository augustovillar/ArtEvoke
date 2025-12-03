terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Get Ubuntu 22.04 LTS AMI if not specified
data "aws_ami" "ubuntu" {
  count       = var.instance_ami == "" ? 1 : 0
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get default subnet in us-east-1a
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "availability-zone"
    values = ["us-east-1a"]
  }
}

# Security group for EC2 instance
resource "aws_security_group" "vm" {
  name        = "${var.project_name}-vm-sg"
  description = "Security group for ArtEvoke VM"
  vpc_id      = data.aws_vpc.default.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH"
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound"
  }

  tags = {
    Name = "${var.project_name}-vm-sg"
  }
}

# Elastic IP for static IP address
resource "aws_eip" "vm" {
  instance = aws_instance.vm.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-vm-ip"
  }
}

# EC2 instance
resource "aws_instance" "vm" {
  ami                    = var.instance_ami != "" ? var.instance_ami : data.aws_ami.ubuntu[0].id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.vm.id]
  availability_zone      = "us-east-1a"
  subnet_id              = data.aws_subnets.default.ids[0]
  
  # Metadata options
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }

  # User data script to install Docker, NVIDIA drivers, and setup
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Update system
              export DEBIAN_FRONTEND=noninteractive
              apt-get update
              apt-get upgrade -y
              
              # Install basic dependencies
              apt-get install -y \
                  ca-certificates \
                  curl \
                  gnupg \
                  lsb-release \
                  git \
                  build-essential
              
              # Install Docker
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              chmod a+r /etc/apt/keyrings/docker.gpg
              
              echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
              
              apt-get update
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              
              # Add ubuntu user to docker group
              usermod -aG docker ubuntu
              
              # Install Docker Compose (standalone)
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              # Create directory for application with correct ownership
              mkdir -p /home/ubuntu/artevoke
              chown -R ubuntu:ubuntu /home/ubuntu/artevoke
              chmod -R 755 /home/ubuntu/artevoke
              
              # Log completion
              echo "Docker and Docker Compose installed successfully" >> /var/log/user-data.log
              echo "User data script completed at $(date)" >> /var/log/user-data.log
              EOF

  # Enable detailed monitoring (optional, can be removed to save costs)
  monitoring = false

  # Root volume
  root_block_device {
    volume_type = "gp3"
    volume_size = var.root_volume_size
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-vm"
  }
}
