# Payment Transfer API

A production-grade, cloud-native payment/transfer API built with FastAPI and AWS, demonstrating modern backend engineering practices end to end.

## Live Deployment

The API runs on AWS EC2 (eu-west-2, London) and is spun up on demand for demos and testing. The database runs on Neon PostgreSQL (free tier, always available).

To request a live demo: start EC2, share the public IP.

API docs: `http://EC2_PUBLIC_IP:8000/docs`
Health check: `http://EC2_PUBLIC_IP:8000/health`

> **Deployment note:** To minimise AWS costs, this portfolio deployment serves the API directly from a single EC2 instance rather than behind an Application Load Balancer (ALB). The application is designed so an ALB can be introduced for production with minimal infrastructure changes, providing HTTPS termination, health checks, path-based routing, and improved traffic management without requiring application code changes.

## Current Status

**Week 3 complete: Auth layer, database layer, transfer endpoint, structured logging, tests, infrastructure as code, containerisation, CI, and observability all built, tested, and deployed to AWS.**

- JWT authentication with access and refresh tokens ✅
- Role-based access control (RBAC) ✅
- Atomic transfer endpoint with SERIALIZABLE isolation ✅
- Structured JSON logging with request ID middleware ✅
- Unit tests (4) and integration tests (2) — 6/6 passing ✅
- Database migrated from Amazon RDS to Neon PostgreSQL for cost-efficient portfolio hosting ✅ 
- Zero ongoing AWS cost — EC2 stopped when not in use, RDS deleted ✅
- Deployed to AWS — VPC, EC2 live ✅
- Redis cache-aside caching for balance reads, with invalidation on transfer ✅
- SQS async audit event processing, with a worker and dead letter queue ✅
- CloudWatch shipping structured logs from EC2 ✅
- Terraform infrastructure as code — VPC, subnets, security groups, EC2, IAM (15 resources) ✅
- Docker containerised deployment — 286MB image, runs locally ✅
- GitHub Actions CI pipeline — 6/6 tests passing on every push ✅
- CloudWatch dashboard with request rate, error rate, and transfer count widgets ✅
- CloudWatch alarm on error rate with SNS email notification ✅

## Architecture Overview

| Component | Description |
|---|---|
| **API** | FastAPI (Python), async-first and type-safe |
| **Database** | PostgreSQL (hosted on Neon), SERIALIZABLE transactions for atomic transfers |
| **Cache** | Redis, cache-aside pattern for account balance reads |
| **Queue** | SQS, async audit event processing with a dead letter queue |
| **Infrastructure** | AWS EC2, VPC, IAM, SQS and CloudWatch. Direct EC2 deployment for cost efficiency; designed to support an ALB for production deployments | 
| **CI/CD** | GitHub Actions — CI pipeline running (lint, test); CD planned (Docker build, ECR push, deploy) |
| **Observability** | CloudWatch log shipping live (structlog); dashboard, X-Ray tracing, metric alarms planned |
| **Auth** | JWT with refresh tokens, RBAC (admin/user roles) |

## AWS Infrastructure

- VPC (`10.0.0.0/16`) with public and private subnets across two AZs
- Security groups: EC2 accepts traffic on port 8000 (API) and port 22 (SSH)
- IAM role on EC2 — no hardcoded credentials anywhere
- EC2 stopped when not in use — $0 ongoing cost
- Portfolio deployment uses Neon PostgreSQL to eliminate database hosting costs
- Application remains PostgreSQL-compatible and can migrate to Amazon RDS by updating `DATABASE_URL` and applying the existing Alembic migrations

## Cost

| Resource | Status | Monthly cost |
|----------|--------|--------------|
| EC2 t3.micro | Stopped when not in use | $0 (free tier) |
| Neon PostgreSQL | Always on | $0 (free tier) |
| VPC / networking | Always on | $0 |
| **Total** | | **$0** |

## Tech Stack

**Backend**
- Python 3.11+
- FastAPI
- Uvicorn (ASGI server)
- Pydantic / pydantic-settings
- python-jose (JWT)
- passlib + bcrypt (password hashing)

**Database**
- PostgreSQL
- SQLAlchemy (ORM / data access)
- Alembic (migrations)
- Neon PostgreSQL (portfolio deployment, free tier)

> **Note:** The portfolio deployment uses Neon PostgreSQL to eliminate ongoing infrastructure costs. The application is database-agnostic—migrating to Amazon RDS for a production deployment only requires updating the `DATABASE_URL` environment variable and running `alembic upgrade head` against the new database.

**Cache**
- Redis (cache-aside pattern)

**Queue**
- Amazon SQS (audit events, DLQ)

**Cloud**
- AWS (VPC, EC2, SQS, CloudWatch, IAM)

**IaC**
- Terraform (15 resources defined)

**CI/CD**
- GitHub Actions (CI pipeline running)

**Containerisation**
- Docker

**Observability**
- structlog (structured JSON logging)
- CloudWatch (log shipping live)
- X-Ray — *planned*

## Project Structure

