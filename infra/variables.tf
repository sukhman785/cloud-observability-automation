variable "region" {
  description = "AWS Region"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 Instance Type"
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for Amazon Linux 2023 (us-east-1)"
  default     = "ami-0c1fe732b5494dc14" # Amazon Linux 2023 AMI 2023.6.20250211.0 x86_64 HVM kernel-6.1
}

variable "key_name" {
  description = "Name of the SSH key pair"
  default     = "cloud-observability-key"
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to SSH to the instance"
  default     = "0.0.0.0/0"
}
