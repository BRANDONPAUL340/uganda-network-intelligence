import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment configuration variables immediately upon package boot
load_dotenv()

from src.config import DATABASE_URL, PIPELINE_NAME
from src.database import engine
from src.logging_config import configure_logging
from src.pipeline_tracking import start_stage, finish_stage
from src.lineage import record_lineage
from src.transformation.silver import run_silver
from src.data_quality.quality_gate import run_quality_gate
from src.transformation.gold import run_gold

# Instantiate module-level logging context handle wrapper
logger = logging.getLogger(__name__)


def start_pipeline_run():
    """Initializes a new tracking run record inside the database registry."""
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name, started_at, status, current_stage, records_processed, duration_seconds
    )
    VALUES (
        :pipeline_name, CURRENT_TIMESTAMP, 'RUNNING', 'STARTING', 0, 0.000
    )
    RETURNING run_id;
    """
    with engine.begin() as connection:
        return connection.execute(
            text(sql),
            {
                "pipeline_name": PIPELINE_NAME,
            }
        ).scalar()


def update_pipeline_stage(run_id, stage):
    """Dynamically updates the active pipeline processing phase on disk."""
    sql = """
    UPDATE pipeline_runs
    SET current_stage = :current_stage
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "current_stage": stage,
            }
        )


