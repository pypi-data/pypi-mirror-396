terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS provider configuration: Paris region (eu-west-3)
provider "aws" {
  region = "eu-west-3"
}

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

# Fedora Cloud AMI ID for eu-west-3 (France).
# You can get this from the AWS console / Marketplace and paste it here.
variable "fedora_ami_id" {
  description = "Fedora Cloud AMI ID in eu-west-3"
  type        = string
}

# -----------------------------------------------------------------------------
# SSH key pair
# -----------------------------------------------------------------------------

resource "aws_key_pair" "hpc" {
  key_name   = "hpc-key"
  public_key = file("${path.module}/.ssh/t3.small.pub")
}

# -----------------------------------------------------------------------------
# Networking: use default VPC and one default subnet
# -----------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security group for SSH access
resource "aws_security_group" "hpc_ssh" {
  name        = "hpc-ssh"
  description = "SSH access for HPC test node"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------------------------------------------------------
# EC2 instance: Fedora + Slurm head/compute node
# -----------------------------------------------------------------------------

resource "aws_instance" "slurm_head" {
  ami           = var.fedora_ami_id
  instance_type = "t3.small"

  root_block_device {
    volume_size = 30     # You can put 30 to stay strictly Free Tier
    volume_type = "gp3"  # Recommended, free-tier eligible
    delete_on_termination = true
  }

  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.hpc_ssh.id]
  key_name               = aws_key_pair.hpc.key_name

  associate_public_ip_address = true

  user_data = file("${path.module}/cloud-init-slurm-fedora.sh")

  tags = {
    Name = "hpc-slurm-head-fedora"
  }
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "slurm_head_public_ip" {
  description = "Public IP address of the Fedora Slurm head node"
  value       = aws_instance.slurm_head.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the Slurm head node"
  value       = "ssh -i ./.ssh/t3.small fedora@${aws_instance.slurm_head.public_ip}"
}

