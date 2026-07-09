# Payment API — Terraform Infrastructure

Defines all AWS infrastructure for the payment API as code.

## Resources Created

- VPC (10.0.0.0/16) with public and private subnets across two AZs
- Internet Gateway and public route table
- EC2 security group (port 8000 public, port 22 from your IP only)
- IAM role for EC2 with SQS and CloudWatch permissions
- EC2 t3.micro instance (Amazon Linux 2023)

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- An existing EC2 key pair named `payment-api-key`

## Usage

```bash
terraform init
terraform plan -var="your_ip_cidr=YOUR_IP/32"
terraform apply -var="your_ip_cidr=YOUR_IP/32"
terraform destroy -var="your_ip_cidr=YOUR_IP/32"
```

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| aws_region | AWS region | eu-west-2 |
| your_ip_cidr | Your IP in CIDR notation for SSH | required |

## Outputs

| Output | Description |
|--------|-------------|
| vpc_id | VPC ID |
| public_subnet_ids | Public subnet IDs |
| ec2_public_ip | EC2 public IP address |
| ec2_security_group_id | EC2 security group ID |

## Notes

- Do not run terraform apply against the existing infrastructure
  without first importing existing resources or destroying them
- State file is local — move to S3 backend for team environments

## Adding an ALB (Production)

The EC2 security group currently allows port 8000 from the internet directly.
To add an ALB for production:

1. Uncomment the ALB security group in main.tf
2. Update the EC2 security group to only accept traffic from the ALB SG
3. Add aws_lb, aws_lb_listener, and aws_lb_target_group resources
4. No application code changes required — the app already listens on 0.0.0.0:8000