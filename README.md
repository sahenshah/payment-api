# Payment Transfer API

A production-grade, cloud-native payment/transfer API built with FastAPI and AWS, demonstrating modern backend engineering practices end to end.

## Live Deployment

The API runs on AWS EC2 (eu-west-2, London) and is spun up on demand for demos and testing. The database runs on Neon PostgreSQL (free tier, always available).

To request a live demo: start EC2, share the public IP.

API docs: `http://EC2_PUBLIC_IP:8000/docs`
Health check: `http://EC2_PUBLIC_IP:8000/health`

## Current Status

**Week 1 complete: Auth layer, database layer, transfer endpoint, structured logging, and tests all built, tested, and deployed to AWS.**

- JWT authentication with access and refresh tokens ✅
- Role-based access control (RBAC) ✅
- Atomic transfer endpoint with SERIALIZABLE isolation ✅
- Structured JSON logging with request ID middleware ✅
- Unit tests (4) and integration tests (2) — 6/6 passing ✅
- Production database migrated from RDS to Neon (free tier, zero ongoing cost) ✅
- Zero ongoing AWS cost — EC2 stopped when not in use, RDS deleted ✅
- Deployed to AWS — VPC, EC2 live ✅

## Architecture Overview

| Component | Description |
|---|---|
| **API** | FastAPI (Python), async-first and type-safe |
| **Database** | PostgreSQL (RDS), with SERIALIZABLE transactions for atomic transfers |
| **Cache** | Redis (ElastiCache), cache-aside pattern for account balance reads |
| **Queue** | SQS, async audit event processing with a dead letter queue |
| **Infrastructure** | Terraform, all AWS resources defined as code, no click-ops |
| **CI/CD** | GitHub Actions — lint, type check, test, Docker build, ECR push, deploy |
| **Observability** | CloudWatch logs (structlog), X-Ray tracing, metric alarms |
| **Auth** | JWT with refresh tokens, RBAC (admin/user roles) |

## AWS Infrastructure

- VPC (`10.0.0.0/16`) with public and private subnets across two AZs
- Security groups: EC2 accepts traffic on port 8000 and port 22 (SSH)
- IAM role on EC2 — no hardcoded credentials anywhere
- EC2 stopped when not in use — $0 ongoing cost
- RDS deleted — replaced with Neon PostgreSQL (free tier)

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
- Neon (production hosting, free tier)
- Local PostgreSQL 14 (development)

> **Note:** The production database uses Neon PostgreSQL (free tier) as this is a personal portfolio project. The codebase is database-agnostic — migrating to Amazon RDS for a production deployment requires only a `DATABASE_URL` change and running `alembic upgrade head` against the new instance.

**Cache**
- Redis (Amazon ElastiCache) — *planned*

**Queue**
- Amazon SQS — *planned*

**Cloud**
- AWS (VPC, EC2, ALB, RDS, ElastiCache, SQS, IAM)

**IaC**
- Terraform — *planned*

**CI/CD**
- GitHub Actions — *planned*

**Observability**
- structlog (structured JSON logging)
- CloudWatch, X-Ray — *planned*

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
│   │   └── decorators.py   # @require_permission decorator
│   ├── database.py          # SQLAlchemy engines, sessions, Base
│   └── models.py            # User and Account ORM models
├── alembic/                 # Database migrations
├── tests/
│   ├── test_transfer.py          # Unit tests (4)
│   └── test_transfer_integration.py  # Integration tests (2)
├── main.py
├── requirements.txt
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

## API Endpoints

| Method | Path | Description | Auth required |
|--------|------|-------------|---------------|
| `POST` | `/auth/login` | Authenticate, returns access + refresh token pair | No |
| `POST` | `/auth/refresh` | Exchange refresh token for new access token | No |
| `GET` | `/auth/me` | Returns current user identity | Yes — access token |
| `GET` | `/auth/admin-only` | Admin-only test endpoint | Yes — admin role |
| `GET` | `/accounts/balance` | Returns current user account balance | Yes — access token |
| `POST` | `/accounts/transfer` | Atomic transfer between accounts | Yes — access token |
| `GET` | `/health` | Liveness check | No |

## Key Design Decisions

- **SERIALIZABLE transactions** for all balance operations — prevents race conditions under concurrent load
- **JWT type claim** — access and refresh tokens are structurally identical but the type claim prevents refresh tokens being used on protected endpoints
- **Chained security groups** — EC2 only accepts traffic from the ALB security group, RDS only accepts traffic from the EC2 security group. No direct internet access to either.
- **IAM role on EC2** — temporary rotating credentials, no long-term access keys stored on the instance
- **Decimal not Float** for all money values — Float has precision errors unacceptable in financial systems
- **SERIALIZABLE isolation level** for all transfer operations — prevents phantom reads
- **with_for_update() row-level locking** — forces concurrent transfers to queue
- **Two SQLAlchemy engines** — standard for reads, SERIALIZABLE for transfers
- **Service layer pattern** — transfer business logic in service.py not in router
- **Self-transfer guard** — explicitly rejected before any DB operations
- **Structured JSON logging** — every log line queryable, correlated by request_id
- **Request ID middleware** — UUID per request bound to all log lines

## What's Coming Next

- Redis caching for account balance reads (cache-aside pattern)
- SQS-based async audit event processing with a dead letter queue
- Terraform modules for all AWS infrastructure
- GitHub Actions CI/CD pipeline (lint, type check, test, build, deploy)
- CloudWatch observability dashboard and X-Ray tracing

---

*Active portfolio project built as part of a structured learning plan to transition into modern backend engineering roles.*