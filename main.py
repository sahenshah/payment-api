"""FastAPI application entry point."""

from fastapi import FastAPI

from app.auth.router import router as auth_router

app = FastAPI(title="Payment Transfer API")

app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Report basic liveness of the API.

    Returns:
        dict[str, str]: a status payload, e.g. {"status": "ok"}.
    """
    return {"status": "ok"}
