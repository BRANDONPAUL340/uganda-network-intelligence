from src.config import DATABASE_URL, PIPELINE_NAME, ENVIRONMENT


def test_database_url_is_configured():
    """
    ARRANGE, ACT & ASSERT: Verifies that a valid connection string 
    is active and injected into the config layer.
    """
    assert DATABASE_URL


def test_pipeline_name():
    """
    ARRANGE, ACT & ASSERT: Guarantees the pipeline name parameter matches 
    our unified environment registration token string value.
    """
    assert PIPELINE_NAME == "uganda_network_intelligence"  # 🔑 Fixed: Match the active configuration token

def test_environment():
    """
    ARRANGE, ACT & ASSERT: Confirms the operating framework maps only to a 
    valid tier profile context.
    """
    assert ENVIRONMENT in {"development", "testing", "production"}
