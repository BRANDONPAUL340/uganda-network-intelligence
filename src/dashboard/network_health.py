
"""Transparent, threshold-based network site health scoring."""

import math

from src.config import (
    CRITICAL_AVAILABILITY_PCT,
    CRITICAL_LATENCY_MS,
    CRITICAL_PACKET_LOSS_PCT,
    WARNING_AVAILABILITY_PCT,
    WARNING_LATENCY_MS,
    WARNING_PACKET_LOSS_PCT,
)


def _number(value):
    """Convert a measurement to a finite float, or return None."""
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def assess_site(row):
    """Return a score, risk status, explanations, and next steps for one site.

    Scoring is a transparent heuristic, not a carrier-certified SLA.
    Critical breaches deduct 35 points per affected metric; warning-only
    breaches deduct 15 points. The final score is bounded between 0 and 100.
    """
    get_value = row.get if hasattr(row, "get") else lambda key, default=None: default

    latency = _number(get_value("avg_latency_ms"))
    packet_loss = _number(get_value("avg_packet_loss_pct"))
    availability = _number(get_value("avg_availability_pct"))
    measurements = _number(get_value("measurement_count"))

    reasons = []
    recommendations = []
    critical_breaches = []
    warning_breaches = []

    metrics = [
        (
            "Latency",
            latency,
            lambda value: value >= CRITICAL_LATENCY_MS,
            lambda value: value >= WARNING_LATENCY_MS,
            f"Investigate congestion, backhaul capacity, and routing.",
        ),
        (
            "Packet loss",
            packet_loss,
            lambda value: value >= CRITICAL_PACKET_LOSS_PCT,
            lambda value: value >= WARNING_PACKET_LOSS_PCT,
            "Inspect link errors, congestion, and radio/backhaul quality.",
        ),
        (
            "Availability",
            availability,
            lambda value: value < CRITICAL_AVAILABILITY_PCT,
            lambda value: value < WARNING_AVAILABILITY_PCT,
            "Review outage events, power, and site connectivity.",
        ),
    ]

    score = 100
    usable_metrics = 0

    for label, value, is_critical, is_warning, recommendation in metrics:
        if value is None:
            continue

        usable_metrics += 1

        if is_critical(value):
            critical_breaches.append(label)
            reasons.append(f"{label} is beyond the critical threshold ({value:g}).")
            recommendations.append(recommendation)
            score -= 35
        elif is_warning(value):
            warning_breaches.append(label)
            reasons.append(f"{label} has crossed the warning threshold ({value:g}).")
            recommendations.append(recommendation)
            score -= 15

    if critical_breaches:
        status = "Critical"
    elif warning_breaches:
        status = "Warning"
    elif usable_metrics < 3 or measurements is None or measurements < 1:
        status = "Insufficient data"
        reasons.append("Not all three performance metrics and a valid measurement count are available.")
        recommendations.append("Collect and validate more site measurements before assessing health.")
    else:
        status = "Healthy"
        reasons.append("All three available metrics are within the configured warning thresholds.")


    if status in {"Critical", "Warning"} and (
        usable_metrics < 3 or measurements is None or measurements < 1
    ):
        reasons.append(
            "Some performance metrics or the measurement count are missing; "
            "interpret this assessment with caution."
        )
        recommendations.append(
            "Validate measurement completeness before closing the investigation."
        )


    if not usable_metrics:
        score = None
        status = "Insufficient data"
        if not recommendations:
            recommendations.append("Collect valid latency, packet-loss, and availability measurements.")
    else:
        score = max(0, min(100, score))

    # Remove duplicate recommendations while preserving their order.
    recommendations = list(dict.fromkeys(recommendations))

    return {
        "health_score": score,
        "risk_status": status,
        "reasons": reasons,
        "recommendations": recommendations,
        "usable_metric_count": usable_metrics,
    }
