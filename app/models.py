from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    accounts = relationship("Account", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")

class AuditEvent(Base):
    """Audit log of all transfer events."""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String, nullable=False)
    from_account_id = Column(Integer, nullable=False)
    to_account_id = Column(Integer, nullable=False)
    amount = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.now)