import sqlite3
import os
from typing import Optional
from datetime import datetime


class ProjectDatabase:
    def __init__(self, db_path: str = ""):
        if not db_path:
            from project_management.config import Config
            db_path = os.path.join(Config.OUTPUT_DIR, "pm.db")
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
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    contact_name TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    whatsapp_phone TEXT DEFAULT '',
                    industry TEXT DEFAULT '',
                    proposal_type TEXT DEFAULT 'service',
                    deal_amount REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'planning',
                    priority TEXT DEFAULT 'medium',
                    start_date TEXT,
                    target_end_date TEXT,
                    actual_end_date TEXT,
                    completion_pct REAL DEFAULT 0.0,
                    project_manager TEXT DEFAULT '',
                    assigned_team TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    onboarding_handover_file TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS milestones (
                    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    phase INTEGER DEFAULT 1,
                    deliverables TEXT DEFAULT '',
                    dependencies TEXT DEFAULT '',
                    due_date TEXT,
                    status TEXT DEFAULT 'pending',
                    completion_pct REAL DEFAULT 0.0,
                    notes TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    milestone_id INTEGER DEFAULT 0,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    owner TEXT DEFAULT '',
                    priority TEXT DEFAULT 'medium',
                    state TEXT DEFAULT 'pending',
                    estimated_hours REAL DEFAULT 0.0,
                    actual_hours REAL DEFAULT 0.0,
                    deadline TEXT,
                    dependencies TEXT DEFAULT '',
                    progress_pct REAL DEFAULT 0.0,
                    notes TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS risks (
                    risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    category TEXT DEFAULT 'other',
                    risk_score INTEGER DEFAULT 1,
                    impact_level TEXT DEFAULT 'low',
                    probability TEXT DEFAULT 'low',
                    mitigation_plan TEXT DEFAULT '',
                    escalation_plan TEXT DEFAULT '',
                    status TEXT DEFAULT 'open',
                    owner TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS change_requests (
                    cr_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    requested_by TEXT DEFAULT '',
                    impact_analysis TEXT DEFAULT '',
                    estimated_effort_hours REAL DEFAULT 0.0,
                    timeline_impact_days INTEGER DEFAULT 0,
                    cost_impact REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'pending',
                    approved_by TEXT DEFAULT '',
                    approved_at TEXT,
                    rejection_reason TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS budget (
                    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    category TEXT DEFAULT 'development',
                    budgeted_hours REAL DEFAULT 0.0,
                    actual_hours REAL DEFAULT 0.0,
                    budgeted_cost REAL DEFAULT 0.0,
                    actual_cost REAL DEFAULT 0.0,
                    notes TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS communications (
                    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    comm_type TEXT DEFAULT 'weekly_update',
                    channel TEXT DEFAULT 'email',
                    subject TEXT DEFAULT '',
                    body TEXT DEFAULT '',
                    recipient TEXT DEFAULT '',
                    status TEXT DEFAULT 'draft',
                    sent_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS resources (
                    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    department TEXT NOT NULL,
                    role TEXT DEFAULT '',
                    member_name TEXT DEFAULT '',
                    allocation_pct INTEGER DEFAULT 100,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT DEFAULT 'assigned',
                    notes TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS quality_checkpoints (
                    qc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    checkpoint_name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    acceptance_criteria TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    tested_by TEXT DEFAULT '',
                    passed INTEGER DEFAULT 0,
                    notes TEXT DEFAULT '',
                    completed_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS lessons_learned (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    category TEXT DEFAULT 'process',
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    impact TEXT DEFAULT '',
                    recommendation TEXT DEFAULT '',
                    is_best_practice INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS project_deliverables (
                    deliverable_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    file_path TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    reviewed INTEGER DEFAULT 0,
                    approved INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                );
            """)

    # --- Projects CRUD ---

    def add_project(self, project: dict) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO projects
                        (project_id, lead_id, company_name, contact_name, email,
                         whatsapp_phone, industry, proposal_type, deal_amount, status,
                         priority, start_date, target_end_date, project_manager,
                         assigned_team, notes, onboarding_handover_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get("project_id", ""),
                    project.get("lead_id", ""),
                    project.get("company_name", ""),
                    project.get("contact_name", ""),
                    project.get("email", ""),
                    project.get("whatsapp_phone", ""),
                    project.get("industry", ""),
                    project.get("proposal_type", ""),
                    project.get("deal_amount", 0.0),
                    project.get("status", "planning"),
                    project.get("priority", "medium"),
                    project.get("start_date", ""),
                    project.get("target_end_date", ""),
                    project.get("project_manager", ""),
                    project.get("assigned_team", ""),
                    project.get("notes", ""),
                    project.get("onboarding_handover_file", ""),
                ))
            return True
        except Exception as e:
            print(f"Error adding project: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_projects(self, status: str = "") -> list:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM projects ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def update_project_status(self, project_id: str, status: str, completion_pct: Optional[float] = None):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            if completion_pct is not None:
                conn.execute(
                    "UPDATE projects SET status = ?, completion_pct = ?, updated_at = ? WHERE project_id = ?",
                    (status, completion_pct, now, project_id),
                )
            else:
                conn.execute(
                    "UPDATE projects SET status = ?, updated_at = ? WHERE project_id = ?",
                    (status, now, project_id),
                )

    def update_project(self, project_id: str, updates: dict):
        now = datetime.now().isoformat()
        allowed = ["status", "priority", "completion_pct", "target_end_date",
                    "actual_end_date", "project_manager", "assigned_team", "notes"]
        set_parts = []
        values = []
        for key, val in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(val)
        if not set_parts:
            return
        set_parts.append("updated_at = ?")
        values.append(now)
        values.append(project_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE projects SET {', '.join(set_parts)} WHERE project_id = ?",
                values,
            )

    # --- Milestones ---

    def add_milestone(self, milestone: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO milestones (project_id, title, description, phase, deliverables,
                                        dependencies, due_date, status, completion_pct, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                milestone["project_id"], milestone.get("title", ""),
                milestone.get("description", ""), milestone.get("phase", 1),
                milestone.get("deliverables", ""), milestone.get("dependencies", ""),
                milestone.get("due_date", ""), milestone.get("status", "pending"),
                milestone.get("completion_pct", 0.0), milestone.get("notes", ""),
            ))
            return cur.lastrowid

    def get_milestones(self, project_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM milestones WHERE project_id = ? ORDER BY phase ASC, due_date ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_milestone(self, milestone_id: int, updates: dict):
        now = datetime.now().isoformat()
        allowed = ["status", "completion_pct", "due_date", "notes"]
        set_parts = []
        values = []
        for key, val in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(val)
        if not set_parts:
            return
        set_parts.append("updated_at = ?")
        values.append(now)
        values.append(milestone_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE milestones SET {', '.join(set_parts)} WHERE milestone_id = ?",
                values,
            )

    # --- Tasks ---

    def add_task(self, task: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO tasks (project_id, milestone_id, title, description, owner,
                                   priority, state, estimated_hours, actual_hours,
                                   deadline, dependencies, progress_pct, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task["project_id"], task.get("milestone_id", 0),
                task.get("title", ""), task.get("description", ""),
                task.get("owner", ""), task.get("priority", "medium"),
                task.get("state", "pending"), task.get("estimated_hours", 0.0),
                task.get("actual_hours", 0.0), task.get("deadline", ""),
                task.get("dependencies", ""), task.get("progress_pct", 0.0),
                task.get("notes", ""),
            ))
            return cur.lastrowid

    def get_tasks(self, project_id: str, state: str = "") -> list:
        with self._get_conn() as conn:
            if state:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project_id = ? AND state = ? ORDER BY priority DESC, deadline ASC",
                    (project_id, state),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project_id = ? ORDER BY state ASC, priority DESC, deadline ASC",
                    (project_id,),
                ).fetchall()
            return [dict(r) for r in rows]

    def update_task_state(self, task_id: int, state: str, progress_pct: Optional[float] = None):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            if progress_pct is not None:
                conn.execute(
                    "UPDATE tasks SET state = ?, progress_pct = ?, updated_at = ? WHERE task_id = ?",
                    (state, progress_pct, now, task_id),
                )
            else:
                conn.execute(
                    "UPDATE tasks SET state = ?, updated_at = ? WHERE task_id = ?",
                    (state, now, task_id),
                )

    def update_task(self, task_id: int, updates: dict):
        now = datetime.now().isoformat()
        allowed = ["owner", "priority", "state", "estimated_hours", "actual_hours",
                    "deadline", "progress_pct", "notes"]
        set_parts = []
        values = []
        for key, val in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(val)
        if not set_parts:
            return
        set_parts.append("updated_at = ?")
        values.append(now)
        values.append(task_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE tasks SET {', '.join(set_parts)} WHERE task_id = ?",
                values,
            )

    def get_task_dashboard(self, project_id: str) -> dict:
        tasks = self.get_tasks(project_id)
        total = len(tasks)
        by_state = {}
        by_owner = {}
        for t in tasks:
            by_state[t["state"]] = by_state.get(t["state"], 0) + 1
            owner = t["owner"] or "unassigned"
            by_owner[owner] = by_owner.get(owner, 0) + 1
        return {
            "total": total,
            "by_state": by_state,
            "by_owner": by_owner,
            "tasks": tasks,
        }

    # --- Risks ---

    def add_risk(self, risk: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO risks (project_id, title, description, category, risk_score,
                                   impact_level, probability, mitigation_plan,
                                   escalation_plan, status, owner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                risk["project_id"], risk.get("title", ""), risk.get("description", ""),
                risk.get("category", "other"), risk.get("risk_score", 1),
                risk.get("impact_level", "low"), risk.get("probability", "low"),
                risk.get("mitigation_plan", ""), risk.get("escalation_plan", ""),
                risk.get("status", "open"), risk.get("owner", ""),
            ))
            return cur.lastrowid

    def get_risks(self, project_id: str, status: str = "") -> list:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM risks WHERE project_id = ? AND status = ? ORDER BY risk_score DESC",
                    (project_id, status),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM risks WHERE project_id = ? ORDER BY risk_score DESC",
                    (project_id,),
                ).fetchall()
            return [dict(r) for r in rows]

    def update_risk(self, risk_id: int, updates: dict):
        now = datetime.now().isoformat()
        allowed = ["status", "risk_score", "impact_level", "probability",
                    "mitigation_plan", "escalation_plan", "owner"]
        set_parts = []
        values = []
        for key, val in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(val)
        if not set_parts:
            return
        set_parts.append("updated_at = ?")
        values.append(now)
        values.append(risk_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE risks SET {', '.join(set_parts)} WHERE risk_id = ?",
                values,
            )

    # --- Change Requests ---

    def add_change_request(self, cr: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO change_requests (project_id, title, description, requested_by,
                                              impact_analysis, estimated_effort_hours,
                                              timeline_impact_days, cost_impact, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cr["project_id"], cr.get("title", ""), cr.get("description", ""),
                cr.get("requested_by", ""), cr.get("impact_analysis", ""),
                cr.get("estimated_effort_hours", 0.0),
                cr.get("timeline_impact_days", 0), cr.get("cost_impact", 0.0),
                cr.get("status", "pending"),
            ))
            return cur.lastrowid

    def get_change_requests(self, project_id: str, status: str = "") -> list:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM change_requests WHERE project_id = ? AND status = ? ORDER BY created_at DESC",
                    (project_id, status),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM change_requests WHERE project_id = ? ORDER BY created_at DESC",
                    (project_id,),
                ).fetchall()
            return [dict(r) for r in rows]

    def approve_change_request(self, cr_id: int, approved_by: str, approved: bool, reason: str = ""):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            if approved:
                conn.execute(
                    "UPDATE change_requests SET status = 'approved', approved_by = ?, approved_at = ?, updated_at = ? WHERE cr_id = ?",
                    (approved_by, now, now, cr_id),
                )
            else:
                conn.execute(
                    "UPDATE change_requests SET status = 'rejected', rejection_reason = ?, updated_at = ? WHERE cr_id = ?",
                    (reason, now, cr_id),
                )

    # --- Budget ---

    def add_budget_entry(self, entry: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO budget (project_id, category, budgeted_hours, actual_hours,
                                    budgeted_cost, actual_cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["project_id"], entry.get("category", "development"),
                entry.get("budgeted_hours", 0.0), entry.get("actual_hours", 0.0),
                entry.get("budgeted_cost", 0.0), entry.get("actual_cost", 0.0),
                entry.get("notes", ""),
            ))
            return cur.lastrowid

    def get_budget(self, project_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM budget WHERE project_id = ? ORDER BY category ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_budget_actuals(self, budget_id: int, actual_hours: float, actual_cost: float):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE budget SET actual_hours = ?, actual_cost = ?, updated_at = ? WHERE budget_id = ?",
                (actual_hours, actual_cost, now, budget_id),
            )

    def get_budget_summary(self, project_id: str) -> dict:
        entries = self.get_budget(project_id)
        total_budgeted_cost = sum(e["budgeted_cost"] for e in entries)
        total_actual_cost = sum(e["actual_cost"] for e in entries)
        total_budgeted_hours = sum(e["budgeted_hours"] for e in entries)
        total_actual_hours = sum(e["actual_hours"] for e in entries)
        project = self.get_project(project_id)
        deal_amount = project["deal_amount"] if project else 0
        profit = deal_amount - total_actual_cost
        margin_pct = (profit / deal_amount * 100) if deal_amount > 0 else 0
        return {
            "deal_amount": deal_amount,
            "total_budgeted_cost": total_budgeted_cost,
            "total_actual_cost": total_actual_cost,
            "total_budgeted_hours": total_budgeted_hours,
            "total_actual_hours": total_actual_hours,
            "profit": profit,
            "profit_margin_pct": margin_pct,
            "budget_health": "healthy" if total_actual_cost <= total_budgeted_cost else "over_budget",
            "entries": entries,
        }

    # --- Communications ---

    def add_communication(self, comm: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO communications (project_id, comm_type, channel, subject, body,
                                             recipient, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comm["project_id"], comm.get("comm_type", "weekly_update"),
                comm.get("channel", "email"), comm.get("subject", ""),
                comm.get("body", ""), comm.get("recipient", ""),
                comm.get("status", "draft"), comm.get("sent_at"),
            ))
            return cur.lastrowid

    def get_communications(self, project_id: str, comm_type: str = "") -> list:
        with self._get_conn() as conn:
            if comm_type:
                rows = conn.execute(
                    "SELECT * FROM communications WHERE project_id = ? AND comm_type = ? ORDER BY created_at DESC",
                    (project_id, comm_type),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM communications WHERE project_id = ? ORDER BY created_at DESC",
                    (project_id,),
                ).fetchall()
            return [dict(r) for r in rows]

    # --- Resources ---

    def add_resource(self, resource: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO resources (project_id, department, role, member_name,
                                       allocation_pct, start_date, end_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource["project_id"], resource.get("department", ""),
                resource.get("role", ""), resource.get("member_name", ""),
                resource.get("allocation_pct", 100), resource.get("start_date", ""),
                resource.get("end_date", ""), resource.get("status", "assigned"),
                resource.get("notes", ""),
            ))
            return cur.lastrowid

    def get_resources(self, project_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM resources WHERE project_id = ? ORDER BY department ASC, role ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_resource_summary(self, project_id: str) -> dict:
        resources = self.get_resources(project_id)
        by_dept = {}
        for r in resources:
            dept = r["department"]
            if dept not in by_dept:
                by_dept[dept] = {"count": 0, "total_allocation": 0, "members": []}
            by_dept[dept]["count"] += 1
            by_dept[dept]["total_allocation"] += r["allocation_pct"]
            by_dept[dept]["members"].append(r["member_name"] or r["role"])
        return {
            "total_resources": len(resources),
            "by_department": by_dept,
            "resources": resources,
        }

    # --- Quality Checkpoints ---

    def add_quality_checkpoint(self, qc: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO quality_checkpoints (project_id, checkpoint_name, description,
                                                  acceptance_criteria, status, tested_by,
                                                  passed, notes, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                qc["project_id"], qc.get("checkpoint_name", ""),
                qc.get("description", ""), qc.get("acceptance_criteria", ""),
                qc.get("status", "pending"), qc.get("tested_by", ""),
                1 if qc.get("passed") else 0, qc.get("notes", ""),
                qc.get("completed_at"),
            ))
            return cur.lastrowid

    def get_quality_checkpoints(self, project_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM quality_checkpoints WHERE project_id = ? ORDER BY created_at ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_quality_checkpoint(self, qc_id: int, passed: bool, tested_by: str, notes: str = ""):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE quality_checkpoints SET status = ?, passed = ?, tested_by = ?, notes = ?, completed_at = ?, updated_at = ? WHERE qc_id = ?",
                ("completed", 1 if passed else 0, tested_by, notes, now, now, qc_id),
            )

    def get_qa_readiness(self, project_id: str) -> dict:
        checkpoints = self.get_quality_checkpoints(project_id)
        total = len(checkpoints)
        passed = sum(1 for c in checkpoints if c["passed"])
        failed = sum(1 for c in checkpoints if not c["passed"] and c["status"] == "completed")
        pending = sum(1 for c in checkpoints if c["status"] == "pending")
        readiness_pct = (passed / total * 100) if total > 0 else 0
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "readiness_pct": readiness_pct,
            "ready": pending == 0 and failed == 0,
            "checkpoints": checkpoints,
        }

    # --- Lessons Learned ---

    def add_lesson(self, lesson: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO lessons_learned (project_id, category, title, description,
                                              impact, recommendation, is_best_practice, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lesson["project_id"], lesson.get("category", "process"),
                lesson.get("title", ""), lesson.get("description", ""),
                lesson.get("impact", ""), lesson.get("recommendation", ""),
                1 if lesson.get("is_best_practice") else 0,
                lesson.get("tags", ""),
            ))
            return cur.lastrowid

    def get_lessons(self, project_id: str = "", category: str = "") -> list:
        with self._get_conn() as conn:
            if project_id and category:
                rows = conn.execute(
                    "SELECT * FROM lessons_learned WHERE project_id = ? AND category = ? ORDER BY created_at DESC",
                    (project_id, category),
                ).fetchall()
            elif project_id:
                rows = conn.execute(
                    "SELECT * FROM lessons_learned WHERE project_id = ? ORDER BY created_at DESC",
                    (project_id,),
                ).fetchall()
            elif category:
                rows = conn.execute(
                    "SELECT * FROM lessons_learned WHERE category = ? ORDER BY created_at DESC",
                    (category,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM lessons_learned ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def get_best_practices(self) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM lessons_learned WHERE is_best_practice = 1 ORDER BY created_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    # --- Deliverables ---

    def add_deliverable(self, deliverable: dict) -> int:
        with self._get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO project_deliverables (project_id, title, description, file_path,
                                                   status, reviewed, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                deliverable["project_id"], deliverable.get("title", ""),
                deliverable.get("description", ""), deliverable.get("file_path", ""),
                deliverable.get("status", "pending"),
                1 if deliverable.get("reviewed") else 0,
                1 if deliverable.get("approved") else 0,
            ))
            return cur.lastrowid

    def get_deliverables(self, project_id: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM project_deliverables WHERE project_id = ? ORDER BY created_at ASC",
                (project_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_deliverable(self, deliverable_id: int, updates: dict):
        now = datetime.now().isoformat()
        allowed = ["status", "reviewed", "approved", "file_path"]
        set_parts = []
        values = []
        for key, val in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(val)
        if not set_parts:
            return
        set_parts.append("updated_at = ?")
        values.append(now)
        values.append(deliverable_id)
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE project_deliverables SET {', '.join(set_parts)} WHERE deliverable_id = ?",
                values,
            )

    # --- Onboarding integration ---

    def get_completed_onboarding_projects(self) -> list:
        db_path = os.getenv("ONBOARDING_DB_PATH", "")
        if not db_path or not os.path.isfile(db_path):
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM onboarding_progress WHERE status = 'completed'"
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def get_onboarding_outputs(self, lead_id: str) -> list:
        db_path = os.getenv("ONBOARDING_DB_PATH", "")
        if not db_path or not os.path.isfile(db_path):
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM onboarding_outputs WHERE lead_id = ? ORDER BY created_at ASC",
                (lead_id,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    # --- Summary / Reporting ---

    def project_summary(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM projects GROUP BY status"
            ).fetchall()
            total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            tasks_by_state = conn.execute(
                "SELECT state, COUNT(*) as cnt FROM tasks GROUP BY state"
            ).fetchall()
            open_risks = conn.execute(
                "SELECT COUNT(*) FROM risks WHERE status = 'open'"
            ).fetchone()[0]
            return {
                "total_projects": total,
                "by_status": {r["status"]: r["cnt"] for r in by_status},
                "total_tasks": total_tasks,
                "tasks_by_state": {r["state"]: r["cnt"] for r in tasks_by_state},
                "open_risks": open_risks,
            }

    def portfolio_health(self) -> dict:
        with self._get_conn() as conn:
            projects = conn.execute("SELECT * FROM projects").fetchall()
            projects = [dict(p) for p in projects]
            on_track = sum(1 for p in projects if p["status"] in ("planning", "in_progress") and p["completion_pct"] < 100)
            completed = sum(1 for p in projects if p["status"] == "completed")
            delayed = sum(1 for p in projects if p["status"] == "delayed")
            total_budgeted = conn.execute("SELECT COALESCE(SUM(budgeted_cost), 0) FROM budget").fetchone()[0]
            total_actual = conn.execute("SELECT COALESCE(SUM(actual_cost), 0) FROM budget").fetchone()[0]
            return {
                "total_projects": len(projects),
                "on_track": on_track,
                "completed": completed,
                "delayed": delayed,
                "total_budgeted": total_budgeted,
                "total_actual": total_actual,
                "budget_health": "healthy" if total_actual <= total_budgeted else "over_budget",
            }
