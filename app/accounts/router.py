"""Account routes: balance and transfer."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.accounts.schemas import AccountResponse, TransferRequest
from app.auth.router import get_current_user
from app.auth.schemas import TokenData
from app.database import get_db
from app.models import Account
from app.models import User
from sqlalchemy import text
from app.accounts.service import transfer_funds
from app.database import get_db, get_serializable_db


from app.core.logging import get_logger
logger = get_logger(__name__)

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/balance", response_model=AccountResponse)
def get_balance(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AccountResponse:
    """Return the balance for the current user's account."""
    user = db.query(User).filter(
        User.username == current_user.username
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    account = db.query(Account).filter(
        Account.user_id == user.id
    ).first()
    
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account

@router.post("/transfer", response_model=AccountResponse)
def transfer(
    transfer_request: TransferRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_serializable_db)
) -> AccountResponse:
    """Transfer funds from current user's account."""
    user = db.query(User).filter(
        User.username == current_user.username
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(
        "transfer_requested",
        username=user.username,
        to_account=transfer_request.to_account_id,
        amount=str(transfer_request.amount)
    )

    from_account = db.query(Account).filter(
        Account.user_id == user.id
    ).first()

    if from_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    account = transfer_funds(
        db=db,
        from_account_id=from_account.id,
        to_account_id=transfer_request.to_account_id,
        amount=transfer_request.amount
    )
    
    logger.info(
        "transfer_complete",
        username=user.username,
        new_balance=str(account.balance)
    )
    
    return account