
"""Explainable, rule-based root cause analysis for pipeline and network incidents.

This module is read-only: it does not access the database, modify incidents,
or change network-degradation risk scores.
"""

from typing import Any


def _result(
    category: str,
    summary: str,
    likely_cause: str,
    evidence: list[str],
    recommended_actions: list[str],
    confidence: str,
    matched_rule: str,
) -> dict[str, Any]:
    """Return a consistent diagnosis structure."""
    return {
        "category": category,
        "summary": summary,
        "likely_cause": likely_cause,
        "evidence": evidence or ["No specific supporting evidence was available."],
        "recommended_actions": recommended_actions,
        "confidence": confidence,
        "matched_rule": matched_rule,
    }


def analyze_pipeline_failure(
    stage_name: str | None = None,
    error_message: str | None = None,
    run_status: str = "FAILED",
    records_rejected: int | None = None,
    records_skipped: int | None = None,
) -> dict[str, Any]:
    """Diagnose a pipeline failure using stored stage and error information."""
    stage = (stage_name or "Unknown stage").strip()
    message = (error_message or "").strip()
    text = message.lower()
    evidence = []

    if stage_name:
        evidence.append(f"Pipeline stage: {stage}")
    if message:
        evidence.append(f"Stored error: {message[:500]}")
    if records_rejected is not None:
        evidence.append(f"Rejected records: {records_rejected}")
    if records_skipped is not None:
        evidence.append(f"Skipped records: {records_skipped}")

    if not message and run_status.upper() not in {"FAILED", "ERROR"}:
        return _result(
            "pipeline",
            "The run does not have a confirmed failure in the supplied information.",
            "A failure could not be established from the available status.",
            evidence,
            ["Inspect the selected run's status and stage logs."],
            "Low",
            "insufficient_failure_evidence",
        )

    rules = [
        (
            ("connection refused", "could not connect", "connection timed out",
             "server closed the connection", "could not translate host name"),
            "Database connectivity failure",
            "The pipeline could not establish or maintain a database connection.",
            [
                "Verify that the database service is running and reachable.",
                "Check the database host, port, network access, and connection settings.",
                "Retry only after connectivity has been restored.",
            ],
            "database_connectivity",
        ),
        (
            ("password authentication failed", "authentication failed",
             "access denied", "permission denied"),
            "Database authentication or permissions failure",
            "The configured credentials or database permissions may be incorrect.",
            [
                "Verify the configured credentials without exposing secrets in logs.",
                "Check the database user's permissions for the affected operation.",
                "Confirm that the deployment is using the intended environment settings.",
            ],
            "database_authentication",
        ),
        (
            ("undefined column", "column does not exist", "does not exist",
             "relation does not exist", "no such table", "no such column"),
            "Database schema mismatch",
            "The query or application expects a table or column that the database cannot find.",
            [
                "Compare the failing query with the actual database schema.",
                "Check table and column names, migrations, and deployment versions.",
                "Verify that the application connects to the intended database.",
            ],
            "schema_mismatch",
        ),
        (
            ("not-null constraint", "foreign key constraint",
             "unique constraint", "check constraint", "integrityerror"),
            "Database constraint violation",
            "The data being written may violate a database integrity constraint.",
            [
                "Inspect the rejected record and the exact constraint named in the error.",
                "Validate required fields, references, and duplicate keys before insertion.",
                "Correct the source data or mapping before retrying.",
            ],
            "database_constraint",
        ),
        (
            ("validationerror", "validation error", "field required",
             "string_too_short", "input should be", "type mismatch",
             "invalid input syntax"),
            "Data validation or type mismatch",
            "A record or field may not satisfy the expected schema or data type.",
            [
                "Inspect the invalid field and the expected type or validation rule.",
                "Check empty values, required fields, and type conversions.",
                "Add validation before loading records into the next pipeline stage.",
            ],
            "data_validation",
        ),
        (
            ("timed out", "timeout", "readtimeout", "connecttimeout"),
            "Operation timed out",
            "A database, network, or external operation did not complete within its time limit.",
            [
                "Identify which operation timed out from the surrounding logs.",
                "Check service availability, network latency, and query duration.",
                "Retry cautiously after confirming that repeating the operation is safe.",
            ],
            "operation_timeout",
        ),
        (
            ("unicode decode error", "parsererror", "tokenizing data",
             "csv error", "invalid csv", "decode error"),
            "Input parsing or encoding failure",
            "An input file or payload may have an unexpected format or character encoding.",
            [
                "Inspect the source file around the failing record.",
                "Verify delimiters, headers, encoding, and column count.",
                "Validate the input format before processing the full batch.",
            ],
            "input_parsing",
        ),
    ]

    for markers, title, cause, actions, rule in rules:
        if any(marker in text for marker in markers):
            return _result(
                "pipeline",
                f"{title} detected in {stage}.",
                cause,
                evidence,
                actions,
                "High" if any(marker in text for marker in markers[:3]) else "Medium",
                rule,
            )

    if records_rejected is not None and records_rejected > 0:
        return _result(
            "pipeline",
            f"{records_rejected} record(s) were rejected in {stage}.",
            "One or more records failed validation or downstream acceptance rules.",
            evidence,
            [
                "Inspect rejected-record details and validation errors.",
                "Check required fields, data types, and source-to-target mappings.",
                "Confirm the corrected records pass validation before rerunning.",
            ],
            "Medium",
            "rejected_records",
        )

    if records_skipped is not None and records_skipped > 0:
        return _result(
            "pipeline",
            f"{records_skipped} record(s) were skipped in {stage}.",
            "Records may have been excluded by filtering, deduplication, or processing rules.",
            evidence,
            [
                "Check the stage's skip conditions and processing counters.",
                "Determine whether skipped records were expected or indicate a defect.",
            ],
            "Low",
            "skipped_records",
        )

    return _result(
        "pipeline",
        f"The cause of the failure in {stage} could not be identified confidently.",
        "The available error information does not match a known diagnostic rule.",
        evidence,
        [
            "Inspect the full traceback and the logs immediately before the failure.",
            "Check the failing stage's inputs, outputs, and database operations.",
            "Add a diagnostic rule once the underlying cause is confirmed.",
        ],
        "Low",
        "unknown_pipeline_error",
    )


