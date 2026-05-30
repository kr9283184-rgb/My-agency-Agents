import sqlite3
import os
from datetime import datetime
from typing import Optional


class OutreachDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            os.makedirs("output", exist_ok=True)
            db_path = "output/outreach.db"
        self.db_path = db_path
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    industry TEXT DEFAULT '',
                    contact_name TEXT DEFAULT '',
                    job_title TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    website TEXT DEFAULT '',
                    linkedin_url TEXT DEFAULT '',
                    facebook_url TEXT DEFAULT '',
                    twitter_url TEXT DEFAULT '',
                    instagram_url TEXT DEFAULT '',
                    whatsapp_phone TEXT DEFAULT '',
                    location TEXT DEFAULT '',
                    lead_score INTEGER DEFAULT 0,
                    priority TEXT DEFAULT 'Low',
                    source TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    pipeline_stage TEXT DEFAULT 'New Lead',
                    consent_email INTEGER DEFAULT 0,
                    consent_whatsapp INTEGER DEFAULT 0,
                    consent_social INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS communications (
                    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    channel TEXT NOT NULL CHECK(channel IN ('email','whatsapp','linkedin','facebook','twitter','instagram')),
                    direction TEXT NOT NULL CHECK(direction IN ('outbound','inbound')),
                    subject TEXT DEFAULT '',
                    body TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    opened_at TEXT,
                    replied_at TEXT,
                    clicked_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
                );

                CREATE TABLE IF NOT EXISTS conversation_analyses (
                    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    comm_id INTEGER,
                    interest_level TEXT DEFAULT 'unknown' CHECK(interest_level IN ('low','medium','high','unknown')),
                    objections TEXT DEFAULT '',
                    urgency TEXT DEFAULT 'low' CHECK(urgency IN ('low','medium','high')),
                    buying_signals TEXT DEFAULT '',
                    classification TEXT DEFAULT 'Cold Lead' CHECK(classification IN ('Hot Lead','Warm Lead','Cold Lead','Unknown')),
                    summary TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id),
                    FOREIGN KEY (comm_id) REFERENCES communications(comm_id)
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    title TEXT DEFAULT 'Sales Meeting',
                    description TEXT DEFAULT '',
                    proposed_slot TEXT,
                    confirmed_slot TEXT,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','confirmed','cancelled','completed')),
                    calendar_event_id TEXT DEFAULT '',
                    reminder_sent INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
                );

                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    proposal_type TEXT DEFAULT 'service' CHECK(proposal_type IN ('service','website','seo','automation')),
                    file_path TEXT DEFAULT '',
                    amount REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'draft' CHECK(status IN ('draft','sent','accepted','rejected')),
                    sent_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
                );

                CREATE TABLE IF NOT EXISTS follow_up_sequences (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT DEFAULT '',
                    body TEXT DEFAULT '',
                    scheduled_at TEXT,
                    sent_at TEXT,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','sent','skipped','cancelled')),
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
                );

                CREATE TABLE IF NOT EXISTS consent_records (
                    consent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    granted INTEGER NOT NULL DEFAULT 0,
                    source TEXT DEFAULT '',
                    recorded_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
                );

                CREATE TABLE IF NOT EXISTS daily_reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date TEXT NOT NULL UNIQUE,
                    leads_contacted INTEGER DEFAULT 0,
                    emails_sent INTEGER DEFAULT 0,
                    messages_sent INTEGER DEFAULT 0,
                    replies_received INTEGER DEFAULT 0,
                    meetings_booked INTEGER DEFAULT 0,
                    proposals_sent INTEGER DEFAULT 0,
                    deals_closed INTEGER DEFAULT 0,
                    revenue_generated REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            """)
            conn.commit()
        finally:
            conn.close()

    # -- Lead operations --

    def add_lead(self, lead: dict) -> str:
        conn = self._get_conn()
        try:
            lead_id = lead.get("lead_id", "")
            existing = conn.execute(
                "SELECT lead_id FROM leads WHERE lead_id = ?", (lead_id,)
            ).fetchone()
            if existing:
                return lead_id
            conn.execute("""
                INSERT INTO leads (
                    lead_id, company_name, industry, contact_name, job_title,
                    email, phone, website, linkedin_url, facebook_url,
                    twitter_url, instagram_url, whatsapp_phone, location,
                    lead_score, priority, source, notes, pipeline_stage
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                lead.get("lead_id", ""),
                lead.get("company_name", ""),
                lead.get("industry", ""),
                lead.get("contact_name", ""),
                lead.get("job_title", ""),
                lead.get("email", ""),
                lead.get("phone", ""),
                lead.get("website", ""),
                lead.get("linkedin_url", ""),
                lead.get("facebook_url", ""),
                lead.get("twitter_url", ""),
                lead.get("instagram_url", ""),
                lead.get("whatsapp_phone", ""),
                lead.get("location", ""),
                lead.get("lead_score", 0),
                lead.get("priority", "Low"),
                lead.get("source", ""),
                lead.get("notes", ""),
                lead.get("pipeline_stage", "New Lead"),
            ))
            conn.commit()
            return lead.get("lead_id", "")
        finally:
            conn.close()

    def add_leads(self, leads: list[dict]):
        for lead in leads:
            self.add_lead(lead)

    def get_lead(self, lead_id: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM leads WHERE lead_id = ?", (lead_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_leads(self, stage: Optional[str] = None) -> list[dict]:
        conn = self._get_conn()
        try:
            if stage:
                rows = conn.execute(
                    "SELECT * FROM leads WHERE pipeline_stage = ? ORDER BY updated_at DESC",
                    (stage,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM leads ORDER BY updated_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_lead(self, lead_id: str, updates: dict):
        fields = []
        values = []
        for key, val in updates.items():
            fields.append(f"{key} = ?")
            values.append(val)
        if not fields:
            return
        fields.append("updated_at = datetime('now')")
        values.append(lead_id)
        conn = self._get_conn()
        try:
            conn.execute(
                f"UPDATE leads SET {', '.join(fields)} WHERE lead_id = ?",
                values,
            )
            conn.commit()
        finally:
            conn.close()

    def update_pipeline_stage(self, lead_id: str, stage: str):
        self.update_lead(lead_id, {"pipeline_stage": stage})

    # -- Communication operations --

    def add_communication(self, comm: dict) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("""
                INSERT INTO communications
                    (lead_id, channel, direction, subject, body, status)
                VALUES (?,?,?,?,?,?)
            """, (
                comm["lead_id"],
                comm["channel"],
                comm.get("direction", "outbound"),
                comm.get("subject", ""),
                comm.get("body", ""),
                comm.get("status", "pending"),
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_communications(self, lead_id: str) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM communications WHERE lead_id = ? ORDER BY created_at",
                (lead_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # -- Conversation analysis --

    def add_analysis(self, analysis: dict) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("""
                INSERT INTO conversation_analyses
                    (lead_id, comm_id, interest_level, objections, urgency,
                     buying_signals, classification, summary)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                analysis["lead_id"],
                analysis.get("comm_id"),
                analysis.get("interest_level", "unknown"),
                analysis.get("objections", ""),
                analysis.get("urgency", "low"),
                analysis.get("buying_signals", ""),
                analysis.get("classification", "Unknown"),
                analysis.get("summary", ""),
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_analyses(self, lead_id: str) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM conversation_analyses WHERE lead_id = ? ORDER BY created_at DESC",
                (lead_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # -- Appointment operations --

    def add_appointment(self, apt: dict) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("""
                INSERT INTO appointments
                    (lead_id, title, description, proposed_slot, confirmed_slot, status)
                VALUES (?,?,?,?,?,?)
            """, (
                apt["lead_id"],
                apt.get("title", "Sales Meeting"),
                apt.get("description", ""),
                apt.get("proposed_slot"),
                apt.get("confirmed_slot"),
                apt.get("status", "pending"),
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_appointments(self, lead_id: Optional[str] = None) -> list[dict]:
        conn = self._get_conn()
        try:
            if lead_id:
                rows = conn.execute(
                    "SELECT * FROM appointments WHERE lead_id = ? ORDER BY created_at DESC",
                    (lead_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM appointments ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # -- Proposal operations --

    def add_proposal(self, proposal: dict) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("""
                INSERT INTO proposals
                    (lead_id, title, proposal_type, file_path, amount, status)
                VALUES (?,?,?,?,?,?)
            """, (
                proposal["lead_id"],
                proposal["title"],
                proposal.get("proposal_type", "service"),
                proposal.get("file_path", ""),
                proposal.get("amount", 0.0),
                proposal.get("status", "draft"),
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_proposals(self, lead_id: Optional[str] = None) -> list[dict]:
        conn = self._get_conn()
        try:
            if lead_id:
                rows = conn.execute(
                    "SELECT * FROM proposals WHERE lead_id = ? ORDER BY created_at DESC",
                    (lead_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM proposals ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # -- Follow-up operations --

    def add_follow_up(self, fu: dict) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("""
                INSERT INTO follow_up_sequences
                    (lead_id, step_number, channel, subject, body, scheduled_at, status)
                VALUES (?,?,?,?,?,?,?)
            """, (
                fu["lead_id"],
                fu["step_number"],
                fu["channel"],
                fu.get("subject", ""),
                fu.get("body", ""),
                fu.get("scheduled_at"),
                fu.get("status", "pending"),
            ))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_pending_follow_ups(self) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT * FROM follow_up_sequences
                WHERE status = 'pending'
                  AND scheduled_at <= datetime('now')
                ORDER BY scheduled_at
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def mark_follow_up_sent(self, sequence_id: int):
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE follow_up_sequences SET status = 'sent', sent_at = datetime('now') WHERE sequence_id = ?",
                (sequence_id,),
            )
            conn.commit()
        finally:
            conn.close()

    # -- Consent operations --

    def get_consent(self, lead_id: str, channel: str) -> bool:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT granted FROM consent_records WHERE lead_id = ? AND channel = ? ORDER BY consent_id DESC LIMIT 1",
                (lead_id, channel),
            ).fetchone()
            return bool(row) and bool(row["granted"])
        finally:
            conn.close()

    def set_consent(self, lead_id: str, channel: str, granted: bool, source: str = ""):
        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO consent_records (lead_id, channel, granted, source)
                VALUES (?,?,?,?)
            """, (lead_id, channel, int(granted), source))
            conn.commit()
        finally:
            conn.close()

    # -- Reporting --

    def get_daily_stats(self, date_str: Optional[str] = None) -> dict:
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM daily_reports WHERE report_date = ?",
                (date_str,),
            ).fetchone()
            if row:
                return dict(row)
            return self._compute_daily_stats(date_str)
        finally:
            conn.close()

    def _compute_daily_stats(self, date_str: str) -> dict:
        conn = self._get_conn()
        try:
            leads_contacted = conn.execute(
                "SELECT COUNT(DISTINCT lead_id) FROM communications WHERE date(created_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            emails_sent = conn.execute(
                "SELECT COUNT(*) FROM communications WHERE channel = 'email' AND date(created_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            messages_sent = conn.execute(
                "SELECT COUNT(*) FROM communications WHERE channel != 'email' AND date(created_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            replies_received = conn.execute(
                "SELECT COUNT(*) FROM communications WHERE direction = 'inbound' AND date(created_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            meetings_booked = conn.execute(
                "SELECT COUNT(*) FROM appointments WHERE status = 'confirmed' AND date(created_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            proposals_sent = conn.execute(
                "SELECT COUNT(*) FROM proposals WHERE status = 'sent' AND date(sent_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            deals_closed = conn.execute(
                "SELECT COUNT(*) FROM proposals WHERE status = 'accepted' AND date(sent_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0
            revenue = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM proposals WHERE status = 'accepted' AND date(sent_at) = ?",
                (date_str,),
            ).fetchone()[0] or 0.0

            stats = {
                "report_date": date_str,
                "leads_contacted": leads_contacted,
                "emails_sent": emails_sent,
                "messages_sent": messages_sent,
                "replies_received": replies_received,
                "meetings_booked": meetings_booked,
                "proposals_sent": proposals_sent,
                "deals_closed": deals_closed,
                "revenue_generated": revenue,
            }

            conn.execute("""
                INSERT OR REPLACE INTO daily_reports
                    (report_date, leads_contacted, emails_sent, messages_sent,
                     replies_received, meetings_booked, proposals_sent,
                     deals_closed, revenue_generated)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, tuple(stats.values()))
            conn.commit()
            return stats
        finally:
            conn.close()

    def summary(self) -> dict:
        conn = self._get_conn()
        try:
            total_leads = conn.execute(
                "SELECT COUNT(*) FROM leads"
            ).fetchone()[0] or 0
            by_stage = {}
            for stage in [
                "New Lead", "Contacted", "Interested",
                "Meeting Booked", "Proposal Sent",
                "Negotiation", "Won", "Lost",
            ]:
                count = conn.execute(
                    "SELECT COUNT(*) FROM leads WHERE pipeline_stage = ?",
                    (stage,),
                ).fetchone()[0] or 0
                by_stage[stage] = count
            total_comms = conn.execute(
                "SELECT COUNT(*) FROM communications"
            ).fetchone()[0] or 0
            total_appts = conn.execute(
                "SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'"
            ).fetchone()[0] or 0
            total_proposals = conn.execute(
                "SELECT COUNT(*) FROM proposals WHERE status = 'sent'"
            ).fetchone()[0] or 0
            return {
                "total_leads": total_leads,
                "pipeline": by_stage,
                "total_communications": total_comms,
                "confirmed_appointments": total_appts,
                "proposals_sent": total_proposals,
            }
        finally:
            conn.close()
