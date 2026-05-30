import os
import tempfile
import json
from project_management.database import ProjectDatabase
from project_management.agents.planning_agent import PlanningAgent
from project_management.agents.resource_allocation_agent import ResourceAllocationAgent
from project_management.agents.task_management_agent import TaskManagementAgent
from project_management.agents.team_coordination_agent import TeamCoordinationAgent
from project_management.agents.progress_tracking_agent import ProgressTrackingAgent
from project_management.agents.risk_management_agent import RiskManagementAgent
from project_management.agents.change_request_agent import ChangeRequestAgent
from project_management.agents.budget_profitability_agent import BudgetProfitabilityAgent
from project_management.agents.client_communication_agent import ClientCommunicationAgent
from project_management.agents.quality_coordination_agent import QualityCoordinationAgent
from project_management.agents.delivery_management_agent import DeliveryManagementAgent
from project_management.agents.knowledge_management_agent import KnowledgeManagementAgent


SAMPLE_PROJECT = {
    "project_id": "test-proj-001",
    "lead_id": "lead-001",
    "company_name": "Test Company",
    "contact_name": "John Doe",
    "email": "john@test.com",
    "whatsapp_phone": "+1234567890",
    "industry": "technology",
    "proposal_type": "website",
    "deal_amount": 5000.0,
    "status": "planning",
    "priority": "high",
}


class TestAgentBase:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.tmp_dir, "test_pm.db")
        self.db = ProjectDatabase(db_path)
        self.db.add_project(SAMPLE_PROJECT)

    def teardown_method(self):
        pass


