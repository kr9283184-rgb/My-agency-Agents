from typing import Optional


class TwitterAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def send_dm(self, username: str, message: str) -> bool:
        self.log(f"[BROWSER] Would send X DM to @{username}")
        return True

    def log(self, msg: str):
        print(msg)
