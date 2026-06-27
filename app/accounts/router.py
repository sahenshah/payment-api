"""Account routes: balance and transfer."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.accounts.schemas import AccountResponse, TransferRequest
from app.auth.router import get_current_user
from app.auth.schemas import TokenData
from app.database import get_db
from app.models import Account
from app.models import User

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