from pathlib import Path


def test_operational_kpi_documentation_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the KPI manual exists and tracks core terms [INDEX]."""
    path = Path("docs/operational_kpis.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    required_terms = [
        "Pipeline KPIs",
        "Health KPIs",
        "Alert KPIs",
        "Stage KPIs",
        "pipeline_kpis",
        "pipeline_stage_summary",
        "daily_pipeline_health",
        "current_pipeline_health",
    ]

    for term in required_terms:
        assert term in content, f"Mandatory term '{term}' is missing from operational KPI documentation."
