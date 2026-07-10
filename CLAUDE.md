# Payment Transfer API — Project Context

## What this is
A production-grade payment/transfer API built on AWS, designed to demonstrate
cloud-native backend engineering. This is a portfolio project built as part of
a structured learning plan to transition into modern backend engineering roles.

## Architecture
- **API**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL — Neon (production, free tier) / Neon for development too
- **Cache**: Redis — cache-aside pattern for account balance reads
- **Queue**: SQS — async audit event processing with dead letter queue
- **Infrastructure**: Terraform — 15 AWS resources defined as code, no click-ops
- **CI/CD**: GitHub Actions — CI pipeline running (lint, test); CD planned
- **Observability**: CloudWatch logs (structlog), dashboard live, metric alarms live
- **Auth**: JWT with refresh tokens, RBAC (admin/user roles)

## AWS Infrastructure
- VPC (10.0.0.0/16) in eu-west-2 (London)
- Public subnets: payment-api-public-1 (10.0.1.0/24, eu-west-2a),
  payment-api-public-2 (10.0.2.0/24, eu-west-2b)
- Private subnets: payment-api-private-1 (10.0.3.0/24, eu-west-2a),
  payment-api-private-2 (10.0.4.0/24, eu-west-2b)
- Security groups: EC2 accepts port 8000 (from internet) and port 22 (SSH from my IP)
- IAM role on EC2 (payment-api-ec2-role) — SQS, CloudWatch, no hardcoded credentials
- EC2 t3.micro (Amazon Linux 2023, Python 3.11) in public subnet
- RDS deleted — replaced with Neon (free tier, zero cost)
- SQS: payment-api-audit-queue + payment-api-audit-dlq (max 3 receives before DLQ)
- CloudWatch: payment-api-logs log group, dashboard, error rate alarm with SNS
- EC2 stopped when not in use — $0 ongoing cost

## Database Setup
- **Production and development**: Neon PostgreSQL (free tier, always available)
- Everything points at Neon via DATABASE_URL — no local/prod split
- Migrations managed by Alembic

## Project Structure
```
payment-api/
├── app/
│   ├── auth/
│   │   ├── router.py        # /auth routes: login, me, refresh, admin-only
│   │   ├── schemas.py       # LoginRequest, TokenResponse, TokenData, RefreshRequest
│   │   └── utils.py         # authenticate_user against real DB
│   ├── accounts/
│   │   ├── router.py        # /accounts routes: balance (cached), transfer
│   │   ├── schemas.py       # TransferRequest, AccountResponse
│   │   └── service.py       # transfer_funds — SERIALIZABLE, cache invalidation, SQS publish
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings, loaded from .env
│   │   ├── security.py      # JWT create/verify, bcrypt password hashing
│   │   ├── logging.py       # structlog JSON configuration
│   │   ├── middleware.py    # RequestIDMiddleware — binds request_id to all logs
│   │   ├── decorators.py   # @require_permission decorator factory
│   │   ├── cache.py         # Redis cache-aside helpers (get/set/invalidate balance)
│   │   └── queue.py         # SQS publish_audit_event
│   ├── database.py          # SQLAlchemy engines (standard + SERIALIZABLE), Base, get_db
│   └── models.py            # User, Account, AuditEvent ORM models
├── alembic/                 # Database migrations
│   └── versions/            # 6ef77d6ea9e5 (users, accounts), 7eba6ca3c842 (audit_events)
├── scripts/
│   └── worker.py            # SQS consumer — polls queue, writes audit_events, deletes message
├── tests/
│   ├── test_transfer.py          # Unit tests (4) — mocked DB, Redis, SQS
│   └── test_transfer_integration.py  # Integration tests (2) — testcontainers Postgres
├── terraform/               # Infrastructure as code
│   ├── main.tf              # VPC, subnets, security groups, EC2, IAM (+ commented ALB/RDS)
│   ├── variables.tf         # aws_region, your_ip_cidr, db_username, db_password
│   ├── outputs.tf           # vpc_id, public_subnet_ids, ec2_public_ip, ec2_sg_id
│   ├── provider.tf          # AWS provider, required version
│   └── README.md            # Usage instructions, variables, outputs, ALB/RDS migration notes
├── .github/
│   └── workflows/
│       └── ci.yml           # CI: checkout, Python 3.11, install, pytest (Redis service included)
├── main.py                  # FastAPI app entry point, middleware, router registration
├── requirements.txt
├── Dockerfile               # python:3.11-slim, layer caching, uvicorn CMD
├── .dockerignore            # excludes venv, .env, __pycache__, .git, terraform, tests
├── .env.example
├── CLAUDE.md
└── README.md
```

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | No | Returns access + refresh token pair |
| POST | /auth/refresh | No | Exchange refresh token for new access token |
| GET | /auth/me | Yes | Returns current user identity |
| GET | /auth/admin-only | Yes (admin) | Admin-only test endpoint |
| GET | /accounts/balance | Yes | Returns balance (Redis cache-aside, 60s TTL) |
| POST | /accounts/transfer | Yes | Atomic transfer, cache invalidation, SQS audit event |
| GET | /health | No | Liveness check — used by ALB health checks |

