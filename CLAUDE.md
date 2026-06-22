# Payment Transfer API — Project Context

## What this is
A production-grade payment/transfer API built on AWS, designed to demonstrate
cloud-native backend engineering. This is a portfolio project built as part of
a structured learning plan to transition into modern backend engineering roles.

## Architecture
- **API**: FastAPI (Python)
- **Database**: PostgreSQL (RDS) with serialisable transactions for atomic transfers
- **Cache**: Redis (ElastiCache) — cache-aside pattern for account balance reads
- **Queue**: SQS — async audit event processing with dead letter queue
- **Infrastructure**: Terraform — all AWS resources defined as code, no click-ops
- **CI/CD**: GitHub Actions — lint, type check, test, Docker build, ECR push, deploy
- **Observability**: CloudWatch logs (structlog), X-Ray tracing, metric alarms
- **Auth**: JWT with refresh tokens, RBAC (admin/user roles)

## AWS Infrastructure
- VPC with public subnets (ALB, EC2) and private subnets (RDS, ElastiCache)
- Security groups chained: internet → ALB → EC2 → RDS/Redis
- IAM roles per service — no hardcoded credentials anywhere

## Current status
Week 1 of build — project structure being set up. Auth API (JWT login, refresh
token, protected routes, RBAC) is the first deliverable.

## Week 1 goals
1. FastAPI project structure set up
2. JWT authentication with login, refresh token, protected routes, RBAC
3. Python decorator for auth middleware
4. Postgres accounts table with Alembic migrations
5. Atomic transfer endpoint using SERIALIZABLE transactions
6. Structured logging with structlog

## Code standards
- Type hints on all functions
- Docstrings on all public functions and classes
- No hardcoded credentials — all config via environment variables
- Tests alongside code — unit tests mock the DB, integration tests use testcontainers
- Meaningful commit messages describing what and why

## Key design decisions to maintain
- FastAPI over Flask — async-first, type-safe, better for production
- Decimal not Float for all money values — Float has precision errors
- SERIALIZABLE isolation for transfers — not READ COMMITTED
- Structured JSON logs — not plain text strings
- IAM roles not access keys for AWS service access