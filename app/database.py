"""SQLAlchemy engine, session, and declarative base setup."""
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)

serializable_engine = create_engine(
    settings.database_url,
    execution_options={"isolation_level": "SERIALIZABLE"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SerializableSession = sessionmaker(autocommit=False, autoflush=False, bind=serializable_engine)

class Base(DeclarativeBase):
    """Base class for all ORM models."""

def get_db() -> Generator[Session, None, None]:
    """Yield a standard database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_serializable_db() -> Generator[Session, None, None]:
    """Yield a SERIALIZABLE isolation level session for financial operations."""
    db = SerializableSession()
    try:
        yield db
    finally:
        db.close()