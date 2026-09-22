from src.dashboard.health import get_deployment_info


def test_deployment_info_contains_version():
    """ARRANGE, ACT & ASSERT: Guarantees the deployment version metadata string exists [INDEX]."""
    result = get_deployment_info()

    assert "version" in result
    assert result["version"] == "1.0.1"


def test_deployment_info_contains_environment():
    """ARRANGE, ACT & ASSERT: Guarantees the active runtime environment parameter is tracked [INDEX]."""
    result = get_deployment_info()

    assert "environment" in result
    assert result["environment"]
