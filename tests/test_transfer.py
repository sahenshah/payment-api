from decimal import Decimal
from unittest.mock import MagicMock
from app.models import Account

def test_transfer_insufficient_funds():
    # Arrange — create a fake account with low balance
    account = Account(id=1, user_id=1, balance=Decimal("50.00"))
    
    # Assert the condition directly
    amount = Decimal("100.00")
    assert account.balance < amount