# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name    = "payment-api-vpc"
    Project = "payment-api"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "payment-api-igw"
    Project = "payment-api"
  }
}

# Public Subnet 1
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-2a"

  tags = {
    Name    = "payment-api-public-1"
    Project = "payment-api"
  }
}

# Public Subnet 2
resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-west-2b"

  tags = {
    Name    = "payment-api-public-2"
    Project = "payment-api"
  }
}

# Private Subnet 1
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "eu-west-2a"

  tags = {
    Name    = "payment-api-private-1"
    Project = "payment-api"
  }
}

# Private Subnet 2
resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "eu-west-2b"

  tags = {
    Name    = "payment-api-private-2"
    Project = "payment-api"
  }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name    = "payment-api-public-rt"
    Project = "payment-api"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# EC2 Security Group
resource "aws_security_group" "ec2" {
  name        = "payment-api-ec2-sg"
  description = "EC2 security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "API access"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.your_ip_cidr]
    description = "SSH from my IP only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name    = "payment-api-ec2-sg"
    Project = "payment-api"
  }
}

# IAM Role for EC2
resource "aws_iam_role" "ec2" {
  name = "payment-api-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name    = "payment-api-ec2-role"
    Project = "payment-api"
  }
}

# IAM Policy Attachments
resource "aws_iam_role_policy_attachment" "sqs" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "ec2" {
  name = "payment-api-ec2-profile"
  role = aws_iam_role.ec2.name
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = "ami-0b45ae66668865cd6"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public_1.id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  key_name               = "payment-api-key"

  associate_public_ip_address = true

  tags = {
    Name    = "payment-api-ec2"
    Project = "payment-api"
  }
}