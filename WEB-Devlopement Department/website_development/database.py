import os
import sqlite3
from datetime import datetime
from typing import Optional


class WebsiteDatabase:
    def __init__(self, db_path: str = ""):
        if not db_path:
            from website_development.config import Config
            db_path = Config.DB_PATH
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
                CREATE TABLE IF NOT EXISTS website_projects (
                    project_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    client_name TEXT DEFAULT '',
                    industry TEXT DEFAULT '',
                    project_type TEXT DEFAULT 'business_website',
                    platform TEXT DEFAULT 'static',
                    website_url TEXT DEFAULT '',
                    goals TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    completion_pct REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS website_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    output_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_preview TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES website_projects(project_id)
                );
            """)

    def add_project(self, project: dict) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO website_projects
                        (project_id, company_name, client_name, industry, project_type,
                         platform, website_url, goals, status, completion_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get("project_id", ""),
                    project.get("company_name", ""),
                    project.get("client_name", project.get("contact_name", "")),
                    project.get("industry", ""),
                    project.get("project_type", project.get("proposal_type", "business_website")),
                    project.get("platform", "static"),
                    project.get("website_url", project.get("website", "")),
                    project.get("goals", ""),
                    project.get("status", "pending"),
                    project.get("completion_pct", 0.0),
                ))
            return True
        except Exception as e:
            print(f"Error adding website project: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM website_projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_projects(self, status: str = "") -> list[dict]:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM website_projects WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM website_projects ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, project_id: str, status: str, completion_pct: float):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE website_projects SET status = ?, completion_pct = ?, updated_at = ? WHERE project_id = ?",
                (status, completion_pct, datetime.now().isoformat(), project_id),
            )

    def add_output(self, project_id: str, output_type: str, file_path: str, preview: str = ""):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO website_outputs (project_id, output_type, file_path, content_preview)
                VALUES (?, ?, ?, ?)
            """, (project_id, output_type, file_path, preview[:200]))

    def get_outputs(self, project_id: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM website_outputs WHERE project_id = ? ORDER BY created_at ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def summary(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM website_projects").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM website_projects GROUP BY status"
            ).fetchall()
            return {
                "total_projects": total,
                "by_status": {r["status"]: r["cnt"] for r in by_status},
            }