## Current status
Week 3 complete. Infrastructure as code, containerisation, and CI all added.

### Completed (Week 1)
- JWT authentication with access/refresh tokens, RBAC (admin/user roles)
- require_role dependency and @require_permission decorator written from scratch
- Alembic migrations — users and accounts tables live in Neon
- Real database authentication against Postgres (replaced fake users)
- GET /accounts/balance endpoint
- POST /accounts/transfer — SERIALIZABLE isolation, row-level locking, self-transfer guard
- Transfer logic extracted to service layer (app/accounts/service.py)
- Two SQLAlchemy engines — standard and SERIALIZABLE
- Structlog structured JSON logging with request ID middleware
- Unit tests (4) and integration tests (2) — 6/6 passing
- AWS infrastructure: VPC, subnets, security groups, EC2
- Production database: Neon (free tier, zero ongoing cost)
- Deployed and tested live on AWS EC2

### Completed (Week 2)
- Redis cache-aside for GET /accounts/balance (60s TTL)
- Cache invalidation on transfer for both accounts
- SQS audit event publishing after successful transfers
- SQS worker (scripts/worker.py) consuming events into audit_events table
- Dead letter queue (max 3 receives)
- AuditEvent model and Alembic migration (7eba6ca3c842)
- CloudWatch agent on EC2 shipping structured logs to payment-api-logs log group

### Completed (Week 3)
- CloudWatch dashboard — request rate, error rate, transfer count widgets
- CloudWatch alarm on error rate with SNS email notification
- Terraform — 15 resources defined as code (VPC, subnets, security groups, EC2, IAM)
- ALB and RDS defined as commented-out Terraform resources for production migration
- Docker — Dockerfile and .dockerignore, 286MB image, runs locally and tested end-to-end
- GitHub Actions CI — 6/6 tests passing on every push to main
- Redis service in CI pipeline, SQS mocked in tests (no AWS dependency in CI)

### Week 4 goals
- GitHub Actions CD — Docker build, ECR push, EC2 deploy on merge to main
- HTTPS via ALB with ACM certificate
- AWS Secrets Manager for production secrets
- User registration and account creation endpoints
- Transaction history endpoint
- DSA sessions 8 and 9 (dynamic programming continued)
- System design — Alex Xu chapters 9-11

### TODOs
- Add exception handler middleware to emit structured error logs for unhandled exceptions
- Update CloudWatch metric filter from `?500` to `{ $.level = "error" }` after above is done

