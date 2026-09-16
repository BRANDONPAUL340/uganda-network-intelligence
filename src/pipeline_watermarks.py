import logging
from src.config import PIPELINE_NAME
from src.ingestion.watermark import update_watermark

logger = logging.getLogger(__name__)


def advance_stage_watermark(stage_name, source_name, measurement_id):
    """
    Unified Orchestration Interface: Provides a standardized, single point of entry
    to advance durable checkpoint watermarks for any active processing layer [INDEX].
    """
    logger.info(f"Unified Interface Request: Advancing stage=[{stage_name}] source=[{source_name}] to checkpoint={measurement_id}")
    
    update_watermark(
        PIPELINE_NAME,
        stage_name,
        source_name,
        measurement_id,
    )
    
    logger.info(f"Durable state checkpoint for {stage_name} safely committed via unified interface.")
