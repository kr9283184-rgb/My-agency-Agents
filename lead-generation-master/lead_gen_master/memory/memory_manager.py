import json
import os
from datetime import datetime
from typing import Optional
from lead_gen_master.config import Config


class MemoryManager:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self._leads_file = os.path.join(self.output_dir, "leads.json")
        self._industries_file = os.path.join(
            self.output_dir, "industries.json"
        )
        self._audits_file = os.path.join(self.output_dir, "audits.json")
        self._outreach_file = os.path.join(
            self.output_dir, "outreach.json"
        )

        self.leads = self._load(self._leads_file, [])
        self.industries = self._load(self._industries_file, [])
        self.audits = self._load(self._audits_file, [])
        self.outreach = self._load(self._outreach_file, [])

    def _load(self, path: str, default):
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default
        return default

    def _save(self, path: str, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    # -- Lead memory --

    def add_lead(self, lead: dict):
        self.leads.append(lead)
        self._save(self._leads_file, self.leads)

    def add_leads(self, leads: list[dict]):
        self.leads.extend(leads)
        self._save(self._leads_file, self.leads)

    def get_leads(self) -> list[dict]:
        return self.leads

    def get_lead(self, lead_id: str) -> Optional[dict]:
        for l in self.leads:
            if l["lead_id"] == lead_id:
                return l
        return None

    def update_lead(self, lead_id: str, updates: dict):
        for l in self.leads:
            if l["lead_id"] == lead_id:
                l.update(updates)
                break
        self._save(self._leads_file, self.leads)

    # -- Industry memory --

    def add_industry(self, industry: dict):
        self.industries.append(industry)
        self._save(self._industries_file, self.industries)

    def add_industries(self, industries: list[dict]):
        self.industries.extend(industries)
        self._save(self._industries_file, self.industries)

    def get_industries(self) -> list[dict]:
        return self.industries

    # -- Audit memory --

    def add_audit(self, audit: dict):
        self.audits.append(audit)
        self._save(self._audits_file, self.audits)

    def add_audits(self, audits: list[dict]):
        self.audits.extend(audits)
        self._save(self._audits_file, self.audits)

    def get_audits(self) -> list[dict]:
        return self.audits

    # -- Outreach memory --

    def add_outreach(self, brief: dict):
        self.outreach.append(brief)
        self._save(self._outreach_file, self.outreach)

    def add_outreaches(self, briefs: list[dict]):
        self.outreach.extend(briefs)
        self._save(self._outreach_file, self.outreach)

    def get_outreaches(self) -> list[dict]:
        return self.outreach

    # -- Summary --

    def summary(self) -> dict:
        return {
            "total_leads": len(self.leads),
            "total_industries": len(self.industries),
            "total_audits": len(self.audits),
            "total_outreaches": len(self.outreach),
            "qualified_leads": sum(
                1
                for l in self.leads
                if l.get("lead_score", 0) >= 50
            ),
            "high_priority": sum(
                1
                for l in self.leads
                if l.get("priority") == "High"
            ),
        }

    def clear_all(self):
        self.leads = []
        self.industries = []
        self.audits = []
        self.outreach = []
        for f in [
            self._leads_file,
            self._industries_file,
            self._audits_file,
            self._outreach_file,
        ]:
            if os.path.exists(f):
                os.remove(f)
