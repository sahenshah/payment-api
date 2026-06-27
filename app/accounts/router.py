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
    db: Session = Depends(get_db)
) -> AccountResponse:
    """ Transfer the balance from current user's account."""
    with db.begin():
        db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
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
        ).with_for_update().first()
        
        to_account = db.query(Account).filter(
            Account.id == transfer_request.to_account_id
        ).with_for_update().first()

        if account is None or to_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        #accounts found, make the transfer
        if account.balance < transfer_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )

        account.balance -= transfer_request.amount
        to_account.balance += transfer_request.amount
        
    db.refresh(account) 
    return account
