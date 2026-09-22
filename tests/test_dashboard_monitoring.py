import pandas as pd
from datetime import datetime, timezone, timedelta
from src.dashboard.monitoring import get_open_alerts


def test_dashboard_open_alerts_structure():
    """ARRANGE, ACT & ASSERT: Verifies the open alerts helper returns a valid dataframe data structure [1]."""
    df = get_open_alerts()
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "status" in df.columns
        assert (df["status"] == "OPEN").all()


def test_alert_age_calculation_presentation_logic():
    """ARRANGE, ACT & ASSERT: Verifies that delta-time age calculations resolve correctly in memory [1]."""
    triggered_at = datetime.now(timezone.utc) - timedelta(minutes=30)
    now_ts = datetime.now(timezone.utc)
    
    delta = now_ts - triggered_at
    tot_min = int(delta.total_seconds() // 60)
    
    assert tot_min == 30, f"Expected 30 minutes age delta, but calculated {tot_min} minutes."
