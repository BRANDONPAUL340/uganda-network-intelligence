import sys
import time
from pathlib import Path
from sqlalchemy import text
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1.0


class TemporaryDeliveryError(Exception):
    """Custom exception family flagging transient retryable glitches [INDEX]."""
    pass


class PermanentDeliveryError(Exception):
    """Custom exception family flagging structural non-retryable configuration errors [INDEX]."""
    pass


def classify_error_type(error_msg: str) -> str:
    """
    Part 17. Error Classification Engine: Audits exception strings 
    to separate transient drops from permanent boundary breaks [INDEX].
    """
    msg_upper = error_msg.upper()
    if "TIMEOUT" in msg_upper or "CONN" in msg_upper or "UNAVAILABLE" in msg_upper:
        return "RETRYABLE"
    return "PERMANENT"


def log_notification_delivery(
    incident_id: int,
    channel: str,
    delivery_status: str,
    recipient: str,
    error_message: str = None,
    attempt_count: int = 1
) -> int:
    """Atomically records alert dispatch transaction states into PostgreSQL [INDEX]."""
    query = text(
        """
        INSERT INTO pipeline_notification_logs 
            (incident_id, channel, delivery_status, recipient, error_message, attempt_count, dispatched_at)
        VALUES 
            (:incident_id, :channel, :delivery_status, :recipient, :error_message, :attempt_count, CURRENT_TIMESTAMP)
        RETURNING notification_id;
        """
    )
    with engine.begin() as conn:
        return int(conn.execute(
            query,
            {
                "incident_id": incident_id,
                "channel": channel,
                "delivery_status": delivery_status,
                "recipient": recipient,
                "error_message": error_message,
                "attempt_count": attempt_count
            }
        ).scalar())

def check_channel_already_notified(incident_id: int, channel: str) -> bool:
    """
    Checks whether an incident has already produced a successful notification
    on the specified channel.

    Used by the notification router to prevent duplicate alerts for the same
    incident/channel pair.
    """
    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM pipeline_notification_logs
            WHERE incident_id = :incident_id
              AND channel = :channel
              AND delivery_status = 'SENT'
        );
        """
    )

    with engine.connect() as conn:
        return bool(conn.execute(
            query,
            {
                "incident_id": incident_id,
                "channel": channel,
            }
        ).scalar())


def execute_network_delivery_with_backoff(incident_id: int, channel: str, recipient: str, message: str) -> bool:
    """
    Part 18. Fault-Tolerant Delivery Handler: Manages attempts and exponential 
    backoffs dynamically based on error retry classifications [INDEX].
    """
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        try:
            # Simulate a temporary network drop on the first attempt loop [INDEX]
            if channel == "EMAIL" and attempts == 1:
                raise TemporaryDeliveryError("Timeout: Remote mail exchange server is temporarily unresponsive.")
            
            # Simulate a permanent auth crash for a specific broken test handle [INDEX]
            if recipient == "bad_credentials@network.co.ug":
                raise PermanentDeliveryError("Auth Failure: Invalid corporate SMTP configuration credentials token.")
            
            # Simulated successful alert transmission loop pass [INDEX]
            log_notification_delivery(incident_id, channel, "SENT", recipient, attempt_count=attempts)
            return True
            
        except TemporaryDeliveryError as exc:
            err_class = classify_error_type(str(exc))
            if attempts >= MAX_ATTEMPTS or err_class == "PERMANENT":
                print(f"❌ Max attempts breached or permanent fault hit. Marking alert as FAILED.")
                log_notification_delivery(incident_id, channel, "FAILED", recipient, str(exc), attempts)
                return False
                
            delay_interval = BASE_DELAY_SECONDS * (2 ** (attempts - 1))
            print(f"⚠️ Retryable glitch (Attempt {attempts}/{MAX_ATTEMPTS}): Waiting {delay_interval}s...")
            time.sleep(delay_interval)
            
        except PermanentDeliveryError as exc:
            # Part 16. Permanent errors immediately drop to FAILED state with zero retries [INDEX]
            print(f"🚨 Permanent configuration failure hit. Aborting retry loop immediately.")
            log_notification_delivery(incident_id, channel, "FAILED", recipient, str(exc), attempts)
            return False
            
    return False


def send_notification(
    incident_id: int,
    severity: str,
    check_name: str,
    raw_message: str
) -> None:
    """Central Channel Router: Evaluates severity rules and prevents duplicate alerts."""
    alert_body = f"Incident Alert for check '{check_name}': {raw_message}"

    # Dashboard notification is recorded for every detection event.
    log_notification_delivery(
        incident_id,
        "DASHBOARD",
        "SENT",
        "streamlit_operations_cockpit"
    )

    if severity == "HIGH":
        email_recipient = "oncall_engineer@network.co.ug"

        # Prevent repeated EMAIL alerts for the same incident.
        if check_channel_already_notified(incident_id, "EMAIL"):
            log_notification_delivery(
                incident_id=incident_id,
                channel="EMAIL",
                delivery_status="SKIPPED",
                recipient=email_recipient,
                error_message="Duplicate notification suppressed.",
            )
            return

        execute_network_delivery_with_backoff(
            incident_id,
            "EMAIL",
            email_recipient,
            alert_body
        )