## Key design decisions
- **FastAPI over Flask** — async-first, type-safe, better for production
- **Decimal not Float** — Float has precision errors unacceptable for financial data
- **SERIALIZABLE isolation** — strongest transaction isolation, prevents phantom reads
- **with_for_update()** — row-level locking, forces concurrent transfers to queue
- **Two engines** — standard engine for reads, SERIALIZABLE engine for transfers
- **Service layer** — transfer business logic in service.py, not in the router
- **Self-transfer guard** — explicitly rejected with 400 before any DB operations
- **Structured JSON logging** — every log line queryable, correlated by request_id
- **Request ID middleware** — UUID per request bound to all log lines via contextvars
- **IAM role on EC2** — temporary rotating credentials, no long-term access keys
- **Neon over RDS** — free tier, zero ongoing cost; codebase is DB-agnostic (DATABASE_URL only)
- **Cache-aside pattern** — balance reads check Redis first, invalidated on both accounts on transfer
- **SQS publish after commit** — never publish an event for a transfer that rolled back
- **At-least-once delivery + idempotency** — worker handles duplicate messages safely
- **Dead letter queue** — prevents a bad message blocking the queue after 3 failed attempts
- **Docker layer caching** — requirements.txt copied before source code, dependency layer cached
- **GitHub Actions CI** — every push runs tests automatically, broken code never reaches main
- **Secrets via GitHub Actions secrets** — never hardcoded in YAML
- **Redis service in CI** — real Redis available in pipeline via Docker service container
- **SQS mocked in CI** — publish_audit_event patched in tests, no AWS credentials needed in CI

## Code standards
- Type hints on all functions
- Docstrings on all public functions and classes
- No hardcoded credentials — all config via environment variables
- Tests alongside code — unit tests mock all external dependencies, integration tests use testcontainers
- Meaningful commit messages describing what and why

## Local development
```bash
# Activate venv
source venv/bin/activate

# Run migrations (against Neon)
alembic upgrade head

# Start Redis locally
sudo service redis-server start

# Start API
uvicorn main:app --reload

# Start SQS worker (separate terminal)
python scripts/worker.py

# Watch cache operations
redis-cli monitor

# Run tests
pytest tests/ -v
```

## Docker
```bash
# Build image
docker build -t payment-api .

# Run container
docker run -p 8000:8000 --env-file .env payment-api

# Test
curl http://localhost:8000/health
```

## EC2 demo deployment
```bash
# 1. Start EC2 in AWS console — get new public IP (changes each start)
# 2. Update SSH security group rule to current IP if needed

ssh -i ~/.ssh/payment-api-key.pem ec2-user@EC2_PUBLIC_IP
cd payment-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start redis6
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Test
curl http://EC2_PUBLIC_IP:8000/health

# Share with employer
# http://EC2_PUBLIC_IP:8000/docs

# Stop when done
pkill -f uvicorn
exit
# Then stop EC2 in AWS console
```

## Terraform
```bash
cd terraform
terraform init
terraform plan -var="your_ip_cidr=YOUR_IP/32"
# Review plan carefully before applying
# Do not apply against existing infrastructure without importing or destroying first
```

## Environment variables
| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | 64-char hex string |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime | 15 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime | 1 |
| DATABASE_URL | Neon Postgres connection string | postgresql://...neon.tech/neondb |
| REDIS_URL | Redis connection string | redis://localhost:6379 |
| SQS_QUEUE_URL | SQS audit queue URL | https://sqs.eu-west-2.amazonaws.com/.../payment-api-audit-queue |

## Cost breakdown
| Resource | Status | Monthly cost |
|----------|--------|--------------|
| EC2 t3.micro | Stopped when not in use | $0 (free tier) |
| Neon PostgreSQL | Always on | $0 (free tier) |
| SQS | Pay per use | $0 (well within 1M free requests) |
| CloudWatch | Minimal log volume | ~$0 |
| VPC / networking | Always on | $0 |
| RDS | Deleted | $0 |
| **Total** | | **~$0** |
