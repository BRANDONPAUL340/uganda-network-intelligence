from pathlib import Path


def test_query_optimization_documentation_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the query optimization log exists and tracks core terms [INDEX]."""
    path = Path("docs/query_optimization.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "EXPLAIN" in content
    assert "ANALYZE" in content
    assert "Index Strategy" in content
    assert "Statistics" in content
