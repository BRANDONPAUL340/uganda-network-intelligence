import pandas as pd


REQUIRED_COLUMNS = [
    "site_name",
    "district",
    "equipment_type",
    "manufacturer",
    "model",
    "incident_type",
    "severity",
    "start_time",
    "end_time",
    "status",
    "description",
]


def validate_incidents(df):

    errors = []

    # Check required columns
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            errors.append(f"Missing column: {column}")

    if errors:
        return errors

    # Check missing values
    for column in REQUIRED_COLUMNS:
        if df[column].isnull().any():
            errors.append(
                f"Missing values found in: {column}"
            )

    # Validate timestamps
    start_times = pd.to_datetime(
        df["start_time"],
        errors="coerce"
    )

    end_times = pd.to_datetime(
        df["end_time"],
        errors="coerce"
    )

    if start_times.isnull().any():
        errors.append("Invalid start_time found")

    if end_times.isnull().any():
        errors.append("Invalid end_time found")

    # End must be after start
    if not start_times.isnull().any() and not end_times.isnull().any():

        invalid_duration = end_times <= start_times

        if invalid_duration.any():
            errors.append(
                "Incident end_time must be after start_time"
            )

    # Validate severity
    allowed_severities = {
        "Low",
        "Medium",
        "High",
        "Critical",
    }

    invalid_severities = (
        set(df["severity"]) - allowed_severities
    )

    if invalid_severities:
        errors.append(
            f"Invalid severity found: {invalid_severities}"
        )

    # Validate status
    allowed_statuses = {
        "Open",
        "Investigating",
        "Resolved",
        "Closed",
    }

    invalid_statuses = (
        set(df["status"]) - allowed_statuses
    )

    if invalid_statuses:
        errors.append(
            f"Invalid incident status found: {invalid_statuses}"
        )

    # Check duplicate incidents
    duplicate_columns = [
        "site_name",
        "district",
        "equipment_type",
        "manufacturer",
        "model",
        "incident_type",
        "start_time",
    ]

    if df.duplicated(
        subset=duplicate_columns
    ).any():

        errors.append(
            "Duplicate incident records found"
        )

    return errors
