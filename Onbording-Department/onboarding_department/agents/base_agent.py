from typing import Optional
from onboarding_department.database import OnboardingDatabase


class BaseAgent:
    def __init__(self, db: Optional[OnboardingDatabase] = None):
        self.db = db or OnboardingDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")
