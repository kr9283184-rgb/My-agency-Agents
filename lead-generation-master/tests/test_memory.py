import tempfile
import os


def test_memory_manager():
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        assert mem.summary()["total_leads"] == 0

        mem.add_lead({
            "lead_id": "test_001",
            "company_name": "Test Corp",
            "industry": "Tech",
        })
        assert mem.summary()["total_leads"] == 1

        lead = mem.get_lead("test_001")
        assert lead["company_name"] == "Test Corp"

        mem.update_lead("test_001", {"lead_score": 85})
        assert mem.get_lead("test_001")["lead_score"] == 85

        leads = mem.get_leads()
        assert len(leads) == 1

        mem.clear_all()
        assert mem.summary()["total_leads"] == 0


def test_memory_industries():
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        mem.add_industry({
            "industry": "Real Estate",
            "demand_score": 80,
        })
        assert len(mem.get_industries()) == 1


def test_memory_audits():
    from lead_gen_master.memory import MemoryManager

    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(output_dir=tmp)
        mem.add_audit({
            "lead_id": "test_001",
            "website": "example.com",
            "overall_quality": 75,
        })
        assert len(mem.get_audits()) == 1


def test_lead_schema():
    from lead_gen_master.memory.schemas import Lead

    lead = Lead(
        lead_id="001",
        company_name="Acme Inc",
    )
    d = lead.to_dict()
    assert d["lead_id"] == "001"
    assert d["company_name"] == "Acme Inc"
    assert d["lead_score"] == 0
    assert "created_at" in d