```
payment-api/
├── app/
│   ├── auth/
│   │   ├── router.py        # /auth routes: login, me, refresh, admin-only
│   │   ├── schemas.py       # LoginRequest, TokenResponse, TokenData, RefreshRequest
│   │   └── utils.py         # authenticate_user against real DB
│   ├── accounts/
│   │   ├── router.py        # /accounts routes: balance, transfer
│   │   ├── schemas.py       # TransferRequest, AccountResponse
│   │   └── service.py       # transfer_funds business logic
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── security.py      # JWT utilities, password hashing
│   │   ├── logging.py       # structlog JSON configuration
│   │   ├── middleware.py    # RequestIDMiddleware
│   │   ├── decorators.py   # @require_permission decorator
│   │   ├── cache.py         # Redis cache-aside helpers for balance reads
│   │   └── queue.py         # SQS publish helper for audit events
│   ├── database.py          # SQLAlchemy engines, sessions, Base
│   └── models.py            # User, Account, and AuditEvent ORM models
├── alembic/                 # Database migrations, incl. audit_events table
├── scripts/
│   └── worker.py            # SQS consumer — processes audit events, idempotent
├── tests/
│   ├── test_transfer.py          # Unit tests (4)
│   └── test_transfer_integration.py  # Integration tests (2)
├── terraform/                # Infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── provider.tf
│   └── README.md
├── .github/
│   └── workflows/
│       └── ci.yml           # Lint and test on every push
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
└── README.md
```

## How to Run Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/sahenshah/payment-api.git
   cd payment-api
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in the values:

   ```bash
   cp .env.example .env
   ```

5. Generate a secret key for `SECRET_KEY`:

   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

6. Run the API:

   ```bash
   uvicorn main:app --reload
   ```

7. Open the interactive API docs:

   ```
   http://localhost:8000/docs
   ```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Secret used to sign and verify JWTs | `b6f1...` (64-char hex, generate with the command above) |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime, in minutes | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime, in days | `1` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://payment_api:changeme@localhost:5432/payment_api` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SQS_QUEUE_URL` | Amazon SQS connection string | `https://sqs.eu-west-2.amazonaws.com/YOUR_ACCOUNT_ID/payment-api-audit-queue` |

## API Endpoints

| Method | Path | Description | Auth required |
|--------|------|-------------|---------------|
| `POST` | `/auth/login` | Authenticate, returns access + refresh token pair | No |
| `POST` | `/auth/refresh` | Exchange refresh token for new access token | No |
| `GET` | `/auth/me` | Returns current user identity | Yes — access token |
| `GET` | `/auth/admin-only` | Admin-only test endpoint | Yes — admin role |
| `GET` | `/accounts/balance` | Returns account balance (Redis cache-aside, 60s TTL) | Yes — access token |
| `POST` | `/accounts/transfer` | Atomic transfer, cache invalidation, publishes SQS audit event | Yes — access token |
| `GET` | `/health` | Liveness check | No |

## Key Design Decisions

- **Infrastructure-agnostic deployment** — FastAPI is exposed directly from EC2 to minimise portfolio costs. An ALB can be introduced for production without any application code changes, providing HTTPS termination, health checks, and horizontal scaling.
- **Database portability** — application code is PostgreSQL-compatible and database-agnostic; the portfolio deployment uses Neon, while Amazon RDS can be adopted for production with only a DATABASE_URL change and running migrations.
- **SERIALIZABLE isolation + with_for_update()** — prevents race conditions under concurrent load. SERIALIZABLE ensures transaction-level consistency, row-level locking forces concurrent transfers to queue rather than conflict.
- **Two SQLAlchemy engines** — standard engine for reads, SERIALIZABLE engine for transfers only.
- **JWT type claim** — access and refresh tokens are structurally identical but the type claim prevents refresh tokens being used on protected endpoints.
- **IAM role on EC2** — temporary rotating credentials, no long-term access keys stored on the instance.
- **Decimal not Float** for all money values — Float has precision errors unacceptable in financial systems.
- **Service layer pattern** — transfer business logic in service.py not in the router.
- **Self-transfer guard** — explicitly rejected before any DB operations.
- **Cache-aside pattern** — balance reads check Redis first, invalidated on both accounts after every transfer.
- **SQS publish after commit** — audit events are never published for transfers that rolled back.
- **At-least-once delivery** handled with idempotency in the worker — duplicate messages produce no side effects.
- **Dead letter queue** — prevents a bad message from blocking the queue after 3 failed attempts.
- **Structured JSON logging + CloudWatch** — every log line is queryable and correlated by request_id, centralised in CloudWatch for search and alerting.
- **Request ID middleware** — UUID per request bound to all log lines via contextvars.
- **Docker layer caching** — requirements.txt copied before source code so the dependency layer is cached and only rebuilds when requirements change.
- **GitHub Actions CI** — every push runs lint and tests automatically, so broken code never reaches main undetected.
- **Secrets via GitHub Actions secrets** — never hardcoded in YAML.
- **Redis service in CI** — spun up as a Docker container in the pipeline so integration tests have a real Redis available.
- **SQS mocked in CI** — publish_audit_event patched in tests so CI has no AWS dependency.

## What's Coming Next

- GitHub Actions CD — Docker build, ECR push, EC2 deploy on merge to main
- HTTPS via ALB with ACM certificate
- AWS Secrets Manager for production secrets
- User registration and account creation endpoints
- Transaction history endpoint

---

*Active portfolio project built as part of a structured learning plan to transition into modern backend engineering roles.*