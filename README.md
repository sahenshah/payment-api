# Payment Transfer API

A production-grade, cloud-native payment/transfer API built with FastAPI and AWS, demonstrating modern backend engineering practices end to end.

## Current Status

**Week 1 complete: Auth layer built and tested. Deployment to AWS in progress.**

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

## Tech Stack

**Backend**
- Python 3.10
- FastAPI
- Uvicorn (ASGI server)
- Pydantic / pydantic-settings
- python-jose (JWT)
- passlib + bcrypt (password hashing)

**Database**
- PostgreSQL (Amazon RDS)
- SQLAlchemy (ORM / data access)
- Alembic (migrations)

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
│   │   ├── router.py        # /auth routes: login, me
│   │   ├── schemas.py       # Pydantic models for auth
│   │   └── utils.py         # credential validation against the DB
│   ├── core/
│   │   ├── config.py        # Settings loaded from environment / .env
│   │   └── security.py      # JWT issuance/verification, password hashing
│   └── database.py          # SQLAlchemy engine, session, declarative base
├── tests/
├── main.py                  # FastAPI app entry point
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
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime, in days | `7` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://payment_api:changeme@localhost:5432/payment_api` |

## API Endpoints

| Method | Path | Description | Auth required |
|---|---|---|---|
| `POST` | `/auth/login` | Authenticate with username/password, returns an access + refresh token pair | No |
| `GET` | `/auth/me` | Returns the identity of the currently authenticated user | Yes (bearer access token) |
| `GET` | `/health` | Liveness check | No |

## What's Coming Next

- Accounts model (Postgres + Alembic migrations)
- Atomic transfer endpoint using SERIALIZABLE transactions
- Redis caching for account balance reads (cache-aside pattern)
- SQS-based async audit event processing with a dead letter queue
- Terraform modules for all AWS infrastructure
- GitHub Actions CI/CD pipeline (lint, type check, test, build, deploy)
- Full AWS deployment (VPC, ALB, EC2, RDS, ElastiCache)

---

*Active portfolio project built as part of a structured learning plan to transition into modern backend engineering roles.*
