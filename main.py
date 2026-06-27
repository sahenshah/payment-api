"""FastAPI application entry point."""

from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.accounts.router import router as accounts_router
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

# Call this before creating the app
configure_logging()

app = FastAPI(title="Payment Transfer API")

# Add middleware
app.add_middleware(RequestIDMiddleware)

app.include_router(auth_router)
app.include_router(accounts_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Report basic liveness of the API.

    Returns:
        dict[str, str]: a status payload, e.g. {"status": "ok"}.
    """
    return {"status": "ok"}
