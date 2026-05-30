from client_outreach.config import Config


class FooterGenerator:
    def __init__(self):
        self.company_name = Config.SMTP_FROM_NAME
        self.email = Config.SMTP_FROM_EMAIL

    def email_footer(self) -> str:
        return (
            f"\n\n---\n"
            f"{self.company_name}\n"
            f"{self.email}\n"
            f"\n"
            f"If you'd prefer not to receive future messages, "
            f"reply with 'unsubscribe' and you'll be opted out immediately."
        )

    def social_footer(self) -> str:
        return (
            f"\n\n— {self.company_name} | "
            f"Reply to stop receiving messages"
        )

    def whatsapp_footer(self) -> str:
        return (
            f"\n\n— {self.company_name}\n"
            f"Reply STOP to opt out"
        )
