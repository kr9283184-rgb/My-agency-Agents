from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent


class DuplicateDetectionAgent(BaseAgent):
    def __init__(self, memory=None):
        super().__init__(memory)

    def deduplicate(self, leads: list[dict]) -> list[dict]:
        self.log(f"Deduplicating {len(leads)} leads")

        seen_names = {}
        seen_websites = {}
        unique = []

        for lead in leads:
            name = (
                lead.get("company_name", "")
                .strip()
                .lower()
            )
            website = (
                lead.get("website", "")
                .strip()
                .lower()
                .rstrip("/")
            )
            lead_id = lead.get("lead_id", "")

            dup_of = None

            if name and name in seen_names:
                dup_of = seen_names[name]
            elif website and website in seen_websites:
                dup_of = seen_websites[website]

            if dup_of:
                existing = next(
                    (
                        l
                        for l in unique
                        if l.get("lead_id") == dup_of
                    ),
                    None,
                )
                if existing:
                    merged = self._merge(existing, lead)
                    unique = [
                        merged
                        if l.get("lead_id") == dup_of
                        else l
                        for l in unique
                    ]
                continue

            if name:
                seen_names[name] = lead_id
            if website:
                seen_websites[website] = lead_id
            unique.append(lead)

        removed = len(leads) - len(unique)
        if removed:
            self.log(f"Removed {removed} duplicates")

        return unique

    def _merge(self, existing: dict, new: dict) -> dict:
        merged = dict(existing)
        for key in [
            "contact_name",
            "job_title",
            "profile_urls",
            "rating",
            "review_count",
            "notes",
        ]:
            if not existing.get(key) and new.get(key):
                merged[key] = new[key]

        existing_notes = existing.get("notes", "")
        new_notes = new.get("notes", "")
        if new_notes and new_notes not in existing_notes:
            merged["notes"] = (
                existing_notes + "; " + new_notes
                if existing_notes
                else new_notes
            )

        return merged
