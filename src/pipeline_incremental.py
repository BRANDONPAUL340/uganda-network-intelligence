import logging
from src.config import PIPELINE_NAME
from src.ingestion.incremental import advance_processing_watermark
from src.transformation.raw_to_silver import promote_incremental_raw_to_silver
from src.transformation.gold import refresh_gold_from_silver_incremental
from src.transformation.gold_incremental import get_gold_watermark, update_gold_watermark

logger = logging.getLogger(__name__)


def run_incremental_silver():
    """
    Orchestrates the incremental Silver processing stage block.
    Promotes fresh raw rows above the watermark using an idempotent layout [INDEX].
    """
    logger.info("Starting incremental Silver processing stage pass...")
    result = promote_incremental_raw_to_silver()
    logger.info("Incremental Silver processing completed: %s records loaded", result)
    return result


def run_gold_incremental():
    """
    Orchestrates the incremental Gold processing stage block.
    Recalculates daily analytical metrics aggregates based on silver measurement_id boundaries [INDEX].
    """
    logger.info("Starting incremental Gold processing stage pass...")
    last_gold_watermark = get_gold_watermark()
    logger.info("Active GOLD processing watermark checkpoint located: last_id=%s", last_gold_watermark)
    
    result = refresh_gold_from_silver_incremental(last_gold_watermark)
    
    # 🔒 SAFE ADVANCEMENT: Update the GOLD watermark only after aggregate success
    update_gold_watermark()
    logger.info("GOLD stage watermark pointer successfully advanced on disk.")
    return result


def run_incremental_pipeline():
    """
    Master Orchestrator Sequence: Coordinates the multi-stage incremental execution loop [INDEX].
    Enforces atomic stage safety boundaries so that watermarks advance only upon success [INDEX].
    """
    logger.info(f"Starting incremental pipeline: {PIPELINE_NAME}")

    # 🥈 1. Process and promote RAW -> SILVER records
    silver_result = run_incremental_silver()

    # 🔒 2. SAFE ADVANCEMENT: Advance the SILVER watermark only after stage success
    silver_watermark = advance_processing_watermark(source_name="measurements")
    logger.info(f"Silver watermark advanced to {silver_watermark}")

    # 🥇 3. Recalculate aggregates and update SILVER -> GOLD summaries
    gold_result = run_gold_incremental()

    logger.info("Incremental pipeline completed successfully.")

    return {
        "silver": silver_result,
        "silver_watermark": silver_watermark,
        "gold": gold_result,
    }
# Public master pipeline entry point
run_pipeline_incremental = run_incremental_pipeline