from typing import Optional
from client_outreach.database import OutreachDatabase


class BaseAgent:
    def __init__(self, db: Optional[OutreachDatabase] = None):
        self.db = db or OutreachDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")
