def test_package_imports():
    from security_department.config import Config
    from security_department.database import SecurityDatabase
    from security_department.orchestrator import SecurityOrchestrator, SecurityResult
    from security_department.cli import main

    assert Config is not None
    assert SecurityDatabase is not None
    assert SecurityOrchestrator is not None
    assert SecurityResult is not None
    assert callable(main)


def test_agent_imports():
    from security_department.agents.base_agent import BaseAgent
    from security_department.agents.chief_security_officer_agent import ChiefSecurityOfficerAgent
    from security_department.agents.specialists import (
        ApplicationSecurityAgent,
        VulnerabilityManagementAgent,
        ThreatDetectionAgent,
        AISecurityAgent,
        BackupRecoveryAgent,
    )

    assert BaseAgent is not None
    assert ChiefSecurityOfficerAgent is not None
    assert ApplicationSecurityAgent is not None
    assert VulnerabilityManagementAgent is not None
    assert ThreatDetectionAgent is not None
    assert AISecurityAgent is not None
    assert BackupRecoveryAgent is not None