class TestPlanningAgent(TestAgentBase):
    def test_create_project_plan(self):
        agent = PlanningAgent(db=self.db)
        result = agent.create_project_plan(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["total_weeks"] > 0
        assert len(result["milestones"]) == 5
        assert result["tasks_count"] > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content
            assert "Master Project Plan" in content
            assert "Milestones" in content

    def test_create_project_plan_automation(self):
        agent = PlanningAgent(db=self.db)
        project = dict(SAMPLE_PROJECT, proposal_type="automation")
        result = agent.create_project_plan(project, self.tmp_dir)
        assert result["total_weeks"] > 0
        assert len(result["milestones"]) == 5

    def test_milestones_stored_in_db(self):
        agent = PlanningAgent(db=self.db)
        agent.create_project_plan(SAMPLE_PROJECT, self.tmp_dir)
        milestones = self.db.get_milestones("test-proj-001")
        assert len(milestones) == 5
        assert milestones[0]["title"] == "Discovery & Research"
        assert milestones[4]["title"] == "Launch & Deploy"

    def test_tasks_stored_in_db(self):
        agent = PlanningAgent(db=self.db)
        agent.create_project_plan(SAMPLE_PROJECT, self.tmp_dir)
        tasks = self.db.get_tasks("test-proj-001")
        assert len(tasks) > 0
        assert tasks[0]["project_id"] == "test-proj-001"


class TestResourceAllocationAgent(TestAgentBase):
    def test_allocate_resources(self):
        agent = ResourceAllocationAgent(db=self.db)
        result = agent.allocate_resources(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["total_resources"] >= 4
        assert "Website" in result["department"]
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Resource Assignment Report" in content
            assert "Test Company" in content

    def test_resources_stored_in_db(self):
        agent = ResourceAllocationAgent(db=self.db)
        agent.allocate_resources(SAMPLE_PROJECT, self.tmp_dir)
        resources = self.db.get_resources("test-proj-001")
        assert len(resources) >= 4
        depts = [r["department"] for r in resources]
        assert "Website & Design Department" in depts


class TestTaskManagementAgent(TestAgentBase):
    def test_manage_tasks_no_tasks(self):
        agent = TaskManagementAgent(db=self.db)
        result = agent.manage_tasks(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["dashboard"]["total"] == 0

    def test_manage_tasks_with_tasks(self):
        self.db.add_task({"project_id": "test-proj-001", "title": "Test task", "state": "pending", "priority": "high"})
        agent = TaskManagementAgent(db=self.db)
        result = agent.manage_tasks(SAMPLE_PROJECT, self.tmp_dir)
        assert result["dashboard"]["total"] == 1

    def test_assign_task(self):
        tid = self.db.add_task({"project_id": "test-proj-001", "title": "Task", "state": "pending"})
        agent = TaskManagementAgent(db=self.db)
        assert agent.assign_task(tid, "John")
        task = self.db.get_tasks("test-proj-001")[0]
        assert task["owner"] == "John"
        assert task["state"] == "assigned"

    def test_complete_task(self):
        tid = self.db.add_task({"project_id": "test-proj-001", "title": "Task", "state": "in_progress"})
        agent = TaskManagementAgent(db=self.db)
        assert agent.complete_task(tid)
        task = self.db.get_tasks("test-proj-001")[0]
        assert task["state"] == "completed"
        assert task["progress_pct"] == 100.0


class TestTeamCoordinationAgent(TestAgentBase):
    def test_coordinate_teams(self):
        self.db.add_resource({"project_id": "test-proj-001", "department": "Website & Design Department", "role": "Designer", "allocation_pct": 100})
        agent = TeamCoordinationAgent(db=self.db)
        result = agent.coordinate_teams(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert len(result["departments"]) > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Coordination Report" in content


class TestProgressTrackingAgent(TestAgentBase):
    def test_track_progress_daily(self):
        agent = ProgressTrackingAgent(db=self.db)
        result = agent.track_progress(SAMPLE_PROJECT, self.tmp_dir, "daily")
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["completion_pct"] >= 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Daily Progress Report" in content

    def test_track_progress_weekly(self):
        agent = ProgressTrackingAgent(db=self.db)
        result = agent.track_progress(SAMPLE_PROJECT, self.tmp_dir, "weekly")
        assert "Weekly Progress Report" in open(result["file_path"]).read()

    def test_track_progress_monthly(self):
        agent = ProgressTrackingAgent(db=self.db)
        result = agent.track_progress(SAMPLE_PROJECT, self.tmp_dir, "monthly")
        assert "Monthly Executive Report" in open(result["file_path"]).read()

    def test_completion_with_tasks(self):
        self.db.add_task({"project_id": "test-proj-001", "title": "T1", "state": "completed", "estimated_hours": 10})
        self.db.add_task({"project_id": "test-proj-001", "title": "T2", "state": "pending", "estimated_hours": 10})
        agent = ProgressTrackingAgent(db=self.db)
        result = agent.track_progress(SAMPLE_PROJECT, self.tmp_dir)
        assert result["completion_pct"] == 50.0

    def test_delay_detection(self):
        import datetime
        future = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        self.db.add_milestone({"project_id": "test-proj-001", "title": "Overdue", "phase": 1, "due_date": "2020-01-01", "status": "pending"})
        self.db.add_milestone({"project_id": "test-proj-001", "title": "Future", "phase": 2, "due_date": future, "status": "pending"})
        agent = ProgressTrackingAgent(db=self.db)
        result = agent.track_progress(SAMPLE_PROJECT, self.tmp_dir)
        delays = result["delay_indicators"]
        assert len(delays) >= 1
        assert any(d["type"] == "milestone_overdue" for d in delays)


class TestRiskManagementAgent(TestAgentBase):
    def test_manage_risks(self):
        agent = RiskManagementAgent(db=self.db)
        result = agent.manage_risks(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert len(result["risks"]) > 0
        assert result["risk_score"] > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Risk Register" in content
            assert "Test Company" in content

    def test_risks_stored_in_db(self):
        agent = RiskManagementAgent(db=self.db)
        agent.manage_risks(SAMPLE_PROJECT, self.tmp_dir)
        risks = self.db.get_risks("test-proj-001")
        assert len(risks) > 0


class TestChangeRequestAgent(TestAgentBase):
    def test_process_change_request(self):
        agent = ChangeRequestAgent(db=self.db)
        cr_data = {
            "title": "Add Analytics",
            "description": "Integrate Google Analytics",
            "estimated_hours": 8,
            "complexity": "low",
            "requested_by": "Client",
        }
        result = agent.process_change_request(SAMPLE_PROJECT, cr_data, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["status"] == "pending_approval"
        assert result["impact"]["effort_hours"] > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Change Request Report" in content
            assert "Add Analytics" in content

    def test_approve_request(self):
        cr_id = self.db.add_change_request({
            "project_id": "test-proj-001",
            "title": "Test CR",
            "status": "pending",
        })
        agent = ChangeRequestAgent(db=self.db)
        result = agent.approve_request(cr_id, "PM", True)
        assert result["status"] == "approved"

    def test_reject_request(self):
        cr_id = self.db.add_change_request({
            "project_id": "test-proj-001",
            "title": "Test CR",
            "status": "pending",
        })
        agent = ChangeRequestAgent(db=self.db)
        result = agent.approve_request(cr_id, "PM", False, "Out of scope")
        assert result["status"] == "rejected"


class TestBudgetProfitabilityAgent(TestAgentBase):
    def test_track_budget(self):
        agent = BudgetProfitabilityAgent(db=self.db)
        result = agent.track_budget(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["summary"]["deal_amount"] == 5000.0
        assert result["summary"]["budget_health"] in ("healthy", "over_budget")
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Budget Health" in content
            assert "Profitability" in content

    def test_log_hours(self):
        agent = BudgetProfitabilityAgent(db=self.db)
        agent.track_budget(SAMPLE_PROJECT, self.tmp_dir)
        result = agent.log_hours("test-proj-001", "development", 10, 750)
        assert result


class TestClientCommunicationAgent(TestAgentBase):
    def test_generate_weekly_update(self):
        agent = ClientCommunicationAgent(db=self.db)
        result = agent.generate_update(SAMPLE_PROJECT, "weekly", self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["update_type"] == "weekly"
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Weekly Project Update" in content or "Test Company" in content

    def test_generate_milestone_notification(self):
        agent = ClientCommunicationAgent(db=self.db)
        milestone = {"title": "Design Complete", "deliverables": "Wireframes, mockups"}
        result = agent.generate_milestone_notification(SAMPLE_PROJECT, milestone)
        assert "Milestone Completed" in result["subject"]

    def test_generate_delay_notification(self):
        agent = ClientCommunicationAgent(db=self.db)
        delay_info = {"description": "Design delayed", "impact": "Minor", "new_date": "2026-07-01", "mitigation": "Working extra"}
        result = agent.generate_delay_notification(SAMPLE_PROJECT, delay_info)
        assert "Schedule Adjustment" in result["subject"]

    def test_generate_delivery_notification(self):
        agent = ClientCommunicationAgent(db=self.db)
        result = agent.generate_delivery_notification(SAMPLE_PROJECT)
        assert "Project Delivered" in result["subject"]


class TestQualityCoordinationAgent(TestAgentBase):
    def test_verify_quality(self):
        agent = QualityCoordinationAgent(db=self.db)
        result = agent.verify_quality(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["readiness"]["total"] > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "QA Readiness Report" in content

    def test_pass_checkpoint(self):
        qc_id = self.db.add_quality_checkpoint({
            "project_id": "test-proj-001",
            "checkpoint_name": "Responsive Design",
            "status": "pending",
        })
        agent = QualityCoordinationAgent(db=self.db)
        agent.pass_checkpoint(qc_id, "QA Tester", "All good")
        checkpoints = self.db.get_quality_checkpoints("test-proj-001")
        assert checkpoints[0]["passed"] == 1

    def test_fail_checkpoint(self):
        qc_id = self.db.add_quality_checkpoint({
            "project_id": "test-proj-001",
            "checkpoint_name": "Load Speed",
            "status": "pending",
        })
        agent = QualityCoordinationAgent(db=self.db)
        agent.fail_checkpoint(qc_id, "QA Tester", "Too slow")
        checkpoints = self.db.get_quality_checkpoints("test-proj-001")
        assert checkpoints[0]["passed"] == 0


class TestDeliveryManagementAgent(TestAgentBase):
    def test_prepare_delivery(self):
        agent = DeliveryManagementAgent(db=self.db)
        result = agent.prepare_delivery(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert "delivery_ready" in result
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Delivery Package" in content
            assert "Test Company" in content


class TestKnowledgeManagementAgent(TestAgentBase):
    def test_capture_lessons(self):
        agent = KnowledgeManagementAgent(db=self.db)
        result = agent.capture_lessons(SAMPLE_PROJECT, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["total_lessons"] > 0
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Knowledge Base" in content
            assert "Lessons Learned" in content

    def test_lessons_stored_in_db(self):
        agent = KnowledgeManagementAgent(db=self.db)
        agent.capture_lessons(SAMPLE_PROJECT, self.tmp_dir)
        lessons = self.db.get_lessons("test-proj-001")
        assert len(lessons) > 0
        assert any("kickoff" in l.get("tags", "") for l in lessons)
