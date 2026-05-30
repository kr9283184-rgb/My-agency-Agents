import os
import tempfile
import pytest

from client_outreach.database import OutreachDatabase


@pytest.fixture
def db():
    tmp = tempfile.mktemp(suffix=".db")
    database = OutreachDatabase(db_path=tmp)
    yield database
    if os.path.exists(tmp):
        os.remove(tmp)


def test_add_and_get_lead(db):
    lead_id = db.add_lead({
        "lead_id": "test-001",
        "company_name": "Test Corp",
        "industry": "real estate",
        "contact_name": "John Doe",
        "email": "john@test.com",
    })
    assert lead_id == "test-001"

    lead = db.get_lead("test-001")
    assert lead is not None
    assert lead["company_name"] == "Test Corp"
    assert lead["pipeline_stage"] == "New Lead"


def test_update_pipeline_stage(db):
    db.add_lead({"lead_id": "test-002", "company_name": "Test Inc"})
    db.update_pipeline_stage("test-002", "Contacted")
    lead = db.get_lead("test-002")
    assert lead["pipeline_stage"] == "Contacted"


def test_get_leads_by_stage(db):
    db.add_lead({"lead_id": "l1", "company_name": "A", "pipeline_stage": "New Lead"})
    db.add_lead({"lead_id": "l2", "company_name": "B", "pipeline_stage": "Contacted"})
    db.add_lead({"lead_id": "l3", "company_name": "C", "pipeline_stage": "New Lead"})

    new_leads = db.get_leads(stage="New Lead")
    assert len(new_leads) == 2

    contacted = db.get_leads(stage="Contacted")
    assert len(contacted) == 1


def test_communications(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    cid = db.add_communication({
        "lead_id": "l1",
        "channel": "email",
        "direction": "outbound",
        "subject": "Hello",
        "body": "Test message",
        "status": "sent",
    })
    assert cid is not None

    comms = db.get_communications("l1")
    assert len(comms) == 1
    assert comms[0]["subject"] == "Hello"


def test_conversation_analysis(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    aid = db.add_analysis({
        "lead_id": "l1",
        "interest_level": "high",
        "classification": "Hot Lead",
        "summary": "Very interested",
    })
    assert aid is not None

    analyses = db.get_analyses("l1")
    assert len(analyses) == 1
    assert analyses[0]["classification"] == "Hot Lead"


def test_appointments(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    apt_id = db.add_appointment({
        "lead_id": "l1",
        "title": "Sales Meeting",
        "proposed_slot": "Monday 10am",
    })
    assert apt_id is not None

    apts = db.get_appointments("l1")
    assert len(apts) == 1
    assert apts[0]["status"] == "pending"


def test_proposals(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    pid = db.add_proposal({
        "lead_id": "l1",
        "title": "Service Proposal",
        "proposal_type": "service",
        "amount": 2500.0,
    })
    assert pid is not None

    proposals = db.get_proposals("l1")
    assert len(proposals) == 1


def test_follow_ups(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    fid = db.add_follow_up({
        "lead_id": "l1",
        "step_number": 1,
        "channel": "email",
        "subject": "Follow-up 1",
        "body": "Hello",
        "scheduled_at": "2020-01-01T00:00:00",
    })
    assert fid is not None

    pending = db.get_pending_follow_ups()
    assert len(pending) == 1


def test_consent(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    assert db.get_consent("l1", "email") is False

    db.set_consent("l1", "email", True, "form")
    assert db.get_consent("l1", "email") is True

    db.set_consent("l1", "email", False, "unsubscribe")
    assert db.get_consent("l1", "email") is False


def test_daily_stats(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    db.add_communication({
        "lead_id": "l1", "channel": "email",
        "direction": "outbound", "subject": "Hi", "body": "Test",
        "status": "sent",
    })

    stats = db.get_daily_stats()
    assert stats["emails_sent"] >= 1


def test_summary(db):
    db.add_lead({"lead_id": "l1", "company_name": "A"})
    db.add_lead({"lead_id": "l2", "company_name": "B"})
    summary = db.summary()
    assert summary["total_leads"] == 2
    assert summary["pipeline"]["New Lead"] == 2
