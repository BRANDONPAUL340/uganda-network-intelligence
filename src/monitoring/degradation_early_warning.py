"""Site-level degradation detection using robust historical baselines."""

import pandas as pd

from src.config import (
    WARNING_LATENCY_MS,
    CRITICAL_LATENCY_MS,
    WARNING_PACKET_LOSS_PCT,
    CRITICAL_PACKET_LOSS_PCT,
    WARNING_AVAILABILITY_PCT,
    CRITICAL_AVAILABILITY_PCT,
)

METRICS = {
    "latency_ms": {
        "label": "Latency",
        "direction": "higher",
        "unit": "ms",
        "static_warning": WARNING_LATENCY_MS,
        "static_critical": CRITICAL_LATENCY_MS,
    },
    "packet_loss_pct": {
        "label": "Packet loss",
        "direction": "higher",
        "unit": "%",
        "static_warning": WARNING_PACKET_LOSS_PCT,
        "static_critical": CRITICAL_PACKET_LOSS_PCT,
    },
    "availability_pct": {
        "label": "Availability",
        "direction": "lower",
        "unit": "%",
        "static_warning": WARNING_AVAILABILITY_PCT,
        "static_critical": CRITICAL_AVAILABILITY_PCT,
    },
}

MIN_BASELINE_SAMPLES = 5
ANOMALY_SCORE_THRESHOLD = 3.5
REGRESSION_WINDOW_SIZE = 3
REGRESSION_MIN_HISTORY = 6
REGRESSION_MIN_CHANGE_PCT = 10.0


def detect_slow_regression(
    site_df: pd.DataFrame,
    metric: str,
    direction: str,
) -> dict:
    result = {
        "regression_detected": False,
        "regression_change_pct": None,
        "regression_reason": None,
    }

    required_columns = {"measured_at", metric}
    if not required_columns.issubset(site_df.columns):
        return result

    data = site_df[["measured_at", metric]].copy()
    data["measured_at"] = pd.to_datetime(
        data["measured_at"], errors="coerce"
    )
    data[metric] = pd.to_numeric(data[metric], errors="coerce")
    data = data.dropna(subset=["measured_at", metric])
    data = data.sort_values("measured_at")

    # Use a recent 7-day window and an earlier 7-day window.
    if data.empty:
        return result

    latest_time = data["measured_at"].max()
    recent_start = latest_time - pd.Timedelta(days=7)
    history_start = latest_time - pd.Timedelta(days=14)

    historical = data.loc[
        (data["measured_at"] >= history_start)
        & (data["measured_at"] < recent_start),
        metric,
    ]
    recent = data.loc[
        (data["measured_at"] >= recent_start)
        & (data["measured_at"] <= latest_time),
        metric,
    ]

    if (
        len(historical) < REGRESSION_MIN_HISTORY
        or len(recent) < REGRESSION_WINDOW_SIZE
    ):
        return result

    expected = float(historical.median())
    observed = float(recent.median())

    # Percentage change is not meaningful around a zero baseline.
    if expected == 0:
        return result

    if direction == "higher":
        change_pct = ((observed - expected) / abs(expected)) * 100
    else:
        change_pct = ((expected - observed) / abs(expected)) * 100

    result["regression_change_pct"] = round(change_pct, 2)

    if change_pct >= REGRESSION_MIN_CHANGE_PCT:
        result["regression_detected"] = True
        result["regression_reason"] = (
            f"Sustained deterioration: recent 7-day median is "
            f"{change_pct:.1f}% worse than the previous 7-day median."
        )

    return result

