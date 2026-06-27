# Payment Transfer API — Project Context

## What this is
A production-grade payment/transfer API built on AWS, designed to demonstrate
cloud-native backend engineering. This is a portfolio project built as part of
a structured learning plan to transition into modern backend engineering roles.

## Architecture
- **API**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (RDS) with SERIALIZABLE transactions for atomic transfers
- **Cache**: Redis (ElastiCache) — cache-aside pattern for account balance reads
- **Queue**: SQS — async audit event processing with dead letter queue
- **Infrastructure**: Terraform — all AWS resources defined as code, no click-ops
- **CI/CD**: GitHub Actions — lint, type check, test, Docker build, ECR push, deploy
- **Observability**: CloudWatch logs (structlog), X-Ray tracing, metric alarms
- **Auth**: JWT with refresh tokens, RBAC (admin/user roles)

## AWS Infrastructure
- VPC (10.0.0.0/16) in eu-west-2 (London)
- Public subnets: payment-api-public-1 (10.0.1.0/24, eu-west-2a),
  payment-api-public-2 (10.0.2.0/24, eu-west-2b)
- Private subnets: payment-api-private-1 (10.0.3.0/24, eu-west-2a),
  payment-api-private-2 (10.0.4.0/24, eu-west-2b)
- Security groups chained: internet → ALB → EC2 (port 8000) → RDS (port 5432)
- IAM role on EC2 (payment-api-ec2-role) — no hardcoded credentials anywhere
- EC2 t3.micro (Amazon Linux 2023, Python 3.11) in public subnet
- RDS db.t3.micro PostgreSQL in private subnet (no public access)
- EC2 and RDS stopped when not in use to minimise cost

## Project Structure
payment-api/

├── app/

│   ├── auth/

│   │   ├── router.py        # /auth routes: login, me, refresh, admin-only

│   │   ├── schemas.py       # LoginRequest, TokenResponse, TokenData, RefreshRequest

│   │   └── utils.py         # authenticate_user against real DB

│   ├── accounts/

│   │   ├── router.py        # /accounts routes: balance, transfer

│   │   ├── schemas.py       # TransferRequest, AccountResponse

│   │   └── service.py       # transfer_funds business logic (SERIALIZABLE)

│   ├── core/

│   │   ├── config.py        # Settings via pydantic-settings, loaded from .env

│   │   ├── security.py      # JWT create/verify, bcrypt password hashing

│   │   ├── logging.py       # structlog JSON configuration

│   │   ├── middleware.py    # RequestIDMiddleware — binds request_id to all logs

│   │   └── decorators.py   # @require_permission decorator factory

│   ├── database.py          # SQLAlchemy engines (standard + SERIALIZABLE), Base, get_db

│   └── models.py            # User and Account ORM models

├── alembic/                 # Database migrations

│   └── versions/            # 6ef77d6ea9e5 — create users and accounts tables

├── tests/

│   ├── test_transfer.py          # Unit tests (4) — mocked DB

│   └── test_transfer_integration.py  # Integration tests (2) — real Postgres via testcontainers

├── main.py                  # FastAPI app entry point, middleware, router registration

├── requirements.txt

├── .env.example

├── CLAUDE.md

└── README.md

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | No | Returns access + refresh token pair |
| POST | /auth/refresh | No | Exchange refresh token for new access token |
| GET | /auth/me | Yes | Returns current user identity |
| GET | /auth/admin-only | Yes (admin) | Admin-only test endpoint |
| GET | /accounts/balance | Yes | Returns current user's account balance |
| POST | /accounts/transfer | Yes | Atomic transfer with SERIALIZABLE isolation |
| GET | /health | No | Liveness check — used by ALB health checks |

## Current status
Week 1 complete. All goals achieved.

### Completed
- JWT authentication with access/refresh tokens, RBAC (admin/user roles)
- require_role dependency and @require_permission decorator
- Alembic migrations — users and accounts tables live in Postgres
- Real database authentication against Postgres (replaced fake users)
- GET /accounts/balance — returns current user's account balance
- POST /accounts/transfer — atomic transfer with SERIALIZABLE isolation,
  row-level locking (with_for_update), and self-transfer guard
- Transfer logic extracted to service layer (app/accounts/service.py)
- Two SQLAlchemy engines — standard and SERIALIZABLE isolation level
- Structlog structured JSON logging with request ID middleware
- Unit tests (4) and integration tests (2) — 6/6 passing
- AWS infrastructure: VPC, subnets, security groups, EC2, RDS
- Deployed and tested live on AWS via EC2 public IP

### Week 2 goals
- Redis caching for balance reads (cache-aside pattern)
- SQS async audit event processing with dead letter queue
- CloudWatch observability dashboard
- Terraform for infrastructure as code
- GitHub Actions CI/CD pipeline
- System design study — Alex Xu Vol 1
- DSA sessions 4 and 5

## Key design decisions
- **FastAPI over Flask** — async-first, type-safe, better for production
- **Decimal not Float** — Float has precision errors unacceptable for financial data
- **SERIALIZABLE isolation** — strongest transaction isolation, prevents phantom reads
- **with_for_update()** — row-level locking, forces concurrent transfers to queue
- **Two engines** — standard engine for reads, SERIALIZABLE engine for transfers
- **Service layer** — transfer business logic in service.py, not in the router
- **Self-transfer guard** — explicitly rejected with 400 before any DB operations
- **Structured JSON logging** — every log line is queryable, correlated by request_id
- **Request ID middleware** — UUID per request, bound to all log lines via contextvars
- **IAM role on EC2** — temporary rotating credentials, no long-term access keys

## Code standards
- Type hints on all functions
- Docstrings on all public functions and classes
- No hardcoded credentials — all config via environment variables
- Tests alongside code — unit tests mock the DB, integration tests use testcontainers
- Meaningful commit messages describing what and why

## Local development
```bash
# Start local Postgres
sudo service postgresql start

# Activate venv
source venv/bin/activate

# Run migrations
alembic upgrade head

# Start API
uvicorn main:app --reload
```

## EC2 management
```bash
# SSH into EC2
ssh -i ~/.ssh/payment-api-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Start app in background
cd payment-api
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Pull latest and restart
git pull origin main
pkill -f uvicorn
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Check logs
tail -f uvicorn.log
```

## Environment variables
| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | 64-char hex string |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime | 15 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime | 1 |
| DATABASE_URL | Postgres connection string | postgresql://user:pass@host:5432/db |