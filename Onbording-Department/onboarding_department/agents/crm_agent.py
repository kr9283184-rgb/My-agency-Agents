from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class CRMAgent(BaseAgent):
    PIPELINE_STAGES = [
        "New Lead",
        "Contacted",
        "Interested",
        "Meeting Booked",
        "Proposal Sent",
        "Negotiation",
        "Won",
        "Onboarding",
        "Planning",
        "Production",
        "Testing",
        "Completed",
    ]

    def update_pipeline(self, lead_id: str, stage: str) -> dict:
        updated = self.db.update_outreach_pipeline_stage(lead_id, stage)
        if updated:
            self.log(f"Updated pipeline for {lead_id}: {stage}")
        else:
            self.log(f"Could not update pipeline for {lead_id} (outreach DB not accessible)")

        return {
            "lead_id": lead_id,
            "stage": stage,
            "updated": updated,
        }

    def get_pipeline_status(self, lead_id: str) -> dict:
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"lead_id": lead_id, "status": "not found"}

        current_idx = 0
        for i, stage in enumerate(self.PIPELINE_STAGES):
            if stage.lower() == lead.get("status", "").lower():
                current_idx = i
                break

        return {
            "lead_id": lead_id,
            "company": lead.get("company_name", ""),
            "current_stage": lead.get("status", ""),
            "stage_index": current_idx,
            "total_stages": len(self.PIPELINE_STAGES),
            "progress_pct": round((current_idx / (len(self.PIPELINE_STAGES) - 1)) * 100),
        }

    def get_onboarding_pipeline_summary(self) -> list:
        leads = self.db.get_leads()
        return [self.get_pipeline_status(l["lead_id"]) for l in leads]
