import os
import tempfile
import pytest

from client_outreach.database import OutreachDatabase
from client_outreach.agents.crm_agent import CRMAgent, PIPELINE_STAGES
from client_outreach.agents.lead_intelligence import LeadIntelligenceAgent
from client_outreach.agents.conversation_analysis import ConversationAnalysisAgent
from client_outreach.agents.follow_up import FollowUpAgent
from client_outreach.agents.appointment_booking import AppointmentBookingAgent
from client_outreach.agents.proposal_generation import ProposalGenerationAgent
from client_outreach.agents.executive_report import ExecutiveReportingAgent


@pytest.fixture
def db():
    tmp = tempfile.mktemp(suffix=".db")
    database = OutreachDatabase(db_path=tmp)
    yield database
    if os.path.exists(tmp):
        os.remove(tmp)


def test_crm_agent_import_leads(db):
    crm = CRMAgent(db=db)
    leads = [
        {"lead_id": "l1", "company_name": "Test Corp", "industry": "tech"},
        {"lead_id": "l2", "company_name": "Test Inc", "industry": "finance"},
    ]
    crm.import_leads(leads)
    all_leads = crm.get_all_leads()
    assert len(all_leads) == 2


def test_crm_agent_pipeline(db):
    crm = CRMAgent(db=db)
    crm.import_leads([{"lead_id": "l1", "company_name": "Test"}])

    crm.advance_stage("l1", "Interested")
    lead = crm.get_lead("l1")
    assert lead["pipeline_stage"] == "Interested"


def test_crm_agent_pipeline_counts(db):
    crm = CRMAgent(db=db)
    crm.import_leads([
        {"lead_id": "l1", "company_name": "A"},
        {"lead_id": "l2", "company_name": "B"},
    ])
    crm.advance_stage("l1", "Contacted")
    counts = crm.get_pipeline_counts()
    assert counts.get("New Lead") == 1
    assert counts.get("Contacted") == 1


def test_lead_intelligence_rule_based(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test Realty", "industry": "real estate"})
    agent = LeadIntelligenceAgent(db=db)
    lead = db.get_lead("l1")
    brief = agent.research_lead(lead)
    assert "pain_points" in brief
    assert "buying_intent" in brief
    updated = db.get_lead("l1")
    assert updated is not None
    import json
    notes = json.loads(updated["notes"])
    assert "pain_points" in notes


def test_conversation_analysis_rule_based(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    agent = ConversationAnalysisAgent(db=db)
    analysis = agent.analyze_response("l1", "Yes, I'm interested. How much does it cost?")
    assert analysis["interest_level"] == "high"
    assert analysis["classification"] in ("Hot Lead", "Warm Lead")


def test_conversation_analysis_not_interested(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    agent = ConversationAnalysisAgent(db=db)
    analysis = agent.analyze_response("l1", "Not interested, please stop contacting me")
    assert analysis["interest_level"] == "low"
    assert analysis["classification"] == "Cold Lead"


def test_follow_up_agent_schedule(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test Corp"})
    agent = FollowUpAgent(db=db)
    from datetime import datetime, timedelta
    past_date = (datetime.now() - timedelta(days=30)).isoformat()
    agent.schedule_sequence("l1", start_date=past_date)
    pending = db.get_pending_follow_ups()
    assert len(pending) == 5  # 5 steps in the sequence


def test_proposal_generation(db):
    db.add_lead({"lead_id": "l1", "company_name": "Test Corp", "industry": "tech"})
    agent = ProposalGenerationAgent(db=db, output_dir=tempfile.mkdtemp())
    fp = agent.generate_service_proposal(
        {"lead_id": "l1", "company_name": "Test Corp", "industry": "tech"}
    )
    assert fp is not None
    assert fp.endswith(".pdf")


def test_executive_report_daily(db, capsys):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    agent = ExecutiveReportingAgent(db=db)
    report = agent.generate_daily_report()
    assert "DAILY SALES REPORT" in report


def test_executive_report_weekly(db, capsys):
    db.add_lead({"lead_id": "l1", "company_name": "Test"})
    agent = ExecutiveReportingAgent(db=db)
    report = agent.generate_weekly_report()
    assert "WEEKLY SALES REPORT" in report


def test_pipeline_stages_definition():
    assert "New Lead" in PIPELINE_STAGES
    assert "Contacted" in PIPELINE_STAGES
    assert "Interested" in PIPELINE_STAGES
    assert "Meeting Booked" in PIPELINE_STAGES
    assert "Proposal Sent" in PIPELINE_STAGES
    assert "Negotiation" in PIPELINE_STAGES
    assert "Won" in PIPELINE_STAGES
    assert "Lost" in PIPELINE_STAGES
