output "public_ip" {
  value = aws_instance.app_server.public_ip
}

output "instance_id" {
  value = aws_instance.app_server.id
}

output "ssh_command" {
  value = "ssh -i ${path.module}/cloud-observability-key.pem ec2-user@${aws_instance.app_server.public_ip}"
}