def analyze_incident(
    incident_type: str | None,
    description: str | None,
    severity: str | None = None,
) -> dict[str, Any]:
    """Explain a network incident using its recorded type and description."""
    incident = (incident_type or "").strip()
    details = (description or "").strip()
    text = f"{incident} {details}".lower()
    evidence = []

    if incident:
        evidence.append(f"Incident type: {incident}")
    if details:
        evidence.append(f"Incident description: {details[:500]}")
    if severity:
        evidence.append(f"Recorded severity: {severity}")

    rules = [
        (
            ("packet loss", "packet_loss", "dropped packets"),
            "Packet loss",
            "Packets may be lost along the network path, affecting reliability.",
            [
                "Check packet-loss measurements over time.",
                "Investigate link errors, congestion, and network-device health.",
                "Compare the affected site with nearby sites and recent measurements.",
            ],
            "packet_loss",
        ),
        (
            ("latency", "high delay", "slow response", "response time"),
            "High network latency",
            "Network delay may be elevated due to congestion, routing, or link performance.",
            [
                "Compare recent latency with the site's historical baseline.",
                "Check link utilization, routing changes, and upstream service response times.",
                "Check whether packet loss and latency increased together.",
            ],
            "high_latency",
        ),
        (
            ("availability", "outage", "unreachable", "offline", "down"),
            "Availability or connectivity incident",
            "The site or service may be unreachable or experiencing an interruption.",
            [
                "Verify reachability and the latest successful measurements.",
                "Check power, connectivity, and relevant network-device status.",
                "Compare the incident window with other sites and upstream services.",
            ],
            "availability",
        ),
        (
            ("signal strength", "weak signal", "signal_strength", "low signal"),
            "Weak signal",
            "Radio signal quality may be insufficient for a stable connection.",
            [
                "Compare signal measurements with the site's historical baseline.",
                "Inspect antenna alignment, interference, and radio equipment status.",
                "Check whether signal deterioration coincides with packet loss or latency.",
            ],
            "weak_signal",
        ),
    ]

    for markers, title, cause, actions, rule in rules:
        if any(marker in text for marker in markers):
            return _result(
                "network_incident",
                f"{title} indicated by the incident record.",
                cause,
                evidence,
                actions,
                "Medium",
                rule,
            )

    return _result(
        "network_incident",
        "The incident record does not contain enough specific information for a confident diagnosis.",
        "The recorded incident type or description does not match a known rule.",
        evidence,
        [
            "Review the incident description and supporting telemetry.",
            "Check recent measurements for latency, packet loss, availability, and signal strength.",
            "Add a diagnostic rule after the cause has been verified.",
        ],
        "Low",
        "unknown_network_incident",
    )


