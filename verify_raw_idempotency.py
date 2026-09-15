import logging
from src.ingestion.raw_loader import load_raw_measurements

# Set up clean logging context output
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def execute_idempotency_audit():
    # 🔑 Uses run_id 1 since we just reset your background database container
    active_run_id = 1
    target_file = "script_automated_test"

    print("\n--- STARTING RAW INGESTION IDEMPOTENCY FIREWALL AUDIT ---")
    
    # 🚀 Pass 1: Run the initial ingestion sweep
    count1 = load_raw_measurements(ingestion_run_id=active_run_id, source_file=target_file)
    print(f"Pass 1 — Rows written to raw data lake: {count1}")

    # 🔒 Pass 2: Re-ingest the exact same data payload to test conflict protection
    count2 = load_raw_measurements(ingestion_run_id=active_run_id, source_file=target_file)
    print(f"Pass 2 — Duplicate rows written to raw data lake: {count2}")
    
    print("--- AUDIT COMPLETE ---\n")

if __name__ == "__main__":
    execute_idempotency_audit()
