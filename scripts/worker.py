"""SQS worker — consumes audit events and writes to the database."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.models import AuditEvent

settings = get_settings()

sqs = boto3.client("sqs", region_name="eu-west-2")
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def process_message(message: dict) -> None:
    """Process a single audit event message and write to database."""
    body = json.loads(message["Body"])
    db = SessionLocal()
    try:
        event = AuditEvent(
            event_type=body["event_type"],
            from_account_id=body["from_account_id"],
            to_account_id=body["to_account_id"],
            amount=body["amount"],
            timestamp=body["timestamp"],
        )
        db.add(event)
        db.commit()
        print(f"Processed: {body['event_type']} — "
              f"from account {body['from_account_id']} "
              f"to account {body['to_account_id']} "
              f"amount {body['amount']}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def run() -> None:
    """Poll SQS continuously and process messages."""
    print("Worker started — polling for messages...")
    while True:
        response = sqs.receive_message(
            QueueUrl=settings.sqs_queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
        )
        messages = response.get("Messages", [])
        if not messages:
            print("No messages — waiting...")
            continue
        for message in messages:
            try:
                process_message(message)
                sqs.delete_message(
                    QueueUrl=settings.sqs_queue_url,
                    ReceiptHandle=message["ReceiptHandle"]
                )
            except Exception as e:
                print(f"Failed to process message: {e}")


if __name__ == "__main__":
    run()