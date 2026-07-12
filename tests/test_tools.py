"""
tests/test_tools.py
───────────────────
Smoke tests for the knowledge base tool.
No internet calls — only local JSON reads.
"""

import pytest
from tools.knowledge_tool import KnowledgeBaseTool


@pytest.fixture
def kb():
    return KnowledgeBaseTool()


def test_loads_sectors(kb):
    sectors = kb.get_all_sectors()
    assert len(sectors) >= 6
    assert "Solar Energy" in sectors


def test_loads_roles(kb):
    roles = kb.get_all_roles()
    assert len(roles) >= 15
    titles = [r["role"]["title"] for r in roles]
    assert "ESG Analyst" in titles


def test_loads_platforms(kb):
    platforms = kb.get_learning_platforms()
    assert len(platforms) >= 8
    names = [p["platform"] for p in platforms]
    assert "NPTEL (IIT/IISc)" in names


def test_find_roles_for_software_background(kb):
    roles = kb.find_roles_for_background("Software/IT")
    assert len(roles) > 0
    titles = [r["role"]["title"] for r in roles]
    assert any("Software" in t or "Analyst" in t for t in titles)


def test_find_roles_for_finance_background(kb):
    roles = kb.find_roles_for_background("Finance/Commerce")
    titles = [r["role"]["title"] for r in roles]
    assert any("Finance" in t or "ESG" in t for t in titles)


def test_format_role_summary(kb):
    roles = kb.get_all_roles()
    summary = kb.format_role_summary(roles[0])
    assert "Role" in summary
    assert "Salary" in summary


def test_get_policy_context(kb):
    policy = kb.get_policy_context()
    assert "net_zero_target" in policy