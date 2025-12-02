# Variables

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region"
}

variable "project_name" {
  type        = string
  default     = "artevoke"
  description = "Project name for resource naming"
}

variable "instance_type" {
  type        = string
  default     = "g4ad.xlarge"
  description = "EC2 instance type. For GPU support: g4ad.xlarge (8GB VRAM), g4dn.xlarge (16GB VRAM), g4dn.2xlarge (16GB VRAM), g5.xlarge (24GB VRAM). For CPU-only: t3.large, t3.xlarge. Note: GPU instances require a paid AWS account (not free tier restricted)"
}

variable "instance_ami" {
  type        = string
  description = "AMI ID for the EC2 instance (Ubuntu 22.04 LTS recommended)"
  # Default to Ubuntu 22.04 LTS in us-east-1
  # You can override this in terraform.tfvars
  default     = ""
}

variable "key_pair_name" {
  type        = string
  description = "Name of the AWS key pair for SSH access"
}

variable "root_volume_size" {
  type        = number
  default     = 50
  description = "Root volume size in GB (50GB minimum recommended for all services)"
}
