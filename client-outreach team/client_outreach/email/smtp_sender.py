import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from client_outreach.config import Config


class SMTPSender:
    def __init__(self):
        self.host = Config.SMTP_HOST
        self.port = Config.SMTP_PORT
        self.user = Config.SMTP_USER
        self.password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM_EMAIL
        self.from_name = Config.SMTP_FROM_NAME

    def send(self, to: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to
            msg["Subject"] = subject

            html_body = body.replace("\n", "<br>\n")
            html = (
                f"<html><body style='font-family: Arial, sans-serif; line-height: 1.6;'>"
                f"{html_body}</body></html>"
            )

            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"[SMTPSender] Failed to send to {to}: {e}")
            return False

    def is_configured(self) -> bool:
        return bool(self.host and self.host != "localhost")
