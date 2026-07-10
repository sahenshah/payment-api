variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "your_ip_cidr" {
  description = "Your IP address in CIDR notation for SSH access"
  type        = string
}

# Used when switching from Neon to RDS
variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "payment_api"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
  default     = ""
}