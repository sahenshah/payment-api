variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "your_ip_cidr" {
  description = "Your IP address in CIDR notation for SSH access"
  type        = string
}
