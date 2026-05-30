from typing import Optional


class FacebookAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def send_message(self, profile_url: str, message: str) -> bool:
        self.log(f"[BROWSER] Would send Facebook message to {profile_url}")
        return True

    def log(self, msg: str):
        print(msg)
