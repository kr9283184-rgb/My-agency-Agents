from typing import Optional
from client_outreach.database import OutreachDatabase


class ConsentManager:
    def __init__(self, db: Optional[OutreachDatabase] = None):
        self.db = db or OutreachDatabase()

    def check_consent(self, lead_id: str, channel: str) -> bool:
        return self.db.get_consent(lead_id, channel)

    def grant_consent(self, lead_id: str, channel: str, source: str = ""):
        self.db.set_consent(lead_id, channel, True, source)

    def revoke_consent(self, lead_id: str, channel: str, source: str = ""):
        self.db.set_consent(lead_id, channel, False, source)

    def require_consent(self, lead_id: str, channel: str) -> bool:
        return self.check_consent(lead_id, channel)

    def get_consent_summary(self, lead_id: str) -> dict:
        channels = ["email", "whatsapp", "linkedin", "facebook", "twitter", "instagram"]
        return {
            ch: self.check_consent(lead_id, ch) for ch in channels
        }
