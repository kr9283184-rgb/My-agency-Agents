from core.agent import BaseAgent
from core.database import SQLiteDatabase
from core.orchestrator import BaseOrchestrator


def test_database_records_and_lists_operations():
    db = SQLiteDatabase(":memory:")
    operation_id = db.record_operation("testing", "smoke", "completed")
    rows = db.list_operations("testing")
    assert operation_id == 1
    assert rows[0]["action"] == "smoke"
    assert rows[0]["status"] == "completed"


def test_orchestrator_executes_items_and_returns_summary():
    db = SQLiteDatabase(":memory:")
    orchestrator = BaseOrchestrator(db=db, agent=BaseAgent("test-worker"))
    result = orchestrator.run([{"id": 1}, {"id": 2}])
    assert result.total_items == 2
    assert result.executed == 2
    assert result.failed == 0
    assert result.summary()["department"] == "core"


def test_status_exposes_persisted_operations():
    db = SQLiteDatabase(":memory:")
    orchestrator = BaseOrchestrator(db=db)
    orchestrator.run([{"id": "one"}])
    status = orchestrator.status()
    assert len(status["operations"]) == 1
    assert status["operations"][0]["status"] == "completed"
