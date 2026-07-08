output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "ec2_public_ip" {
  description = "EC2 public IP address"
  value       = aws_instance.main.public_ip
}

output "ec2_security_group_id" {
  description = "EC2 security group ID"
  value       = aws_security_group.ec2.id
}