"""Unit tests for transfer business logic."""
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from app.accounts.service import transfer_funds
from app.models import Account


def make_account(id: int, user_id: int, balance: str) -> Account:
    """Helper to create a mock account."""
    account = Account()
    account.id = id
    account.user_id = user_id
    account.balance = Decimal(balance)
    return account

def test_transfer_success():
    # Arrange
    from_account = make_account(id=1, user_id=1, balance="1000.00")
    to_account = make_account(id=2, user_id=2, balance="500.00")
    
    db = MagicMock()
    
    # First call to db.query().filter().with_for_update().first()
    # returns from_account, second call returns to_account
    db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = [
        from_account,
        to_account
    ]
    
    # Act
    result = transfer_funds(
        db=db,
        from_account_id=1,
        to_account_id=2,
        amount=Decimal("100.00")
    )
    
    # Assert
    assert from_account.balance == Decimal("900.00")
    assert to_account.balance == Decimal("600.00")
    assert result == from_account
    db.commit.assert_called_once()

def test_transfer_insufficient_funds():
    # Arrange
    from_account = make_account(id=1, user_id=1, balance="50.00")
    to_account = make_account(id=2, user_id=2, balance="500.00")
    
    db = MagicMock()
    db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = [
        from_account,
        to_account
    ]
    
    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        transfer_funds(
            db=db,
            from_account_id=1,
            to_account_id=2,
            amount=Decimal("100.00")
        )
    
    assert exc_info.value.status_code == 400
    assert "Insufficient funds" in exc_info.value.detail
    db.commit.assert_not_called()

def test_account_not_found():
    # Arrange
    db = MagicMock()
    db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = [
        None,
        None
    ]
    
    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        transfer_funds(
            db=db,
            from_account_id=1,
            to_account_id=2,
            amount=Decimal("100.00")
        )
    
    assert exc_info.value.status_code == 404
    assert "Account not found" in exc_info.value.detail
    db.commit.assert_not_called()

def test_transfer_to_same_account():
    account = make_account(id=1, user_id=1, balance="1000.00")
    
    db = MagicMock()
    db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = [
        account,
        account
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        transfer_funds(
            db=db,
            from_account_id=1,
            to_account_id=1,
            amount=Decimal("100.00")
        )
    
    assert exc_info.value.status_code == 400
    assert "Cannot transfer to the same account" in exc_info.value.detail
    db.commit.assert_not_called()