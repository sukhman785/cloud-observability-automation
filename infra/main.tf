terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# 1. IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "cloud_observability_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_policy" {
  name = "cloud_observability_policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "cloud_observability_profile"
  role = aws_iam_role.ec2_role.name
}

# 2. Security Group
resource "aws_security_group" "app_sg" {
  name        = "cloud_observability_sg"
  description = "Allow SSH and outbound traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Key Pair (Generate a new one for this demo)
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "kp" {
  key_name   = var.key_name
  public_key = tls_private_key.pk.public_key_openssh
}

resource "local_file" "ssh_key" {
  filename        = "${path.module}/cloud-observability-key.pem"
  content         = tls_private_key.pk.private_key_pem
  file_permission = "0400"
}

# 4. EC2 Instance
resource "aws_instance" "app_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.kp.key_name

  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data_base64 = base64gzip(templatefile("${path.module}/user_data.sh.tftpl", {
    requirements_txt = file("${path.root}/../requirements.txt")
    generator_py     = file("${path.root}/../src/generator.py")
    processor_py     = file("${path.root}/../src/processor.py")
    alerts_py        = file("${path.root}/../src/alerts.py")
    actions_py       = file("${path.root}/../src/actions.py")
    main_py          = file("${path.root}/../src/main.py")
  }))

  tags = {
    Name = "CloudObservabilityPlatform"
  }
}
