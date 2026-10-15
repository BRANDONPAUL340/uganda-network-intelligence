
"""Explainable, measurement-level network degradation detection.

This module deliberately does not read from or write to the database.
It evaluates site measurement history and returns an auditable assessment.

Risk scores are heuristic scores, not probabilities of failure.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from statistics import median
from typing import Any, Iterable, Mapping

from src.config import (
    CRITICAL_AVAILABILITY_PCT,
    CRITICAL_LATENCY_MS,
    CRITICAL_PACKET_LOSS_PCT,
    WARNING_AVAILABILITY_PCT,
    WARNING_LATENCY_MS,
    WARNING_PACKET_LOSS_PCT,
)


# The first version requires enough observations to compare two periods.
MIN_OBSERVATIONS = 6
MIN_DISTINCT_DAYS = 2
RECENT_WINDOW_SIZE = 3
FRESHNESS_LIMIT_HOURS = 24

METRIC_CONFIG = {
    "latency_ms": {
        "label": "Latency",
        "direction": "higher_is_worse",
        "warning": WARNING_LATENCY_MS,
        "critical": CRITICAL_LATENCY_MS,
        "minimum_change": 10.0,
        "relative_change": 0.20,
        "unit": "ms",
    },
    "packet_loss_pct": {
        "label": "Packet loss",
        "direction": "higher_is_worse",
        "warning": WARNING_PACKET_LOSS_PCT,
        "critical": CRITICAL_PACKET_LOSS_PCT,
        "minimum_change": 1.0,
        "relative_change": 0.0,
        "unit": "percentage points",
    },
    "availability_pct": {
        "label": "Availability",
        "direction": "lower_is_worse",
        "warning": WARNING_AVAILABILITY_PCT,
        "critical": CRITICAL_AVAILABILITY_PCT,
        "minimum_change": 2.0,
        "relative_change": 0.0,
        "unit": "percentage points",
    },
    "signal_strength_dbm": {
        "label": "Signal strength",
        "direction": "lower_is_worse",
        "warning": None,
        "critical": None,
        "minimum_change": 5.0,
        "relative_change": 0.0,
        "unit": "dBm",
    },
}


def _parse_timestamp(value: Any) -> datetime | None:
    """Convert supported timestamp values to timezone-aware UTC."""
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if result.tzinfo is None:
        # Database timestamps without timezone information are interpreted
        # consistently as UTC. Confirm this matches your database convention.
        result = result.replace(tzinfo=timezone.utc)

    return result.astimezone(timezone.utc)


def _number(value: Any) -> float | None:
    """Return a finite numeric value, or None for invalid/missing values."""
    if value is None or isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if result != result or result in (float("inf"), float("-inf")):
        return None

    return result


def _threshold_state(metric: str, value: float) -> str:
    """Classify an observation using configured absolute thresholds."""
    config = METRIC_CONFIG[metric]

    if metric == "availability_pct":
        if value <= config["critical"]:
            return "CRITICAL"
        if value <= config["warning"]:
            return "WARNING"
    elif metric in ("latency_ms", "packet_loss_pct"):
        if value >= config["critical"]:
            return "CRITICAL"
        if value >= config["warning"]:
            return "WARNING"

    return "NORMAL"


def _is_deteriorating(
    metric: str,
    baseline: float,
    recent: float,
) -> bool:
    """Detect a material change in the undesirable direction."""
    config = METRIC_CONFIG[metric]
    minimum = config["minimum_change"]

    if config["direction"] == "higher_is_worse":
        change = recent - baseline
        relative = change / max(abs(baseline), 1.0)
    else:
        change = baseline - recent
        relative = change / max(abs(baseline), 1.0)

    if change < minimum:
        return False

    required_relative = config["relative_change"]
    return relative >= required_relative


def evaluate_site_history(
    records: Iterable[Mapping[str, Any]],
    *,
    now: datetime | None = None,
    min_observations: int = MIN_OBSERVATIONS,
    min_distinct_days: int = MIN_DISTINCT_DAYS,
    recent_window_size: int = RECENT_WINDOW_SIZE,
    freshness_limit_hours: float = FRESHNESS_LIMIT_HOURS,
) -> dict[str, Any]:
    """Evaluate one site's chronological or unordered measurement records.

    Each record should contain measured_at and any of:
    site_id, site_name, latency_ms, packet_loss_pct,
    availability_pct, signal_strength_dbm.

    Returns a dictionary with status, heuristic risk score, findings,
    evidence, and a human-readable explanation.
    """
    current_time = _parse_timestamp(now or datetime.now(timezone.utc))
    if current_time is None:
        raise ValueError("now must be a valid datetime")

    prepared = []
    for record in records:
        timestamp = _parse_timestamp(record.get("measured_at"))
        if timestamp is None:
            continue

        prepared.append({
            **record,
            "_timestamp": timestamp,
        })

    prepared.sort(key=lambda item: item["_timestamp"])

    if not prepared:
        return {
            "status": "INSUFFICIENT_DATA",
            "risk_score": None,
            "site_id": None,
            "site_name": None,
            "observation_count": 0,
            "latest_measurement_at": None,
            "findings": [],
            "reason": "No valid timestamped measurements are available.",
        }

    latest = prepared[-1]
    site_id = latest.get("site_id")
    site_name = latest.get("site_name") or (
        f"Site {site_id}" if site_id is not None else "Unnamed site"
    )
    age_hours = (
        current_time - latest["_timestamp"]
    ).total_seconds() / 3600

    base_result = {
        "site_id": site_id,
        "site_name": site_name,
        "observation_count": len(prepared),
        "latest_measurement_at": latest["_timestamp"].isoformat(),
        "data_age_hours": round(max(age_hours, 0.0), 2),
        "findings": [],
    }


    
    # A stale latest observation takes priority because it cannot
    # establish current network health, regardless of sample count.
    if age_hours > freshness_limit_hours:
        return {
            **base_result,
            "status": "STALE_DATA",
            "risk_score": None,
            "reason": (
                f"The latest measurement is {age_hours:.1f} hours old. "
                "Refresh the data before assessing current network risk."
            ),
        }

    distinct_days = {
        item["_timestamp"].date()
        for item in prepared
    }

    if (
        len(prepared) < min_observations
        or len(distinct_days) < min_distinct_days
        or recent_window_size < 2
        or len(prepared) < recent_window_size * 2
    ):
        return {
            **base_result,
            "status": "INSUFFICIENT_DATA",
            "risk_score": None,
            "reason": (
                f"Need at least {min_observations} observations across "
                f"{min_distinct_days} distinct days, with at least "
                f"{recent_window_size} observations in each comparison "
                "window."
            ),
        }

    split = len(prepared) - recent_window_size
    baseline_rows = prepared[:split]
    recent_rows = prepared[split:]

    findings = []
    risk_score = 0
    critical_breach = False
    warning_breach = False
    deteriorating_metrics = []

    for metric, config in METRIC_CONFIG.items():
        baseline_values = [
            value
            for row in baseline_rows
            if (value := _number(row.get(metric))) is not None
        ]
        recent_values = [
            value
            for row in recent_rows
            if (value := _number(row.get(metric))) is not None
        ]

        # A metric is assessed only when both windows have evidence.
        if not baseline_values or not recent_values:
            continue

        baseline_value = median(baseline_values)
        recent_value = median(recent_values)
        threshold = _threshold_state(metric, recent_value)
        deteriorating = _is_deteriorating(
            metric, baseline_value, recent_value
        )

        if deteriorating:
            deteriorating_metrics.append(metric)
            risk_score += 20

        if threshold == "CRITICAL":
            risk_score += 40
            critical_breach = True
        elif threshold == "WARNING":
            risk_score += 20
            warning_breach = True

        if config["direction"] == "higher_is_worse":
            raw_change = recent_value - baseline_value
        else:
            raw_change = baseline_value - recent_value

        findings.append({
            "metric": metric,
            "label": config["label"],
            "unit": config["unit"],
            "baseline_median": round(baseline_value, 3),
            "recent_median": round(recent_value, 3),
            "change_toward_degradation": round(raw_change, 3),
            "threshold_state": threshold,
            "deteriorating": deteriorating,
            "explanation": (
                f"{config['label']} changed from "
                f"{baseline_value:.2f} to {recent_value:.2f} "
                f"{config['unit']} across the comparison windows."
            ),
        })

    risk_score = min(risk_score, 100)

    if critical_breach or risk_score >= 70:
        status = "CRITICAL"
    elif warning_breach or risk_score >= 40:
        status = "WARNING"
    elif deteriorating_metrics:
        status = "WATCH"
    else:
        status = "HEALTHY"

    if not findings:
        status = "INSUFFICIENT_DATA"
        risk_score = None
        reason = "No metric had valid values in both comparison windows."
    else:
        reason = (
            f"{len(deteriorating_metrics)} metric(s) show material "
            "deterioration; "
            f"{sum(f['threshold_state'] == 'WARNING' for f in findings)} "
            "metric(s) are at warning thresholds; "
            f"{sum(f['threshold_state'] == 'CRITICAL' for f in findings)} "
            "metric(s) are at critical thresholds."
        )

    return {
        **base_result,
        "status": status,
        "risk_score": risk_score,
        "baseline_observations": len(baseline_rows),
        "recent_observations": len(recent_rows),
        "deteriorating_metrics": deteriorating_metrics,
        "findings": findings,
        "reason": reason,
    }


def evaluate_all_sites(
    records: Iterable[Mapping[str, Any]],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Group measurement-level rows by site and evaluate each site."""
    grouped: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)

    for record in records:
        site_id = record.get("site_id")
        if site_id is not None:
            grouped[site_id].append(record)

    assessments = [
        evaluate_site_history(site_rows, **kwargs)
        for site_rows in grouped.values()
    ]

    priority = {
        "CRITICAL": 0,
        "WARNING": 1,
        "WATCH": 2,
        "INSUFFICIENT_DATA": 3,
        "STALE_DATA": 4,
        "HEALTHY": 5,
    }

    return sorted(
        assessments,
        key=lambda item: (
            priority.get(item["status"], 99),
            -(item["risk_score"] or 0),
            item["site_name"],
        ),
    )
