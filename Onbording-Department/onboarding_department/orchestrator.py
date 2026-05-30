from dataclasses import dataclass, field
from typing import Optional
from onboarding_department.database import OnboardingDatabase
from onboarding_department.agents.client_manager_agent import ClientManagerAgent


@dataclass
class OnboardingResult:
    db: Optional[OnboardingDatabase] = None
    total_leads: int = 0
    onboarded: int = 0
    failed: int = 0
    reports: list = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "total_leads": self.total_leads,
            "onboarded": self.onboarded,
            "failed": self.failed,
        }


class OnboardingOrchestrator:
    def __init__(self, db: Optional[OnboardingDatabase] = None):
        self.db = db or OnboardingDatabase()
        self.manager = ClientManagerAgent(db=self.db)

    def run(self, lead_id: str = "", output_dir: str = "") -> OnboardingResult:
        result = OnboardingResult(db=self.db)

        if lead_id:
            leads = [self.db.get_lead(lead_id)] if self.db.get_lead(lead_id) else []
            if not leads:
                lead_data = self._fetch_lead_from_outreach(lead_id)
                leads = [lead_data] if lead_data else []
        else:
            leads = self.db.get_won_leads_from_outreach()

        if not leads:
            self._log("No won leads found to onboard")
            return result

        result.total_leads = len(leads)

        for i, lead in enumerate(leads, 1):
            company = lead.get("company_name", "Unknown")
            lid = lead.get("lead_id", "")
            self._log(f"\n{'='*60}")
            self._log(f"[{i}/{len(leads)}] Onboarding {company} ({lid})")
            self._log(f"{'='*60}")

            try:
                proposal = self.db.get_proposal_from_outreach(lid)
                lead_with_proposal = dict(lead)
                if proposal:
                    lead_with_proposal["proposal_type"] = proposal.get("proposal_type", "service")
                    lead_with_proposal["deal_amount"] = proposal.get("amount", 0.0)

                onboarding_result = self.manager.onboard_lead(
                    lead_with_proposal, proposal, output_dir
                )
                result.onboarded += 1
                result.reports.append({
                    "lead_id": lid,
                    "company": company,
                    "status": "completed",
                    "outputs": onboarding_result,
                })
                self._log(f"✓ {company} onboarded successfully")

            except Exception as e:
                self._log(f"✗ Failed to onboard {company}: {e}")
                result.failed += 1
                result.reports.append({
                    "lead_id": lid,
                    "company": company,
                    "status": "failed",
                    "error": str(e),
                })

        self._log(f"\n{'='*60}")
        self._log(f"ONBOARDING COMPLETE — {result.onboarded}/{result.total_leads} onboarded")
        self._log(f"{'='*60}")

        return result

    def run_status(self, lead_id: str = "") -> dict:
        if lead_id:
            status = self.manager.crm_agent.get_pipeline_status(lead_id)
            return {"leads": [status]}
        else:
            pipeline = self.manager.crm_agent.get_onboarding_pipeline_summary()
            outreach = self.db.outreach_summary()
            return {
                "leads": pipeline,
                "outreach_db": outreach,
            }

    def _fetch_lead_from_outreach(self, lead_id: str) -> Optional[dict]:
        db_path = self.db._resolve_outreach_db()
        if not db_path:
            return None
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM leads WHERE lead_id = ?", (lead_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    def _log(self, message: str):
        print(message)
