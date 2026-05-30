from typing import Optional
from client_outreach.agents.base_agent import BaseAgent


PIPELINE_STAGES = [
    "New Lead",
    "Contacted",
    "Interested",
    "Meeting Booked",
    "Proposal Sent",
    "Negotiation",
    "Won",
    "Lost",
]


class CRMAgent(BaseAgent):
    def import_leads(self, leads: list[dict]):
        count = 0
        for lead in leads:
            if not lead.get("lead_id"):
                continue
            if not lead.get("pipeline_stage"):
                lead["pipeline_stage"] = "New Lead"
            self.db.add_lead(lead)
            count += 1
        self.log(f"Imported {count} leads into CRM")

    def get_pipeline_summary(self) -> dict:
        return self.db.summary()

    def advance_stage(self, lead_id: str, stage: str):
        if stage in PIPELINE_STAGES:
            self.db.update_pipeline_stage(lead_id, stage)
            self.log(f"Lead {lead_id} → {stage}")

    def get_leads_by_stage(self, stage: str) -> list[dict]:
        return self.db.get_leads(stage=stage)

    def get_lead(self, lead_id: str) -> Optional[dict]:
        return self.db.get_lead(lead_id)

    def update_lead(self, lead_id: str, updates: dict):
        self.db.update_lead(lead_id, updates)

    def get_all_leads(self) -> list[dict]:
        return self.db.get_leads()

    def get_pipeline_counts(self) -> dict:
        summary = self.db.summary()
        return summary.get("pipeline", {})

    def get_qualified_leads(self) -> list[dict]:
        return self.db.get_leads(stage="New Lead")
