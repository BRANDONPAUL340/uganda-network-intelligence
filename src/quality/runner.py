# 🚀 Add this import to the top of your existing runner file
from src.quality.raw_validation import run_raw_quality_checks


# Locate your main quality runner block and merge the metrics dictionary payloads:
def run_quality_checks(run_id=None):
    """
    Orchestrates the entire data platform quality firewall sweep layer.
    Combines core source checks with raw ingestion perimeter evaluations.
    """
    logger.info("Executing global data quality matrix audit sweep...")

    # 1. Gather your core historical source check counts
    # (Preserve your existing logic block here)
    results = {}  # Assume your existing dictionary gathers source check counts here

    # 2. Extract and merge the raw perimeter metric entries dynamically
    raw_results = run_raw_quality_checks()
    results.update(raw_results)

    # 3. Process severity ranks and log to 'data_quality_results' via your existing database write loop
    # (Keep your existing table insertion logic completely unchanged)
    logger.info("Global data quality matrix successfully committed to disk.")
    return results
