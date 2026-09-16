from pathlib import Path


def test_performance_document_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the master performance log exists in the docs folder [INDEX]."""
    path = Path("docs/performance.md")
    assert path.exists()


def test_partitioning_document_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the partitioning strategy document exists in the docs folder [INDEX]."""
    path = Path("docs/partitioning.md")
    assert path.exists()
