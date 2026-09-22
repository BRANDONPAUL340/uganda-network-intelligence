from src.version import PROJECT_VERSION


def test_project_version_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the central project version string is instantiated [INDEX]."""
    assert PROJECT_VERSION is not None
    assert len(PROJECT_VERSION) > 0


def test_project_version_format():
    """ARRANGE, ACT & ASSERT: Validates that the application version string strictly matches MAJOR.MINOR.PATCH format [INDEX]."""
    parts = PROJECT_VERSION.split(".")

    assert len(parts) == 3, f"Version '{PROJECT_VERSION}' must have exactly three numeric segments."
    assert all(part.isdigit() for part in parts), f"All segments in version '{PROJECT_VERSION}' must be integers."
