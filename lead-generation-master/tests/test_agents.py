import tempfile


def test_duplicate_detection():
    from lead_gen_master.agents.duplicate_detection import (
        DuplicateDetectionAgent,
    )
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        agent = DuplicateDetectionAgent(memory=mem)

        leads = [
            {
                "lead_id": "001",
                "company_name": "Acme Corp",
                "website": "https://acme.com",
                "notes": "First entry",
            },
            {
                "lead_id": "002",
                "company_name": "Acme Corp",
                "website": "",
                "notes": "Second entry (duplicate name)",
            },
            {
                "lead_id": "003",
                "company_name": "Other Inc",
                "website": "https://other.com",
                "notes": "Unique",
            },
        ]

        result = agent.deduplicate(leads)
        assert len(result) == 2
        names = {r["company_name"] for r in result}
        assert "Acme Corp" in names
        assert "Other Inc" in names


def test_crm_management():
    from lead_gen_master.agents.crm_management import (
        CRMManagementAgent,
        CRM_FIELDS,
    )
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        agent = CRMManagementAgent(memory=mem)

        leads = [
            {
                "lead_id": "001",
                "company_name": "Test Corp",
                "industry": "Tech",
            }
        ]
        records = agent.structure_records(leads)
        assert len(records) == 1
        for field in CRM_FIELDS:
            assert field in records[0]

        rows = agent.to_csv_rows(leads)
        assert rows[0] == CRM_FIELDS
        assert len(rows) == 2


def test_lead_qualification_rule_based():
    from lead_gen_master.agents.lead_qualification import (
        LeadQualificationAgent,
    )
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        agent = LeadQualificationAgent(llm=None, memory=mem)

        leads = [
            {
                "lead_id": "001",
                "company_name": "Strong Lead Inc",
                "website": "https://strong.com",
                "rating": 4.5,
                "review_count": 25,
            },
            {
                "lead_id": "002",
                "company_name": "Weak Lead LLC",
                "website": "",
                "rating": 0,
                "review_count": 0,
            },
        ]

        result = agent.qualify_leads(leads)
        assert result[0]["lead_score"] >= result[1]["lead_score"]


def test_executive_report():
    from lead_gen_master.agents.executive_report import (
        ExecutiveReportAgent,
    )
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        agent = ExecutiveReportAgent(llm=None, memory=mem)

        leads = [
            {
                "lead_id": "001",
                "company_name": "Alpha Corp",
                "industry": "Real Estate",
                "lead_score": 85,
                "priority": "High",
                "recommended_service": "Website Design",
            },
            {
                "lead_id": "002",
                "company_name": "Beta LLC",
                "industry": "Real Estate",
                "lead_score": 30,
                "priority": "Low",
                "recommended_service": "SEO",
            },
        ]

        report = agent.generate(leads)
        assert "DAILY EXECUTIVE REPORT" in report
        assert "Alpha Corp" in report
        assert "Total Leads Found:     2" in report
        assert "85" in report
