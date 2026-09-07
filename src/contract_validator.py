import json
from pathlib import Path
from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize tracking layer logger instance
logger = get_logger(__name__)

# Resolve absolute workspace directory tree path contexts safely
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "contracts"


def load_contract(dataset_name):
    """
    Locates and deserialises a targeted JSON data contract specification blueprint.
    """
    contract_path = CONTRACTS_DIR / f"{dataset_name}.json"

    if not contract_path.exists():
        raise FileNotFoundError(
            f"Contract definition metadata artifact not found: {contract_path}"
        )

    with contract_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_columns(dataset_name, actual_columns):
    """
    Validates an array list of target columns against the data contract blueprint.
    Raises ValueError immediately if the schema is missing any required field attributes.
    """
    contract = load_contract(dataset_name)

    required_columns = set(contract["required_columns"])
    actual_columns = set(actual_columns)

    # Compute a set difference evaluation to capture missing field gaps
    missing_columns = required_columns - actual_columns

    if missing_columns:
        raise ValueError(
            f"{dataset_name} schema model contract violation! Missing required "
            f"structural target columns: {sorted(missing_columns)}"
        )

    return True


def get_database_columns(table_name):
    """
    Queries the database system catalogs directly to retrieve an ordered list 
    of all active columns matching the target physical table on disk.
    """
    sql = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = :table_name
    ORDER BY ordinal_position;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {"table_name": table_name}
        )
        # Safely extract positional values from row objects mapping to index 0
        return [row[0] for row in result]


def validate_database_table(dataset_name, table_name=None):
    """
    Pulls live schemas from your warehouse deployment on disk and evaluates them 
    against your declarative semantic contracts.
    """
    if table_name is None:
        table_name = dataset_name

    actual_columns = get_database_columns(table_name)
    logger.info(f"Inspecting database table schema | table={table_name} | actual_columns={actual_columns}")
    
    return validate_columns(dataset_name, actual_columns)
def validate_measurement_values():
    """
    Queries rows inside your measurements data layer dynamically to detect 
    any values that violate structural contract boundary constraints.
    
    Returns:
        dict: A boolean scorecard map indicating whether each check contains zero violations.
    """
    checks = {
        "traffic_mb_non_negative": "traffic_mb < 0",
        "latency_ms_non_negative": "latency_ms < 0",
        "packet_loss_pct_range": "packet_loss_pct < 0 OR packet_loss_pct > 100",
        "availability_pct_range": "availability_pct < 0 OR availability_pct > 100",
    }

    results = {}

    with engine.begin() as connection:
        for check_name, condition in checks.items():
            sql = f"""
            SELECT COUNT(*)
            FROM measurements
            WHERE {condition};
            """
            failed = connection.execute(text(sql)).scalar()
            
            # The contract passes (True) only if the violation count is exactly 0
            results[check_name] = (failed == 0)

    return results
