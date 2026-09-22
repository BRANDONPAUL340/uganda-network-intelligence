from src.monitoring.alerts import Alert


def check_watermark(current_watermark, previous_watermark) -> Alert | None:
    """
    Watermark Regression Guard: Protects your data lakehouse platform from processing 
    duplicate files or moving backward across historical rows [INDEX].
    """
    if current_watermark < previous_watermark:
        return Alert(
            name="watermark_regression",
            severity="SEV2",
            message=(
                f"Watermark moved backwards from "
                f"{previous_watermark} to {current_watermark}"
            ),
        )

    return None
