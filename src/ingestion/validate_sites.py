import pandas as pd

# Define our strict data engineering standards
ALLOWED_SITE_TYPES = {'Macro Tower', 'Micro Cell', 'Rooftop Hub', 'Data Center'}

def validate_sites(df: pd.DataFrame) -> list:
    """
    Validates site rows and captures any compliance failures.
    Returns a list of descriptive error messages.
    """
    errors = []

    # 1. Structure Check: Verify all required columns are present
    required_columns = ['site_name', 'region', 'district', 'latitude', 'longitude', 'site_type', 'status']
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required structure column: {col}")
            return errors 

    # 2. Check for Missing Rows (Nulls)
    if df['site_name'].isnull().any():
        errors.append("Found empty values (NULLs) in the 'site_name' column.")

    # 3. GPS Range Coordinates Check
    if not df['latitude'].between(-2.0, 5.0).all():
        errors.append("Latitude anomaly detected: Coordinates sit outside Uganda boundaries.")
        
    if not df['longitude'].between(29.0, 36.0).all():
        errors.append("Longitude anomaly detected: Coordinates sit outside Uganda boundaries.")

    # 4. Strict Column Type Validation (The New Rule!)
    # Find rows where the CSV site_type does not match our allowed business choices
    invalid_types = df[~df['site_type'].isin(ALLOWED_SITE_TYPES)]['site_type'].unique()
    
    if len(invalid_types) > 0:
        errors.append(f"Invalid site_type values found in CSV: {list(invalid_types)}. "
                      f"Must be one of: {list(ALLOWED_SITE_TYPES)}")

    return errors
