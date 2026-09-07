"""SQLite persistence shared by all departments."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteDatabase:
    """Tiny SQLite repository with WAL and foreign-key support."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        if self.path != ":memory:":
            connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS operations ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "department TEXT NOT NULL, "
                "action TEXT NOT NULL, "
                "status TEXT NOT NULL, "
                "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )

    def record_operation(self, department: str, action: str, status: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO operations(department, action, status) VALUES (?, ?, ?)",
                (department, action, status),
            )
            return int(cursor.lastrowid)

    def list_operations(self, department: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM operations"
        parameters: tuple[Any, ...] = ()
        if department:
            query += " WHERE department = ?"
            parameters = (department,)
        query += " ORDER BY id"
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, parameters)]
