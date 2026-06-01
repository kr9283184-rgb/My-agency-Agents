import os
import sqlite3
from datetime import datetime
from typing import Optional


class SecurityDatabase:
    def __init__(self, db_path: str = ""):
        if not db_path:
            from security_department.config import Config
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
                CREATE TABLE IF NOT EXISTS security_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    target_name TEXT NOT NULL,
                    target_type TEXT DEFAULT 'system',
                    assessment_type TEXT DEFAULT 'security_review',
                    risk_level TEXT DEFAULT 'medium',
                    owner TEXT DEFAULT '',
                    scope TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    security_score REAL DEFAULT 0.0,
                    completion_pct REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS security_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id TEXT NOT NULL,
                    output_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_preview TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (assessment_id) REFERENCES security_assessments(assessment_id)
                );

                CREATE TABLE IF NOT EXISTS vulnerability_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    recommendation TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (assessment_id) REFERENCES security_assessments(assessment_id)
                );
            """)

    def add_assessment(self, assessment: dict) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO security_assessments
                        (assessment_id, target_name, target_type, assessment_type,
                         risk_level, owner, scope, status, security_score,
                         completion_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment.get("assessment_id", ""),
                    assessment.get("target_name", ""),
                    assessment.get("target_type", "system"),
                    assessment.get("assessment_type", "security_review"),
                    assessment.get("risk_level", "medium"),
                    assessment.get("owner", ""),
                    assessment.get("scope", ""),
                    assessment.get("status", "pending"),
                    float(assessment.get("security_score", 0.0) or 0.0),
                    float(assessment.get("completion_pct", 0.0) or 0.0),
                ))
            return True
        except Exception as e:
            print(f"Error adding security assessment: {e}")
            return False

    def get_assessment(self, assessment_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM security_assessments WHERE assessment_id = ?",
                (assessment_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_assessments(self, status: str = "") -> list[dict]:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM security_assessments WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM security_assessments ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, assessment_id: str, status: str, completion_pct: float, security_score: float = None):
        with self._get_conn() as conn:
            if security_score is None:
                conn.execute(
                    "UPDATE security_assessments SET status = ?, completion_pct = ?, updated_at = ? WHERE assessment_id = ?",
                    (status, completion_pct, datetime.now().isoformat(), assessment_id),
                )
            else:
                conn.execute(
                    "UPDATE security_assessments SET status = ?, completion_pct = ?, security_score = ?, updated_at = ? WHERE assessment_id = ?",
                    (status, completion_pct, security_score, datetime.now().isoformat(), assessment_id),
                )

    def add_output(self, assessment_id: str, output_type: str, file_path: str, preview: str = ""):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO security_outputs (assessment_id, output_type, file_path, content_preview)
                VALUES (?, ?, ?, ?)
            """, (assessment_id, output_type, file_path, preview[:200]))

    def get_outputs(self, assessment_id: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM security_outputs WHERE assessment_id = ? ORDER BY created_at ASC",
                (assessment_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_vulnerability(self, assessment_id: str, title: str, severity: str, recommendation: str):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO vulnerability_register
                    (assessment_id, title, severity, recommendation)
                VALUES (?, ?, ?, ?)
            """, (assessment_id, title, severity, recommendation))

    def get_vulnerabilities(self, assessment_id: str = "", severity: str = "") -> list[dict]:
        query = "SELECT * FROM vulnerability_register"
        clauses = []
        params = []
        if assessment_id:
            clauses.append("assessment_id = ?")
            params.append(assessment_id)
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
            total = conn.execute("SELECT COUNT(*) FROM security_assessments").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM security_assessments GROUP BY status"
            ).fetchall()
            by_risk = conn.execute(
                "SELECT risk_level, COUNT(*) AS cnt FROM security_assessments GROUP BY risk_level"
            ).fetchall()
            vulns = conn.execute(
                "SELECT severity, COUNT(*) AS cnt FROM vulnerability_register GROUP BY severity"
            ).fetchall()
            avg_score = conn.execute(
                "SELECT AVG(security_score) FROM security_assessments"
            ).fetchone()[0]
            return {
                "total_assessments": total,
                "by_status": {r["status"]: r["cnt"] for r in by_status},
                "by_risk": {r["risk_level"]: r["cnt"] for r in by_risk},
                "vulnerabilities": {r["severity"]: r["cnt"] for r in vulns},
                "average_security_score": round(avg_score or 0.0, 1),
            }
