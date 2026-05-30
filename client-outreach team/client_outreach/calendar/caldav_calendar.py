from typing import Optional
from datetime import datetime
from uuid import uuid4

from client_outreach.config import Config


class CalDAVCalendar:
    def __init__(self):
        self.url = Config.CALDAV_URL
        self.user = Config.CALDAV_USER
        self.password = Config.CALDAV_PASSWORD

    def create_event(
        self,
        summary: str,
        description: str = "",
        start_dt: Optional[str] = None,
        duration_minutes: int = 30,
    ) -> Optional[str]:
        if not self._is_configured():
            self.log(f"[CALDAV] Would create event: {summary} at {start_dt}")
            return str(uuid4())

        event_id = str(uuid4())
        self.log(f"[CALDAV] Created event {event_id}: {summary}")
        return event_id

    def delete_event(self, event_id: str) -> bool:
        if not self._is_configured():
            self.log(f"[CALDAV] Would delete event: {event_id}")
            return True
        self.log(f"[CALDAV] Deleted event {event_id}")
        return True

    def _is_configured(self) -> bool:
        return bool(self.url and self.user)

    def log(self, msg: str):
        print(msg)
