from sqlalchemy import text
from src.database import engine


def record_lineage(
    run_id,
    stage_run_id,
    source_table,
    target_table,
    records_processed=0,
):
    """
    Inserts an un-fakeable audit record into the pipeline_lineage table,
    documenting exactly how data records migrated between layers.
    """
    query = text("""
        INSERT INTO pipeline_lineage (
            run_id,
            stage_run_id,
            source_table,
            target_table,
            records_processed
        )
        VALUES (
            :run_id,
            :stage_run_id,
            :source_table,
            :target_table,
            :records_processed
        );
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "stage_run_id": stage_run_id,
                "source_table": source_table,
                "target_table": target_table,
                "records_processed": records_processed,
            },
        )
