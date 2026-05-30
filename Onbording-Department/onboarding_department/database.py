import sqlite3
import os
from typing import Optional
from datetime import datetime


class OnboardingDatabase:
    def __init__(self, db_path: str = ""):
        if not db_path:
            from onboarding_department.config import Config
            db_path = os.path.join(Config.OUTPUT_DIR, "onboarding.db")
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._init_schema()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self):
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS onboarding_progress (
                    lead_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    contact_name TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    whatsapp_phone TEXT DEFAULT '',
                    industry TEXT DEFAULT '',
                    proposal_type TEXT DEFAULT '',
                    deal_amount REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'pending',
                    welcome_sent_at TEXT,
                    requirements_collected_at TEXT,
                    questionnaire_sent_at TEXT,
                    assets_requested_at TEXT,
                    access_checklist_created_at TEXT,
                    brand_analysis_at TEXT,
                    scope_defined_at TEXT,
                    contract_verified_at TEXT,
                    roadmap_created_at TEXT,
                    handover_completed_at TEXT,
                    crm_updated_at TEXT,
                    report_generated_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS onboarding_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    output_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_preview TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES onboarding_progress(lead_id)
                );
            """)

    def add_lead(self, lead: dict) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO onboarding_progress
                        (lead_id, company_name, contact_name, email, whatsapp_phone,
                         industry, proposal_type, deal_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """, (
                    lead.get("lead_id", ""),
                    lead.get("company_name", ""),
                    lead.get("contact_name", ""),
                    lead.get("email", ""),
                    lead.get("whatsapp_phone", ""),
                    lead.get("industry", ""),
                    lead.get("proposal_type", ""),
                    lead.get("deal_amount", 0.0),
                ))
            return True
        except Exception:
            return False

    def get_lead(self, lead_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM onboarding_progress WHERE lead_id = ?", (lead_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_leads(self, status: str = "") -> list:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM onboarding_progress WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM onboarding_progress ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, lead_id: str, status: str, field: str = ""):
        now = datetime.now().isoformat()
        field_map = {
            "welcome": "welcome_sent_at",
            "requirements": "requirements_collected_at",
            "questionnaire": "questionnaire_sent_at",
            "assets": "assets_requested_at",
            "access": "access_checklist_created_at",
            "brand": "brand_analysis_at",
            "scope": "scope_defined_at",
            "contract": "contract_verified_at",
            "roadmap": "roadmap_created_at",
            "handover": "handover_completed_at",
            "crm": "crm_updated_at",
            "report": "report_generated_at",
        }
        with self._get_conn() as conn:
            if field and field in field_map:
                conn.execute(
                    f"UPDATE onboarding_progress SET status = ?, {field_map[field]} = ?, updated_at = ? WHERE lead_id = ?",
                    (status, now, now, lead_id),
                )
            else:
                conn.execute(
                    "UPDATE onboarding_progress SET status = ?, updated_at = ? WHERE lead_id = ?",
                    (status, now, lead_id),
                )

    def add_output(self, lead_id: str, output_type: str, file_path: str, preview: str = ""):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO onboarding_outputs (lead_id, output_type, file_path, content_preview)
                VALUES (?, ?, ?, ?)
            """, (lead_id, output_type, file_path, preview[:200]))

    def get_outputs(self, lead_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM onboarding_outputs WHERE lead_id = ? ORDER BY created_at ASC",
                (lead_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def summary(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM onboarding_progress").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM onboarding_progress GROUP BY status"
            ).fetchall()
            return {
                "total": total,
                "by_status": {r["status"]: r["cnt"] for r in by_status},
            }

    def get_won_leads_from_outreach(self) -> list:
        db_path = self._resolve_outreach_db()
        if not db_path:
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM leads WHERE pipeline_stage = 'Won'"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def get_proposal_from_outreach(self, lead_id: str) -> Optional[dict]:
        db_path = self._resolve_outreach_db()
        if not db_path:
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM proposals WHERE lead_id = ? AND status = 'accepted' ORDER BY created_at DESC LIMIT 1",
                (lead_id,),
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    def update_outreach_pipeline_stage(self, lead_id: str, stage: str) -> bool:
        db_path = self._resolve_outreach_db()
        if not db_path:
            return False
        try:
            conn = sqlite3.connect(db_path)
            conn.execute(
                "UPDATE leads SET pipeline_stage = ?, updated_at = datetime('now') WHERE lead_id = ?",
                (stage, lead_id),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_communications_from_outreach(self, lead_id: str) -> list:
        db_path = self._resolve_outreach_db()
        if not db_path:
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM communications WHERE lead_id = ? ORDER BY created_at ASC",
                (lead_id,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def _resolve_outreach_db(self) -> str:
        path = os.getenv("OUTREACH_DB_PATH", "")
        if path and os.path.isfile(path):
            return path
        from onboarding_department.config import Config
        if os.path.isfile(Config.OUTREACH_DB_PATH):
            return Config.OUTREACH_DB_PATH
        return ""

    def outreach_summary(self) -> dict:
        db_path = self._resolve_outreach_db()
        if not db_path:
            return {"error": "Outreach DB not found"}
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            stages = conn.execute(
                "SELECT pipeline_stage, COUNT(*) as cnt FROM leads GROUP BY pipeline_stage"
            ).fetchall()
            conn.close()
            return {"stages": {r["pipeline_stage"]: r["cnt"] for r in stages}}
        except Exception as e:
            return {"error": str(e)}
