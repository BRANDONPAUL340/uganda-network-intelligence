from src.transformation.silver import load_silver_measurements


def test_silver_load_contract():
    """
    ARRANGE, ACT & ASSERT: Verifies that our upgraded denormalized Silver fact
    loader compiles correctly and exposes an active, callable interface.
    """
    assert callable(load_silver_measurements)
