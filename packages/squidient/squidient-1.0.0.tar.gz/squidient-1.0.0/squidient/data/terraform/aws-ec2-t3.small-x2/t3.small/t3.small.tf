terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-3"
}

variable "fedora_ami_id" {
  description = "Fedora Cloud AMI ID in eu-west-3"
  type        = string
}

# List of compute node hostnames.
# For now: single node. Later: ["slurm-node1", "slurm-node2", ...]
variable "compute_nodes" {
  type    = list(string)
  default = ["slurm-node1"]
}

# Primary compute node name used in slurm.conf generated on the head
locals {
  primary_compute = var.compute_nodes[0]
}

resource "aws_key_pair" "hpc" {
  key_name   = "hpc-key-x2"
  public_key = file("${path.module}/.ssh/t3.small.pub")
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "hpc_ssh" {
  name        = "hpc-ssh-x2"
  description = "SSH + internal comms for HPC cluster"
  vpc_id      = data.aws_vpc.default.id

  # SSH from everywhere (OK for tests, not prod)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Head <-> compute comms (Slurm/MPI/NFS): allow all inside the VPC
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  # Outbound: allow everything (updates, git, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------- HEAD -------------------------
resource "aws_instance" "slurm_head" {
  ami           = var.fedora_ami_id
  instance_type = "t3.small"

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }

  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.hpc_ssh.id]
  key_name               = aws_key_pair.hpc.key_name

  associate_public_ip_address = true

  # Head gets a single "primary" compute hostname for its slurm.conf
  user_data = templatefile(
    "${path.module}/cloud-init-slurm-fedora.sh",
    {
      ROLE             = "head"
      HEAD_HOSTNAME    = "slurm-head"
      COMPUTE_HOSTNAME = local.primary_compute
      HEAD_PRIVATE_IP  = "0.0.0.0"
      COMPUTE_NODE_LIST  = join(" ", var.compute_nodes) 
    }
  )

  tags = {
    Name = "hpc-slurm-head-fedora"
  }
}

# -------------------- COMPUTES (for_each) ------------------------
resource "aws_instance" "slurm_compute" {
  for_each      = toset(var.compute_nodes)
  ami           = var.fedora_ami_id
  instance_type = "t3.small"

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }

  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.hpc_ssh.id]
  key_name               = aws_key_pair.hpc.key_name

  associate_public_ip_address = true

  depends_on = [aws_instance.slurm_head]

  user_data = templatefile(
    "${path.module}/cloud-init-slurm-fedora.sh",
    {
      ROLE             = "compute"
      HEAD_HOSTNAME    = "slurm-head"
      COMPUTE_HOSTNAME = each.key
      HEAD_PRIVATE_IP  = aws_instance.slurm_head.private_ip
      COMPUTE_NODE_LIST = join(" ", var.compute_nodes)
    }
  )

  tags = {
    Name = "hpc-${each.key}-fedora"
  }
}

# -------------------- OUTPUTS ------------------------

output "head_public_ip" {
  description = "Public IP of the Slurm head node"
  value       = aws_instance.slurm_head.public_ip
}

output "compute_public_ips" {
  description = "Public IPs of compute nodes (by hostname)"
  value       = { for name, inst in aws_instance.slurm_compute : name => inst.public_ip }
}

output "ssh_head" {
  value = "ssh -i ./.ssh/t3.small fedora@${aws_instance.slurm_head.public_ip}"
}

output "ssh_compute_examples" {
  value = {
    for name, inst in aws_instance.slurm_compute :
    name => "ssh -i ./.ssh/t3.small fedora@${inst.public_ip}"
  }
}

