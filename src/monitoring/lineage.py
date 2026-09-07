from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize tracking layer utility logger instance
logger = get_logger(__name__)


def record_lineage(
    run_id,
    source_layer,
    source_table,
    target_layer,
    target_table,
    transformation_name,
    records_processed=0,
):
    """
    Inserts a row into the data_lineage table, recording an auditable 
    and deterministic relationship contract between a source asset and target asset.
    """
    sql = """
    INSERT INTO data_lineage (
        run_id,
        source_layer,
        source_table,
        target_layer,
        target_table,
        transformation_name,
        records_processed
    )
    VALUES (
        :run_id,
        :source_layer,
        :source_table,
        :target_layer,
        :target_table,
        :transformation_name,
        :records_processed
    );
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "source_layer": source_layer,
                "source_table": source_table,
                "target_layer": target_layer,
                "target_table": target_table,
                "transformation_name": transformation_name,
                "records_processed": records_processed,
            },
        )
    logger.info(
        f"Data lineage logged | run_id={run_id} | "
        f"{source_table} ──► {target_table} ({transformation_name})"
    )
