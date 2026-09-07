"""AI automation workflow."""
from core.database import SQLiteDatabase
from core.orchestrator import BaseOrchestrator
from .config import DB_PATH


class Orchestrator(BaseOrchestrator):
    department = "ai_automation"

    def __init__(self, db=None, agent=None):
        super().__init__(db or SQLiteDatabase(DB_PATH), agent)
