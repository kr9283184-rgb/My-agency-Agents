from typing import Optional


class WhatsAppAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def send_message(self, phone_number: str, message: str) -> bool:
        self.log(f"[BROWSER] Would send WhatsApp message to {phone_number}")
        return True

    def log(self, msg: str):
        print(msg)