def detect_degradation(measurements: pd.DataFrame) -> pd.DataFrame:
    """Score the latest observation for each site and monitored metric."""
    columns = [
        "site_id", "site_name", "measured_at", "metric",
        "observed", "expected", "robust_score",
        "severity", "reason", "model_status",
        "baseline_samples", "baseline_readiness",
        "seasonality_status",
        "regression_detected",
        "regression_change_pct",
        "regression_reason",
    ]

    if measurements.empty:
        return pd.DataFrame(columns=columns)

    required = {
        "site_id", "measured_at", *METRICS.keys()
    }
    if not required.issubset(measurements.columns):
        return pd.DataFrame(columns=columns)

    df = measurements.copy()
    df["measured_at"] = pd.to_datetime(
        df["measured_at"], errors="coerce"
    )
    df = df.dropna(subset=["site_id", "measured_at"])
    df = df.sort_values(["site_id", "measured_at"])

    if df.empty:
        return pd.DataFrame(columns=columns)

    if "site_name" not in df.columns:
        df["site_name"] = df["site_id"].astype(str)
    else:
        df["site_name"] = (
            df["site_name"]
            .fillna(df["site_id"].astype(str))
            .replace("", df["site_id"].astype(str))
        )

    results = []

    for site_id, site_df in df.groupby("site_id", sort=False):
        site_df = site_df.sort_values("measured_at")

        # Assess the latest reading for each site and metric.
        latest = site_df.iloc[-1]
        regression_results = {}
        for metric, config in METRICS.items():
            regression_results[metric] = detect_slow_regression(
                site_df,
                metric,
                config["direction"],
            )

        for metric, config in METRICS.items():
            observed = pd.to_numeric(
                pd.Series([latest[metric]]), errors="coerce"
            ).iloc[0]

            if pd.isna(observed):
                continue

            # Exclude the latest observation from its own baseline.
            history = site_df.iloc[:-1].copy()
            history = history.dropna(subset=[metric])

            # Compare observations from the same hour of day.
            same_hour = history[
                history["measured_at"].dt.hour
                == latest["measured_at"].hour
            ]
            baseline = pd.to_numeric(
                same_hour[metric], errors="coerce"
            ).dropna()

            expected = None
            score = None
            severity = "INFO"
            reason = "Insufficient comparable historical data."
            model_status = "WARMING_UP"
            baseline_samples = len(baseline)
            baseline_readiness = "INSUFFICIENT_HISTORY"
            seasonality_status = "SAME_HOUR_ONLY"
            regression = regression_results[metric]

            if len(baseline) >= MIN_BASELINE_SAMPLES:
                expected = float(baseline.median())
                mad = float((baseline - expected).abs().median())

                if mad > 0:
                    score = (
                        0.6745 * (float(observed) - expected) / mad
                    )
                elif float(observed) == expected:
                    score = 0.0
                else:
                    # Zero historical variation: flag the change,
                    # but do not claim a calibrated anomaly score.
                    score = None

                model_status = "READY"
                baseline_readiness = "MINIMUM_HISTORY_READY"

                if config["direction"] == "higher":
                    deviation = float(observed) - expected
                    directional_score = score
                else:
                    deviation = expected - float(observed)
                    directional_score = (
                        -score if score is not None else None
                    )

                if mad > 0 and directional_score is not None:
                    if (
                        deviation > 0
                        and directional_score >= ANOMALY_SCORE_THRESHOLD
                    ):
                        severity = "WARNING"
                        reason = (
                            "Reading is unusually degraded relative "
                            "to the same-hour site baseline."
                        )
                    else:
                        reason = "No significant robust deviation."
                elif mad == 0 and deviation > 0:
                    severity = "WARNING"
                    reason = (
                        "Reading differs from a zero-variation "
                        "baseline; anomaly score is uncalibrated."
                    )
                else:
                    reason = "No significant robust deviation."

            if regression["regression_detected"]:
                if severity == "INFO":
                    severity = "WARNING"
                reason = regression["regression_reason"]

            # Existing static limits remain independent guardrails.
            if config["direction"] == "higher":
                if observed > config["static_critical"]:
                    severity = "CRITICAL"
                    reason = "Existing critical threshold exceeded."
                elif observed > config["static_warning"] and severity != "CRITICAL":
                    if severity == "INFO":
                        severity = "WARNING"
                    reason = "Existing warning threshold exceeded."
            else:
                if observed < config["static_critical"]:
                    severity = "CRITICAL"
                    reason = "Existing critical threshold breached."
                elif observed < config["static_warning"] and severity != "CRITICAL":
                    if severity == "INFO":
                        severity = "WARNING"
                    reason = "Existing warning threshold breached."

            results.append({
                "site_id": site_id,
                "site_name": latest["site_name"],
                "measured_at": latest["measured_at"],
                "metric": config["label"],
                "observed": float(observed),
                "expected": expected,
                "robust_score": score,
                "severity": severity,
                "reason": reason,
                "model_status": model_status,
                "baseline_samples": baseline_samples,
                "baseline_readiness": baseline_readiness,
                "seasonality_status": seasonality_status,
                "regression_detected": regression["regression_detected"],
                "regression_change_pct": regression["regression_change_pct"],
                "regression_reason": regression["regression_reason"],
            })

    result = pd.DataFrame(results, columns=columns)

    severity_order = {
        "CRITICAL": 0, "WARNING": 1, "INFO": 2
    }
    if not result.empty:
        result["_order"] = result["severity"].map(severity_order)
        result = result.sort_values(
            ["_order", "site_id", "metric"]
        ).drop(columns="_order")

    return result.reset_index(drop=True)
