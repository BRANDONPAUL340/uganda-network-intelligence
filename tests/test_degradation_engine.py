
from datetime import datetime, timedelta, timezone

from src.monitoring.degradation import (
    evaluate_site_history,
    evaluate_all_sites,
)


NOW = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)


def make_history(
    *,
    latency=(20, 21, 20, 22, 23, 24),
    packet_loss=(0.1, 0.2, 0.1, 0.2, 0.3, 0.4),
    availability=(99.8, 99.7, 99.8, 99.7, 99.6, 99.5),
    signal=(-65, -64, -65, -64, -63, -64),
):
    rows = []

    # Six observations spread across three days.
    for index in range(6):
        rows.append({
            "site_id": 12,
            "site_name": None,
            "measured_at": NOW - timedelta(
                hours=(5 - index) * 12
            ),
            "latency_ms": latency[index],
            "packet_loss_pct": packet_loss[index],
            "availability_pct": availability[index],
            "signal_strength_dbm": signal[index],
        })

    return rows


def test_healthy_history_has_no_degradation():
    result = evaluate_site_history(
        make_history(),
        now=NOW,
    )

    assert result["status"] == "HEALTHY"
    assert result["risk_score"] == 0
    assert result["site_name"] == "Site 12"


def test_critical_latency_is_explained():
    rows = make_history(
        latency=(20, 21, 20, 80, 85, 90)
    )

    result = evaluate_site_history(rows, now=NOW)

    assert result["status"] == "CRITICAL"
    assert result["risk_score"] is not None

    latency = next(
        finding for finding in result["findings"]
        if finding["metric"] == "latency_ms"
    )

    assert latency["threshold_state"] == "CRITICAL"
    assert latency["recent_median"] >= 70
    assert latency["explanation"]


def test_material_deterioration_produces_watch_or_higher():
    rows = make_history(
        latency=(20, 21, 20, 35, 38, 40)
    )

    result = evaluate_site_history(rows, now=NOW)

    assert result["status"] in {"WATCH", "WARNING", "CRITICAL"}
    assert "latency_ms" in result["deteriorating_metrics"]


def test_stale_measurements_are_not_scored():
    rows = make_history()
    old_now = NOW + timedelta(days=3)

    result = evaluate_site_history(rows, now=old_now)

    assert result["status"] == "STALE_DATA"
    assert result["risk_score"] is None


def test_insufficient_history_is_not_scored():
    rows = make_history()[:3]

    result = evaluate_site_history(
        rows,
        now=NOW - timedelta(hours=24),
    )

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["risk_score"] is None


def test_missing_metric_values_do_not_crash():
    rows = make_history()

    for row in rows:
        row["latency_ms"] = None
        row["packet_loss_pct"] = None
        row["availability_pct"] = None
        row["signal_strength_dbm"] = None

    result = evaluate_site_history(rows, now=NOW)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["risk_score"] is None


def test_sites_are_ranked_by_severity():
    healthy = make_history()
    critical = make_history(
        latency=(20, 21, 20, 80, 85, 90)
    )

    for row in healthy:
        row["site_id"] = 1
        row["site_name"] = "Healthy site"

    for row in critical:
        row["site_id"] = 2
        row["site_name"] = "Critical site"

    results = evaluate_all_sites(
        healthy + critical,
        now=NOW,
    )

    assert results[0]["site_id"] == 2
    assert results[0]["status"] == "CRITICAL"
