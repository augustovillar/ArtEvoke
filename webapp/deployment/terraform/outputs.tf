# Outputs

output "instance_public_ip" {
  value       = aws_eip.vm.public_ip
  description = "Public IP address of the VM (use this to SSH and access the application)"
}

output "instance_public_dns" {
  value       = aws_instance.vm.public_dns
  description = "Public DNS name of the VM"
}

output "ssh_command" {
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_eip.vm.public_ip}"
  description = "SSH command to connect to the VM"
}

output "application_url" {
  value       = "http://${aws_eip.vm.public_ip}"
  description = "Application URL (HTTP)"
}
