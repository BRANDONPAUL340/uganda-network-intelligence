from pathlib import Path


def test_dockerfile_exists():
    """ARRANGE, ACT & ASSERT: Verifies the secure, non-root Dockerfile is on disk."""
    assert Path("Dockerfile").exists()


def test_dockerignore_exists():
    assert Path(".dockerignore").exists()


def test_main_compose_exists():
    assert Path("docker-compose.yml").exists()


def test_test_compose_exists():
    assert Path("docker-compose.test.yml").exists()


def test_production_compose_exists():
    assert Path("docker-compose.prod.yml").exists()


def test_test_environment_template_exists():
    assert Path(".env.test.example").exists()


def test_production_environment_template_exists():
    assert Path(".env.prod.example").exists()
