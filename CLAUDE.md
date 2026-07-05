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
- **Infrastructure**: Terraform (planned) — AWS resources as code
- **CI/CD**: GitHub Actions (planned) — lint, type check, test, Docker build, deploy
- **Observability**: structlog JSON logging shipped to CloudWatch, dashboard (planned)
- **Auth**: JWT with refresh tokens, RBAC (admin/user roles)

## AWS Infrastructure
- VPC (10.0.0.0/16) in eu-west-2 (London)
- Public subnets: payment-api-public-1 (10.0.1.0/24, eu-west-2a),
  payment-api-public-2 (10.0.2.0/24, eu-west-2b)
- Private subnets: payment-api-private-1 (10.0.3.0/24, eu-west-2a),
  payment-api-private-2 (10.0.4.0/24, eu-west-2b)
- Security groups: EC2 accepts port 8000 (from internet during dev) and port 22 (SSH from my IP)
- IAM role on EC2 (payment-api-ec2-role): RDS, SQS, and CloudWatch agent policies
- EC2 t3.micro (Amazon Linux 2023, Python 3.11) in public subnet
- RDS deleted — replaced with Neon (free tier, zero cost)
- SQS: payment-api-audit-queue + payment-api-audit-dlq (max 3 receives before DLQ)
- CloudWatch: payment-api-logs log group receiving structured logs via CloudWatch agent
- EC2 stopped when not in use — near-zero ongoing cost

## Database Setup
- **Production and development**: Neon PostgreSQL (free tier, always available)
- Migrations managed by Alembic
- Everything points at Neon via DATABASE_URL — no local/prod split

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
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── security.py      # JWT create/verify, bcrypt password hashing
│   │   ├── logging.py       # structlog JSON configuration
│   │   ├── middleware.py    # RequestIDMiddleware
│   │   ├── decorators.py   # @require_permission decorator
│   │   ├── cache.py         # Redis cache-aside helpers (get/set/invalidate balance)
│   │   └── queue.py         # SQS publish_audit_event
│   ├── database.py          # SQLAlchemy engines (standard + SERIALIZABLE), Base, get_db
│   └── models.py            # User, Account, AuditEvent ORM models
├── alembic/                 # Database migrations
│   └── versions/            # 6ef77d6ea9e5 (users, accounts), 7eba6ca3c842 (audit_events)
├── scripts/
│   └── worker.py            # SQS consumer — polls queue, writes audit_events, deletes message
├── tests/
│   ├── test_transfer.py          # Unit tests (4) — mocked DB
│   └── test_transfer_integration.py  # Integration tests (2) — testcontainers Postgres
├── main.py                  # FastAPI app entry point, middleware, router registration
├── requirements.txt
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
| GET | /health | No | Liveness check |

## Current status
Week 2 complete. Caching, async processing, and observability added.

### Completed (Week 1)
- JWT auth with access/refresh tokens, RBAC, require_role, @require_permission
- Alembic migrations, User and Account models, real DB auth
- Balance and transfer endpoints, SERIALIZABLE isolation, self-transfer guard
- structlog JSON logging with request ID middleware
- Unit and integration tests (6/6 passing)
- AWS infra: VPC, subnets, security groups, EC2
- Neon production database (zero cost)

### Completed (Week 2)
- Redis cache-aside for GET /accounts/balance (60s TTL)
- Cache invalidation on transfer for both accounts
- SQS audit event publishing after successful transfers
- SQS worker (scripts/worker.py) consuming events into audit_events table
- Dead letter queue (max 3 receives)
- AuditEvent model and migration
- CloudWatch agent on EC2 shipping structured logs to payment-api-logs log group

### Week 3 goals
- CloudWatch dashboard (request rate, error rate) and alarms
- Terraform — infrastructure as code
- GitHub Actions CI/CD pipeline
- Docker — containerise the application
- AWS SAA certification prep begins
- System design — Alex Xu chapters 6-8
- DSA sessions 7-8 (heaps, dynamic programming)
- OOP design practice — parking lot

## Key design decisions
- **FastAPI over Flask** — async-first, type-safe, better for production
- **Decimal not Float** — Float has precision errors unacceptable for financial data
- **SERIALIZABLE isolation + with_for_update()** — prevents race conditions on transfers
- **Two engines** — standard for reads, SERIALIZABLE for transfers
- **Service layer** — transfer business logic in service.py, not the router
- **Cache-aside pattern** — check Redis first, fall back to DB, invalidate on write
- **Cache invalidation on both accounts** — receiver balance also changes on transfer
- **String storage in Redis** — Decimal doesn't serialise; str preserves precision
- **SQS publish after commit** — never publish an event for a transfer that rolled back
- **At-least-once delivery + idempotency** — worker must handle duplicate messages
- **Dead letter queue** — prevents a bad message blocking the queue forever
- **structlog + CloudWatch** — every log line queryable, correlated by request_id, centralised
- **IAM role on EC2** — temporary rotating credentials, no long-term keys
- **Neon over RDS** — free tier, zero ongoing cost; codebase is DB-agnostic (DATABASE_URL only)

## Local development
```bash
source venv/bin/activate
alembic upgrade head          # migrations against Neon
uvicorn main:app --reload     # start API
python scripts/worker.py      # start SQS worker (separate terminal)
redis-cli monitor             # watch cache operations
```

## EC2 demo deployment
```bash
# 1. Start EC2 in AWS console — get new public IP (changes each start)
# 2. Update SSH security group rule to current IP if needed
ssh -i ~/.ssh/payment-api-key.pem ec2-user@EC2_PUBLIC_IP
cd payment-api && git pull origin main
source venv/bin/activate && pip install -r requirements.txt
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
# Test: curl http://EC2_PUBLIC_IP:8000/health
# Stop when done: pkill -f uvicorn, then stop EC2 in console
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
| CloudWatch | Logs ingestion | ~$0 (minimal volume) |
| VPC / networking | Always on | $0 |
| **Total** | | **~$0** |