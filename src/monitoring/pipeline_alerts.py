from src.monitoring.alerts import Alert


def check_pipeline_status(status: str) -> Alert | None:
    """
    Pipeline State Evaluator: Catches transformation drop-offs or unhandled exceptions 
    and instantly upgrades them to a high-priority operational state [INDEX].
    """
    if status in {"FAILED", "ERROR", "CRITICAL"}:
        return Alert(
            name="pipeline_failure",
            severity="SEV2",
            message=f"Pipeline status is {status} — Investigation required.",
        )

    return None
