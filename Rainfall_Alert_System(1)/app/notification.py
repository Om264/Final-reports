import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import (
    EMAIL_SETTINGS,
    ENABLE_EMAIL,
    ENABLE_SMS,
    NOTIFICATION_LOG_FILE,
    SMS_SETTINGS,
)
from app.utils import current_timestamp

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, log_file: Path = NOTIFICATION_LOG_FILE):
        self.log_file: Path = log_file
        self.email_enabled: bool = ENABLE_EMAIL
        self.sms_enabled: bool = ENABLE_SMS
        self._notifications: List[Dict[str, Any]] = []

    def send_alert_notification(
        self,
        city: str,
        rainfall: float,
        alert_level: str,
        notification_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if notification_types is None:
            notification_types = ["email", "sms"]
        result: Dict[str, Any] = {
            "timestamp": current_timestamp(),
            "city": city,
            "rainfall": rainfall,
            "alert_level": alert_level,
            "notifications_sent": [],
        }

        if "email" in notification_types and self.email_enabled:
            email_result: Dict[str, Any] = self._send_email(city, rainfall, alert_level)
            result["notifications_sent"].append(f"email:{email_result['status']}")

        if "sms" in notification_types and self.sms_enabled:
            sms_result: Dict[str, Any] = self._send_sms(city, rainfall, alert_level)
            result["notifications_sent"].append(f"sms:{sms_result['status']}")

        self._log_notification(result)
        self._notifications.append(result)
        return result

    def _send_email(self, city: str, rainfall: float, alert_level: str) -> Dict[str, Any]:
        if not all([EMAIL_SETTINGS["smtp_server"], EMAIL_SETTINGS["sender_email"]]):
            logger.info(f"Email not configured. Would send alert for {city}.")
            return {"status": "simulated", "message": "Email not configured; notification simulated."}

        try:
            import smtplib
            from email.mime.text import MIMEText

            subject: str = f"RAINFALL ALERT: {city} - {alert_level} Level"
            body: str = (
                f"Rainfall Alert Notification\n"
                f"========================\n"
                f"City: {city}\n"
                f"Rainfall: {rainfall:.2f} mm/h\n"
                f"Alert Level: {alert_level}\n"
                f"Time: {current_timestamp()}\n"
                f"\nPlease take appropriate precautions."
            )

            msg: Any = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = EMAIL_SETTINGS["sender_email"]
            msg["To"] = EMAIL_SETTINGS["receiver_email"]

            with smtplib.SMTP(
                str(EMAIL_SETTINGS["smtp_server"]),
                int(str(EMAIL_SETTINGS["smtp_port"])),
                timeout=10,
            ) as server:
                if EMAIL_SETTINGS["sender_password"]:
                    server.starttls()
                    server.login(str(EMAIL_SETTINGS["sender_email"]), str(EMAIL_SETTINGS["sender_password"]))
                server.send_message(msg)

            logger.info(f"Email alert sent for {city}")
            return {"status": "sent", "message": "Email alert sent successfully."}
        except Exception as e:
            logger.error(f"Failed to send email for {city}: {e}")
            return {"status": "failed", "message": f"Email sending failed: {e}"}

    def _send_sms(self, city: str, rainfall: float, alert_level: str) -> Dict[str, Any]:
        if not all([SMS_SETTINGS["twilio_account_sid"], SMS_SETTINGS["twilio_phone_number"]]):
            logger.info(f"SMS not configured. Would send alert for {city}.")
            return {"status": "simulated", "message": "SMS not configured; notification simulated."}

        try:
            from twilio.rest import Client

            body: str = (
                f"ALERT: {city} rainfall {rainfall:.1f}mm/h "
                f"({alert_level}). Take precautions."
            )

            client: Any = Client(
                SMS_SETTINGS["twilio_account_sid"],
                SMS_SETTINGS["twilio_auth_token"],
            )
            client.messages.create(
                body=body,
                from_=str(SMS_SETTINGS["twilio_phone_number"]),
                to=str(SMS_SETTINGS["receiver_phone"]),
            )

            logger.info(f"SMS alert sent for {city}")
            return {"status": "sent", "message": "SMS alert sent successfully."}
        except ImportError:
            logger.warning("twilio package not installed. SMS simulation only.")
            return {"status": "simulated", "message": "twilio not installed; notification simulated."}
        except Exception as e:
            logger.error(f"Failed to send SMS for {city}: {e}")
            return {"status": "failed", "message": f"SMS sending failed: {e}"}

    def _log_notification(self, entry: Dict[str, Any]) -> None:
        try:
            line: str = (
                f"{entry['timestamp']} | {entry['city']} | "
                f"{entry['rainfall']:.2f} mm/h | {entry['alert_level']} | "
                f"{', '.join(entry['notifications_sent'])}\n"
            )
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as e:
            logger.error(f"Failed to log notification: {e}")

    def load_notification_history(self, max_lines: int = 100) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        if not self.log_file.exists():
            return records
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines: List[str] = f.readlines()
            for line in lines[-max_lines:]:
                parts: List[str] = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    records.append({
                        "timestamp": parts[0],
                        "city": parts[1],
                        "rainfall": parts[2],
                        "level": parts[3],
                        "type": parts[4],
                    })
        except OSError as e:
            logger.error(f"Failed to read notification log: {e}")
        return records

    def get_stats(self) -> Dict[str, int]:
        history: List[Dict[str, Any]] = self.load_notification_history()
        stats: Dict[str, int] = {"total": len(history), "email": 0, "sms": 0, "simulated": 0}
        for entry in history:
            types: str = entry.get("type", "")
            if "email" in types:
                stats["email"] += 1
            if "sms" in types:
                stats["sms"] += 1
            if "simulated" in types:
                stats["simulated"] += 1
        return stats
