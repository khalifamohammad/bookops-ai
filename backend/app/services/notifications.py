from __future__ import annotations

import json
import logging
import smtplib
import urllib.parse
import urllib.request
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_notification(subject: str, message: str) -> None:
    sent = False
    if settings.telegram_bot_token and settings.telegram_chat_id:
        try:
            payload = urllib.parse.urlencode({"chat_id": settings.telegram_chat_id, "text": f"{subject}\n{message}"}).encode()
            url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
            urllib.request.urlopen(urllib.request.Request(url, data=payload), timeout=10).read()
            sent = True
        except Exception:
            logger.exception("Telegram notification failed")

    if settings.smtp_host and settings.notification_email:
        try:
            email = EmailMessage()
            email["Subject"] = subject
            email["From"] = settings.smtp_user or settings.notification_email
            email["To"] = settings.notification_email
            email.set_content(message)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if settings.smtp_user and settings.smtp_password:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(email)
            sent = True
        except Exception:
            logger.exception("Email notification failed")

    if not sent:
        logger.info("Notification: %s | %s", subject, message)