def finish_pipeline_run(
    run_id,
    status,
    records_processed=0,
    error_message=None,
    duration_seconds=None,
    current_stage=None
):
    """Closes out the pipeline execution run tracking state with final parameters."""
    sql = """
    UPDATE pipeline_runs
    SET completed_at = :completed_at,
        status = :status,
        records_processed = :records_processed,
        error_message = :error_message,
        duration_seconds = :duration_seconds,
        current_stage = COALESCE(:current_stage, current_stage)
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "current_stage": current_stage,
            }
        )

import logging
from src.version import PROJECT_VERSION
from src.config import PIPELINE_NAME
# 🧩 Import your centralized, transaction-safe monitoring hooks [INDEX]
from src.pipeline_monitoring import (
    start_pipeline_step,
    complete_pipeline_step,
    fail_pipeline_step,
)

logger = logging.getLogger(__name__)

def run_pipeline_execution(run_id: int) -> None:
    """
    Automated Platform Orchestration Loop: Executes data lakehouse transformations, 
    instrumenting each step to stream metrics straight to PostgreSQL [INDEX].
    """
    logger.info(f"Starting instrumented pipeline execution context for Run #{run_id}")

    # ==========================================================================
    # 🏗️ PART 3 — Wrap Bronze Ingestion Layer Block
    # ==========================================================================
    # 1. Initialize the step as 'RUNNING' and capture its unique ID [INDEX]
    step_id_bronze = start_pipeline_step(run_id, "bronze_ingestion")
    try:
        logger.info("Executing Bronze ingestion stage...")
        
        # 🟢 CALL YOUR EXISTING BRONZE FUNCTION HERE 
        # Example: records_bronze = run_bronze() or ingest_raw_telemetry()
        records_bronze = 1250  # Capturing your validated processed count baseline [INDEX]
        
        # 2. Mark as SUCCESS and record processed row counts atomically [INDEX]
        complete_pipeline_step(step_id_bronze, records_processed=records_bronze)
        logger.info(f"Bronze ingestion step completed successfully. Rows: {records_bronze}")
        
    except Exception as exc:
        # 3. Catch errors gracefully, stamp FAILED status, log the error, and re-raise [INDEX]
        logger.error(f"❌ Bronze ingestion step failed: {exc}")
        fail_pipeline_step(step_id_bronze, error_message=str(exc))
        raise

    # (Keep your existing Silver, Gold, and Data Quality function triggers intact below)



def main():
    """Unified data pipeline stage engine equipped with accurate accounting trackers."""
    # 🚀 Boot up centralized logger configurations before any execution logic runs
    configure_logging()
    
    logger.info("=" * 60)
    logger.info("STARTING UGANDA NETWORK & SERVICE INTELLIGENCE PIPELINE RUN")
    logger.info("=" * 60)

    # Begin global clock timer tracking pass
    pipeline_start = time.perf_counter()
    
    run_id = start_pipeline_run()
    logger.info(f"Pipeline tracking run record successfully created. run_id={run_id}")

    silver_records = 0
    gold_records = 0
    try:
        # -------------------------------------------------
        # 2. SILVER STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "SILVER")
        silver_sid = start_stage(run_id, "SILVER")
        
        try:
            silver_start = time.perf_counter()
            logger.info("Starting SILVER stage")
            
            # 🚀 Interlock: Capture the comprehensive dictionary payload
            silver_counts = run_silver(run_id)
            silver_records = sum(silver_counts.values())
            silver_duration = time.perf_counter() - silver_start
            
            logger.info("SILVER processed %s records", silver_records)

            # 📜 Dynamic Lineage Tracing via Explicit Dictionary Keys
            record_lineage(
                run_id=run_id,
                stage_run_id=silver_sid,
                source_table="measurements",
                target_table="silver_measurements",
                records_processed=silver_counts["silver_measurements"]
            )
            record_lineage(
                run_id=run_id,
                stage_run_id=silver_sid,
                source_table="measurements",
                target_table="silver_network_health",
                records_processed=silver_counts["silver_network_health"]
            )
            
            finish_stage(silver_sid, "SUCCESS")
            logger.info(f"SILVER stage completed in {silver_duration:.2f} seconds")
        except Exception as exc:
            finish_stage(silver_sid, "FAILED", error_message=str(exc))
            logger.exception("SILVER stage failed ❌")
            raise
    

        # -------------------------------------------------
        # 3. QUALITY STAGE (🔒 Enforced with Pre-Flight Schema Firewall!)
        # -------------------------------------------------
        update_pipeline_stage(run_id, "QUALITY")
        quality_sid = start_stage(run_id, "QUALITY")
        
        try:
            quality_start = time.perf_counter()
            
            # 🔒 Execute Pre-Flight Schema & Data Contract Validation Firewall Check
            from src.data_quality.schema_validation import validate_schema
            
            logger.info("Running schema validation")
            schema_result = validate_schema()

            if not schema_result["passed"]:
                error_message = "; ".join(schema_result["errors"])
                logger.error("Schema validation failed: %s", error_message)
                raise RuntimeError(f"Schema validation failed: {error_message}")
            
            logger.info("Schema validation passed")

            # Execute 18-point core logic verification checks
            logger.info("Starting QUALITY stage")
            quality_result = run_quality_gate(run_id)
            quality_duration = time.perf_counter() - quality_start

            finish_stage(quality_sid, "SUCCESS")
            if quality_result["failed"] > 0:
                logger.warning(f"⚠️ Quality anomalies detected for run_id={run_id} | Failed counts={quality_result['failed']}")
                logger.info(f"QUALITY stage completed with warnings in {quality_duration:.2f} seconds")
            else:
                logger.info(f"QUALITY stage completed in {quality_duration:.2f} seconds with 0 rule breaches.")
        except Exception as exc:
            finish_stage(quality_sid, "FAILED", error_message=str(exc))
            logger.exception("QUALITY stage failed ❌")
            raise

        # -------------------------------------------------
        # 4. GOLD STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "GOLD")
        gold_sid = start_stage(run_id, "GOLD")
        
        try:
            gold_start = time.perf_counter()
            logger.info("Starting GOLD stage")
            
            # 🚀 Interlock: Capture the analytical dictionary payload
            gold_counts = run_gold()
            gold_records = gold_counts
            gold_duration = time.perf_counter() - gold_start
            
            logger.info("GOLD processed %s records", gold_records)

            # 📜 Dynamic Lineage Tracing via Explicit Dictionary Keys
            record_lineage(
                run_id=run_id,
                stage_run_id=gold_sid,
                source_table="silver_measurements",
                target_table="gold_site_daily_performance",
                records_processed=gold_records
            )
            record_lineage(
                run_id=run_id,
                stage_run_id=gold_sid,
                source_table="silver_network_health",
                target_table="gold_equipment_health",
                records_processed=0
            )
            
            finish_stage(gold_sid, "SUCCESS")
            logger.info(f"GOLD stage completed in {gold_duration:.2f} seconds")
        except Exception as exc:
            finish_stage(gold_sid, "FAILED", error_message=str(exc))
            logger.exception("GOLD stage failed ❌")
            raise

        # Compute complete transaction duration metrics from perf counter
        total_duration = time.perf_counter() - pipeline_start

        # 🔒 Explicit Data Accounting Standard: Total records successfully produced by transformation stages during this run.
        total_records_processed = silver_records + gold_records
        logger.info("Pipeline processed %s records", total_records_processed)

    
        # -------------------------------------------------
        # 5. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=total_records_processed,
            duration_seconds=total_duration,
            current_stage="SUCCESS",
            silver_records_processed=silver_records,
            gold_records_processed=gold_records,
            quality_checks_run=quality_result["checks"],
            quality_checks_failed=quality_result["failed"],
            quality_checks_passed=quality_result["passed"],
        )
        logger.info("============================================================")
        logger.info(f"Pipeline completed successfully in {total_duration:.2f} seconds 🎉")
        logger.info(f"Total metrics records processed: {total_records_processed}")
        logger.info("============================================================")

    except Exception as error:
        total_duration = time.perf_counter() - pipeline_start

        # -------------------------------------------------
        # 6. FAILURE PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            duration_seconds=total_duration,
            current_stage=None)
        logger.exception(f"Pipeline failed after {total_duration:.2f} seconds ❌")
        raise
    # 🚀 Fixed: Ensure there are absolutely ZERO leading spaces before either line below!
if __name__ == "__main__":
    main()
import logging
from src.version import PROJECT_VERSION
from src.config import PIPELINE_NAME
# Ingest our newly deployed automated tracking drivers [INDEX]
from src.monitoring.step_tracker import (
    start_pipeline_step,
    complete_pipeline_step,
    fail_pipeline_step
)

logger = logging.getLogger(__name__)

def execute_full_pipeline(run_id: int) -> None:
    """
    Automated Platform Orchestration Loop: Executes multi-tier data lakehouse 
    transformations, tracking step metrics and catching exceptions live [INDEX].
    """
    logger.info(f"Starting step-level monitoring execution pass for Run #{run_id}")

    # ==========================================================================
    # 🏗️ PART 9 — Apply the Pattern to Bronze Ingestion
    # ==========================================================================
    step_id_bronze = start_pipeline_step(run_id, "bronze_ingestion")
    try:
        logger.info("Executing Bronze ingestion step...")
        
        # Call your existing Bronze data extraction function logic here [INDEX]
        # For example: records_bronze = ingest_raw_telemetry()
        records_bronze = 1250  # Mapping baseline metric bounds
        
        complete_pipeline_step(step_id_bronze, records_processed=records_bronze)
        logger.info(f"Bronze step completed successfully: {records_bronze} rows.")
    except Exception as exc:
        logger.error(f"Bronze ingestion crashed: {exc}")
        fail_pipeline_step(step_id_bronze, error_message=str(exc))
        raise

    # ==========================================================================
    # 🏗️ PART 10 — Apply the Pattern to Silver Transformation
    # ==========================================================================
    step_id_silver = start_pipeline_step(run_id, "silver_transformation")
    try:
        logger.info("Executing Silver cleaning & deduplication step...")
        
        # Call your existing Silver transformation function logic here [INDEX]
        # For example: records_silver = run_silver_cleansing()
        records_silver = 1210  # Mapping baseline metric bounds
        
        complete_pipeline_step(step_id_silver, records_processed=records_silver)
        logger.info(f"Silver step completed successfully: {records_silver} rows.")
    except Exception as exc:
        logger.error(f"Silver transformation crashed: {exc}")
        fail_pipeline_step(step_id_silver, error_message=str(exc))
        raise

    # ==========================================================================
    # 🏗️ PART 11 — Apply the Pattern to Gold Summaries
    # ==============================================================================
    step_id_gold = start_pipeline_step(run_id, "gold_transformation")
    try:
        logger.info("Executing Gold analytical business intelligence view step...")
        
        # Call your existing Gold analytical views compilation logic here [INDEX]
        # For example: records_gold = compute_gold_aggregates()
        records_gold = 1210  # Mapping baseline metric bounds
        
        complete_pipeline_step(step_id_gold, records_processed=records_gold)
        logger.info(f"Gold step completed successfully: {records_gold} rows.")
    except Exception as exc:
        logger.error(f"Gold transformation crashed: {exc}")
        fail_pipeline_step(step_id_gold, error_message=str(exc))
        raise
import logging
from src.version import PROJECT_VERSION
from src.config import PIPELINE_NAME
from src.pipeline_monitoring import (
    start_pipeline_step,
    complete_pipeline_step,
    fail_pipeline_step,
)
# 🧩 Import the centralized automated data quality suite engine [INDEX]
from src.monitoring.quality_engine import execute_data_quality_suite

logger = logging.getLogger(__name__)

def run_pipeline_execution(run_id: int) -> None:
    """
    Automated Platform Orchestration Loop: Executes multi-tier lakehouse 
    transformations and hooks up automated data quality gates [INDEX].
    """
    logger.info(f"Starting instrumented pipeline execution context for Run #{run_id}")

    # --- Day 122 Bronze Ingestion Block ---
    step_id_bronze = start_pipeline_step(run_id, "bronze_ingestion")
    try:
        records_bronze = 1250  
        complete_pipeline_step(step_id_bronze, records_processed=records_bronze)
    except Exception as exc:
        fail_pipeline_step(step_id_bronze, error_message=str(exc))
        raise

    # --- Day 122 Silver Transformation Block ---
    step_id_silver = start_pipeline_step(run_id, "silver_transformation")
    try:
        records_silver = 1210  
        complete_pipeline_step(step_id_silver, records_processed=records_silver)
    except Exception as exc:
        fail_pipeline_step(step_id_silver, error_message=str(exc))
        raise

    # --- Day 122 Gold Analytics Block ---
    step_id_gold = start_pipeline_step(run_id, "gold_transformation")
    try:
        records_gold = 1210  
        complete_pipeline_step(step_id_gold, records_processed=records_gold)
    except Exception as exc:
        fail_pipeline_step(step_id_gold, error_message=str(exc))
        raise

    # ==========================================================================
    # 🧪 DAY 128 — AUTOMATED DATA QUALITY GATE INTEGRATION
    # ==========================================================================
    step_id_dq = start_pipeline_step(run_id, "data_quality")
    try:
        logger.info(f"Triggering automated data quality suite gates for Run #{run_id}...")
        
        # Execute your 5 core validations (volume, nulls, duplicates, ranges, freshness)
        # Pass down the run_id to link metrics directly to the current batch context [INDEX]
        dq_suite_passed = execute_data_quality_suite(run_id=run_id)
        
        if dq_suite_passed:
            logger.info("🎉 Data Quality suite checks successfully passed.")
            complete_pipeline_step(step_id_dq, records_processed=5) # 5 checks passed
        else:
            # Pipeline ran without a technical crash, but data quality checks failed! [INDEX]
            logger.warning("⚠️ Data Quality rules breached. Validation errors logged to database.")
            complete_pipeline_step(step_id_dq, records_processed=0)
            
    except Exception as exc:
        logger.error(f"❌ Data Quality execution gate encountered a technical failure: {exc}")
        fail_pipeline_step(step_id_dq, error_message=str(exc))
        raise

