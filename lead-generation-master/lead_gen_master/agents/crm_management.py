from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent


CRM_FIELDS = [
    "lead_id",
    "company_name",
    "industry",
    "contact_name",
    "job_title",
    "website",
    "profile_urls",
    "location",
    "rating",
    "review_count",
    "lead_score",
    "priority",
    "recommended_service",
    "notes",
    "source",
    "created_at",
]


class CRMManagementAgent(BaseAgent):
    def __init__(self, memory=None):
        super().__init__(memory)

    def structure_records(
        self, leads: list[dict]
    ) -> list[dict]:
        self.log(f"Structuring {len(leads)} CRM records")
        records = []
        for lead in leads:
            record = {}
            for field in CRM_FIELDS:
                value = lead.get(field, "")
                if isinstance(value, float):
                    value = round(value, 2)
                record[field] = value
            records.append(record)
        return records

    def to_csv_rows(self, leads: list[dict]) -> list[list]:
        rows = [CRM_FIELDS]
        for lead in leads:
            rows.append(
                [str(lead.get(f, "")) for f in CRM_FIELDS]
            )
        return rows
