from dataclasses import dataclass
from time import perf_counter


@dataclass
class QueryMetric:
    query_name: str
    duration_seconds: float
    rows_returned: int


def measure_query(query_name: str, query_function) -> tuple[object, QueryMetric]:
    """
    High-Resolution Telemetry Wrapper: Captures precise stop-watch timings 
    and output record sizes across database execution threads [INDEX].
    """
    start = perf_counter()

    result = query_function()

    duration = perf_counter() - start
    rows = len(result) if hasattr(result, "__len__") else 0

    metric = QueryMetric(
        query_name=query_name,
        duration_seconds=round(duration, 4),
        rows_returned=rows,
    )

    return result, metric
