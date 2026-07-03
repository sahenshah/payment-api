"""SQS message publishing for audit events."""
import json
import boto3
from datetime import datetime, timezone
from app.core.config import get_settings

settings = get_settings()

sqs_client = boto3.client("sqs", region_name="eu-west-2")

def publish_audit_event(
    event_type: str,
    from_account_id: int,
    to_account_id: int,
    amount: str,
) -> None:
    """Publish a transfer audit event to SQS.
    
    Args:
        event_type: the type of event e.g. transfer_completed
        from_account_id: the sender account ID
        to_account_id: the receiver account ID
        amount: the transfer amount as a string
    """
    message = {
        "event_type": event_type,
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "amount": amount,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    sqs_client.send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=json.dumps(message),
    )