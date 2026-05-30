from typing import Optional


class LinkedInAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def send_connection_request(self, profile_url: str, note: str = "") -> bool:
        self.log(f"[BROWSER] Would send LinkedIn connection to {profile_url}")
        if note:
            self.log(f"  With note: {note}")
        return True

    def send_message(self, profile_url: str, message: str) -> bool:
        self.log(f"[BROWSER] Would send LinkedIn message to {profile_url}")
        return True

    def log(self, msg: str):
        print(msg)
