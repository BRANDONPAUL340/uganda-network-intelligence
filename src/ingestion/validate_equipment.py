import pandas as pd


REQUIRED_COLUMNS = [
    "site_name",
    "district",
    "equipment_type",
    "manufacturer",
    "model",
    "installation_date",
    "status",
]


def validate_equipment(df):

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
            errors.append(f"Missing values found in: {column}")

    # Check duplicate equipment records
    duplicate_columns = [
        "site_name",
        "district",
        "equipment_type",
        "manufacturer",
        "model",
    ]

    if df.duplicated(subset=duplicate_columns).any():
        errors.append("Duplicate equipment records found")

    # Validate installation dates
    dates = pd.to_datetime(
        df["installation_date"],
        errors="coerce"
    )

    if dates.isnull().any():
        errors.append("Invalid installation date found")

    # Validate equipment status
    allowed_statuses = {
        "Active",
        "Maintenance",
        "Inactive",
    }

    invalid_statuses = set(df["status"]) - allowed_statuses

    if invalid_statuses:
        errors.append(
            f"Invalid equipment status found: {invalid_statuses}"
        )

    return errors
