import os
import smtplib

from email.message import EmailMessage

from .email_templates import build_verify_email_content


EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@hiretrackr.org")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")


def build_verify_link(token: str) -> str:
    return f"{APP_BASE_URL}/verify-email?token={token}"


def send_email_smtp(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    if not SMTP_HOST:
        raise RuntimeError("SMTP_HOST is not set")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.starttls()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)