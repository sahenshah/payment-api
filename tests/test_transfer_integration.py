"""Integration tests for transfer endpoint using a real Postgres container."""
import pytest
from decimal import Decimal
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Account
from app.core.security import get_password_hash
from app.accounts.service import transfer_funds


@pytest.fixture(scope="module")
def db_session():
    """Spin up a real Postgres container and yield a database session."""
    with PostgresContainer("postgres:15") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Seed test users and accounts
        user1 = User(
            username="alice",
            hashed_password=get_password_hash("password123"),
            role="user"
        )
        user2 = User(
            username="bob",
            hashed_password=get_password_hash("password123"),
            role="user"
        )
        db.add_all([user1, user2])
        db.commit()
        
        account1 = Account(user_id=user1.id, balance=Decimal("1000.00"))
        account2 = Account(user_id=user2.id, balance=Decimal("500.00"))
        db.add_all([account1, account2])
        db.commit()
        
        yield db, account1, account2
        
        db.close()


def test_successful_transfer(db_session):
    """Test a real transfer between two accounts in Postgres."""
    db, account1, account2 = db_session
    
    result = transfer_funds(
        db=db,
        from_account_id=account1.id,
        to_account_id=account2.id,
        amount=Decimal("100.00")
    )
    
    db.refresh(account1)
    db.refresh(account2)
    
    assert account1.balance == Decimal("900.00")
    assert account2.balance == Decimal("600.00")
    assert result.balance == Decimal("900.00")


def test_insufficient_funds_integration(db_session):
    """Test insufficient funds rejection against real database."""
    from fastapi import HTTPException
    db, account1, account2 = db_session
    
    with pytest.raises(HTTPException) as exc_info:
        transfer_funds(
            db=db,
            from_account_id=account1.id,
            to_account_id=account2.id,
            amount=Decimal("10000.00")
        )
    
    assert exc_info.value.status_code == 400
    
    # Verify balances unchanged
    db.refresh(account1)
    db.refresh(account2)
    assert account1.balance == Decimal("900.00")
    assert account2.balance == Decimal("600.00")