def analyze_network_degradation(
    assessment: dict[str, Any],
) -> dict[str, Any]:
    """Summarize an existing degradation assessment without recalculating its score."""
    status = str(assessment.get("status") or "UNKNOWN").upper()
    site = assessment.get("site_name") or assessment.get("site_id") or "Unknown site"
    reason = str(assessment.get("reason") or "").strip()
    findings = assessment.get("findings") or []
    deteriorating = assessment.get("deteriorating_metrics") or []

    evidence = []
    if reason:
        evidence.append(reason)

    if isinstance(findings, (list, tuple)):
        for finding in findings:
            if isinstance(finding, dict):
                label = finding.get("label", "Metric")
                explanation = finding.get("explanation")
                threshold = finding.get("threshold_state")

                description = str(label)
                if explanation:
                    description += f": {explanation}"
                if threshold:
                    description += f" (threshold: {threshold})"

                evidence.append(description)
            elif finding:
                evidence.append(str(finding))
    elif findings:
        evidence.append(str(findings))

    if isinstance(deteriorating, (list, tuple)):
        evidence.extend(
            f"Deteriorating metric: {item}" for item in deteriorating if item
        )
    elif deteriorating:
        evidence.append(f"Deteriorating metrics: {deteriorating}")

    actions = []
    rules = {
        "CRITICAL": (
            "Critical network degradation",
            "The existing assessment identifies a high-priority degradation condition.",
        ),
        "WARNING": (
            "Network degradation warning",
            "The existing assessment identifies concerning network conditions.",
        ),
        "WATCH": (
            "Network condition requires monitoring",
            "The existing assessment identifies a possible developing change.",
        ),
        "STALE_DATA": (
            "Telemetry data is stale",
            "The latest measurements may be too old to reflect the current network state.",
        ),
        "INSUFFICIENT_DATA": (
            "Insufficient telemetry history",
            "There may not be enough observations to assess network behavior reliably.",
        ),
        "HEALTHY": (
            "No degradation detected by the current assessment",
            "The existing assessment did not identify a degradation condition.",
        ),
    }

    title, cause = rules.get(
        status,
        (
            "Network assessment needs review",
            "The assessment status is not recognized by the RCA rules.",
        ),
    )

    if status in {"CRITICAL", "WARNING", "WATCH"}:
        actions.extend([
            "Review the listed findings and deteriorating metrics.",
            "Compare recent measurements with the site's historical baseline.",
            "Check related incidents and equipment status before taking corrective action.",
        ])
    elif status == "STALE_DATA":
        actions.extend([
            "Check the latest measurement timestamp and ingestion pipeline.",
            "Verify that telemetry collection is running and recent records are arriving.",
        ])
    elif status == "INSUFFICIENT_DATA":
        actions.extend([
            "Check telemetry coverage and the number of available observations.",
            "Verify that measurements are being collected consistently over time.",
        ])
    else:
        actions.append("Review the underlying measurements if symptoms persist.")

    if not evidence:
        evidence.append("No detailed findings were supplied by the assessment.")

    return _result(
        "network_degradation",
        f"{title} for {site}.",
        cause,
        evidence,
        actions,
        "Medium" if status in {"CRITICAL", "WARNING", "WATCH"} else "Low",
        f"degradation_status_{status.lower()}",
    )
