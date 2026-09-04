from dataclasses import dataclass


@dataclass
class PipelineMetrics:
    """
    Unified object model representing the operational, volume, and balancing metrics
    for a single end-to-end data pipeline execution run.
    """
    records_read: int = 0
    records_inserted: int = 0
    records_rejected: int = 0
    records_skipped: int = 0

    @property
    def records_processed(self) -> int:
        """
        Calculates active system modifications. Represents the total number 
        of records that caused a database transaction write or quarantine load.
        """
        return self.records_inserted + self.records_rejected

    def summary(self) -> dict:
        """
        Serializes current structural performance metrics into a clean dictionary map.
        """
        return {
            "records_read": self.records_read,
            "records_inserted": self.records_inserted,
            "records_rejected": self.records_rejected,
            "records_skipped": self.records_skipped,
            "records_processed": self.records_processed,
        }
