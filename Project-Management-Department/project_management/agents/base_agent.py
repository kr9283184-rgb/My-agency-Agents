from typing import Optional
from project_management.database import ProjectDatabase


class BaseAgent:
    def __init__(self, db: Optional[ProjectDatabase] = None):
        self.db = db or ProjectDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")
