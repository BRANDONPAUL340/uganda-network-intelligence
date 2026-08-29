import pandas as pd


REQUIRED_COLUMNS = [
    "site_name",
    "district",
    "equipment_type",
    "manufacturer",
    "model",
    "measured_at",
    "traffic_mb",
    "latency_ms",
    "packet_loss_pct",
    "signal_strength_dbm",
    "availability_pct",
]


def validate_measurements(df):

    errors = []

    # Required columns
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            errors.append(f"Missing column: {column}")

    if errors:
        return errors

    # Missing values
    for column in REQUIRED_COLUMNS:
        if df[column].isnull().any():
            errors.append(f"Missing values found in: {column}")

    # Timestamp validation
    timestamps = pd.to_datetime(
        df["measured_at"],
        errors="coerce"
    )

    if timestamps.isnull().any():
        errors.append("Invalid measurement timestamp found")

    # Numeric validation
    numeric_columns = [
        "traffic_mb",
        "latency_ms",
        "packet_loss_pct",
        "signal_strength_dbm",
        "availability_pct",
    ]

    for column in numeric_columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if values.isnull().any():
            errors.append(
                f"Invalid numeric value found in: {column}"
            )

    # Percentage validation
    if (
        (df["packet_loss_pct"] < 0).any()
        or
        (df["packet_loss_pct"] > 100).any()
    ):
        errors.append("Packet loss must be between 0 and 100")

    if (
        (df["availability_pct"] < 0).any()
        or
        (df["availability_pct"] > 100).any()
    ):
        errors.append("Availability must be between 0 and 100")

    # Negative traffic / latency
    if (df["traffic_mb"] < 0).any():
        errors.append("Traffic cannot be negative")

    if (df["latency_ms"] < 0).any():
        errors.append("Latency cannot be negative")

    # Duplicate measurements
    duplicate_columns = [
        "site_name",
        "district",
        "equipment_type",
        "manufacturer",
        "model",
        "measured_at",
    ]

    if df.duplicated(subset=duplicate_columns).any():
        errors.append("Duplicate measurements found")

    return errors
