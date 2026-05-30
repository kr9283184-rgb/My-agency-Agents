import pytest

from client_outreach.compliance.rate_limiter import RateLimiter
from client_outreach.compliance.consent_manager import ConsentManager
from client_outreach.compliance.footer_generator import FooterGenerator


def test_rate_limiter_can_send():
    limiter = RateLimiter()
    assert limiter.can_send("email") is True
    assert limiter.remaining("email") > 0


def test_rate_limiter_record():
    limiter = RateLimiter()
    initial = limiter.remaining("email")
    limiter.record_send("email")
    assert limiter.remaining("email") == initial - 1


def test_consent_manager(monkeypatch):
    class MockDB:
        def __init__(self):
            self._consent = {}

        def get_consent(self, lead_id, channel):
            return self._consent.get((lead_id, channel), False)

        def set_consent(self, lead_id, channel, granted, source=""):
            self._consent[(lead_id, channel)] = granted

    cm = ConsentManager(db=MockDB())

    assert cm.check_consent("l1", "email") is False
    cm.grant_consent("l1", "email", "web_form")
    assert cm.check_consent("l1", "email") is True
    cm.revoke_consent("l1", "email", "unsubscribe")
    assert cm.check_consent("l1", "email") is False


def test_footer_generator():
    fg = FooterGenerator()
    footer = fg.email_footer()
    assert "unsubscribe" in footer.lower()
    assert fg.email in footer
