"""Redis cache client and cache-aside utilities."""
import json
import redis
from app.core.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)

def get_cached_balance(account_id: int) -> str | None:
    """Get cached account balance from Redis.
    
    Args:
        account_id: the account ID to look up
        
    Returns:
        str | None: cached balance as string, or None if cache miss
    """
    return redis_client.get(f"balance:{account_id}")

def set_cached_balance(account_id: int, balance: str, ttl: int = 60) -> None:
    """Store account balance in Redis cache.
    
    Args:
        account_id: the account ID
        balance: the balance as a string
        ttl: time to live in seconds (default 60)
    """
    redis_client.setex(f"balance:{account_id}", ttl, balance)

def invalidate_balance(account_id: int) -> None:
    """Delete cached balance for an account.
    
    Args:
        account_id: the account ID to invalidate
    """
    redis_client.delete(f"balance:{account_id}")