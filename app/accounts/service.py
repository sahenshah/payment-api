"""Business logic for account operations."""
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Account

def transfer_funds(
    db: Session,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal
) -> Account:
    """Transfer funds between two accounts atomically."""
    try:
        from_account = db.query(Account).filter(
            Account.id == from_account_id
        ).with_for_update().first()
        
        to_account = db.query(Account).filter(
            Account.id == to_account_id
        ).with_for_update().first()
        
        if from_account is None or to_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        if from_account.id == to_account.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to the same account"
            )

        if from_account.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        
        from_account.balance -= amount
        to_account.balance += amount
        db.commit()
        db.refresh(from_account)
        return from_account
        
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise