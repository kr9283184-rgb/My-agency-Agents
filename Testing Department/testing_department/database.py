import os
import sqlite3
from datetime import datetime
from typing import Optional


class TestingDatabase:
    __test__ = False

    def __init__(self, db_path: str = ""):
        if not db_path:
            from testing_department.config import Config
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
                CREATE TABLE IF NOT EXISTS qa_projects (
                    qa_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    product_type TEXT DEFAULT 'web_application',
                    owner TEXT DEFAULT '',
                    risk_level TEXT DEFAULT 'medium',
                    requirements TEXT DEFAULT '',
                    acceptance_criteria TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    qa_decision TEXT DEFAULT 'pending',
                    quality_score REAL DEFAULT 0.0,
                    completion_pct REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS qa_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    qa_id TEXT NOT NULL,
                    output_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_preview TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (qa_id) REFERENCES qa_projects(qa_id)
                );

                CREATE TABLE IF NOT EXISTS bug_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    qa_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    reproduction_steps TEXT DEFAULT '',
                    owner TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (qa_id) REFERENCES qa_projects(qa_id)
                );
            """)

    def add_project(self, project: dict) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO qa_projects
                        (qa_id, product_name, product_type, owner, risk_level,
                         requirements, acceptance_criteria, status, qa_decision,
                         quality_score, completion_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get("qa_id", ""),
                    project.get("product_name", ""),
                    project.get("product_type", "web_application"),
                    project.get("owner", ""),
                    project.get("risk_level", "medium"),
                    project.get("requirements", ""),
                    project.get("acceptance_criteria", ""),
                    project.get("status", "pending"),
                    project.get("qa_decision", "pending"),
                    float(project.get("quality_score", 0.0) or 0.0),
                    float(project.get("completion_pct", 0.0) or 0.0),
                ))
            return True
        except Exception as e:
            print(f"Error adding QA project: {e}")
            return False

    def get_project(self, qa_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM qa_projects WHERE qa_id = ?", (qa_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_projects(self, status: str = "") -> list[dict]:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM qa_projects WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM qa_projects ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, qa_id: str, status: str, completion_pct: float, quality_score: float = None, qa_decision: str = None):
        fields = ["status = ?", "completion_pct = ?", "updated_at = ?"]
        params = [status, completion_pct, datetime.now().isoformat()]
        if quality_score is not None:
            fields.append("quality_score = ?")
            params.append(quality_score)
        if qa_decision is not None:
            fields.append("qa_decision = ?")
            params.append(qa_decision)
        params.append(qa_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE qa_projects SET {', '.join(fields)} WHERE qa_id = ?",
                params,
            )

    def add_output(self, qa_id: str, output_type: str, file_path: str, preview: str = ""):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO qa_outputs (qa_id, output_type, file_path, content_preview)
                VALUES (?, ?, ?, ?)
            """, (qa_id, output_type, file_path, preview[:200]))

    def get_outputs(self, qa_id: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM qa_outputs WHERE qa_id = ? ORDER BY created_at ASC",
                (qa_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_bug(self, qa_id: str, title: str, severity: str, reproduction_steps: str, owner: str = ""):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO bug_register
                    (qa_id, title, severity, reproduction_steps, owner)
                VALUES (?, ?, ?, ?, ?)
            """, (qa_id, title, severity, reproduction_steps, owner))

    def get_bugs(self, qa_id: str = "", severity: str = "") -> list[dict]:
        query = "SELECT * FROM bug_register"
        clauses = []
        params = []
        if qa_id:
            clauses.append("qa_id = ?")
            params.append(qa_id)
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def summary(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM qa_projects").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM qa_projects GROUP BY status"
            ).fetchall()
            by_decision = conn.execute(
                "SELECT qa_decision, COUNT(*) AS cnt FROM qa_projects GROUP BY qa_decision"
            ).fetchall()
            bugs = conn.execute(
                "SELECT severity, COUNT(*) AS cnt FROM bug_register GROUP BY severity"
            ).fetchall()
            avg_score = conn.execute("SELECT AVG(quality_score) FROM qa_projects").fetchone()[0]
            return {
                "total_projects": total,
                "by_status": {r["status"]: r["cnt"] for r in by_status},
                "by_decision": {r["qa_decision"]: r["cnt"] for r in by_decision},
                "bugs": {r["severity"]: r["cnt"] for r in bugs},
                "average_quality_score": round(avg_score or 0.0, 1),
            }
