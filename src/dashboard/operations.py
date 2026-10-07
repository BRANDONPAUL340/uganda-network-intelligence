
from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session


def _commit_if_session(session: Session) -> None:
    session.commit()


def _rollback_if_session(session: Session) -> None:
    try:
        session.rollback()
    except Exception:
        pass

# ============================================================
# SITE VALIDATION
# ============================================================

class SiteValidationModel(BaseModel):
    """Validation contract for the sites table."""

    name: str = Field(..., min_length=2, max_length=150)
    district: str = Field(..., min_length=2, max_length=100)
    region: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    site_type: str = Field(...)
    status: str = Field(...)

    @field_validator("name", "district", "region")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("site_type")
    @classmethod
    def validate_site_type(cls, value: str) -> str:
        value = value.strip()

        allowed = [
            "Data Center",
            "Macro Tower",
            "Micro Cell",
            "Rooftop Hub",
        ]

        if value not in allowed:
            raise ValueError(
                f"Site type must be one of: {', '.join(allowed)}"
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip()

        allowed = [
            "Active",
            "Inactive",
            "Maintenance",
            "Planned",
        ]

        if value not in allowed:
            raise ValueError(
                f"Site status must be one of: {', '.join(allowed)}"
            )

        return value


def ingest_new_site(
    session: Session,
    payload: Dict[str, Any],
) -> Tuple[bool, str, Optional[int]]:
    """
    Validate and insert a new site.

    Returns:
        (success, message, site_id)
    """

    try:
        validated = SiteValidationModel(**payload)
        data = validated.model_dump()

        # ----------------------------------------------------
        # Duplicate protection
        # ----------------------------------------------------

        duplicate = session.execute(
            text(
                """
                SELECT site_id
                FROM sites
                WHERE LOWER(site_name) = LOWER(:site_name)
                  AND LOWER(district) = LOWER(:district)
                LIMIT 1;
                """
            ),
            {
                "site_name": data["name"],
                "district": data["district"],
            },
        ).fetchone()

        if duplicate:
            return (
                False,
                (
                    f"Site '{data['name']}' already exists "
                    f"in {data['district']} District."
                ),
                None,
            )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        result = session.execute(
            text(
                """
                INSERT INTO sites (
                    site_name,
                    district,
                    region,
                    latitude,
                    longitude,
                    site_type,
                    status
                )
                VALUES (
                    :name,
                    :district,
                    :region,
                    :latitude,
                    :longitude,
                    :site_type,
                    :status
                )
                RETURNING site_id;
                """
            ),
            data,
        )

        new_site_id = result.scalar_one()

        _commit_if_session(session)

        return (
            True,
            f"Site '{data['name']}' saved successfully.",
            new_site_id,
        )

    except Exception as err:
        _rollback_if_session(session)

        return (
            False,
            f"Site insertion failed: {str(err)}",
            None,
        )


# ============================================================
# EQUIPMENT VALIDATION
# ============================================================

class EquipmentValidationModel(BaseModel):
    """Validation contract for the equipment table."""

    site_id: int = Field(..., ge=1)

    equipment_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    manufacturer: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    model: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    installation_date: Optional[date] = Field(default=None)

    status: str = Field(default="Active")

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Equipment type cannot be empty.")

        return value

    @field_validator("manufacturer", "model")
    @classmethod
    def clean_optional_text(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value if value else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip()

        allowed = [
            "Active",
            "Inactive",
            "Maintenance",
            "Retired",
        ]

        if value not in allowed:
            raise ValueError(
                f"Equipment status must be one of: {', '.join(allowed)}"
            )

        return value


def ingest_new_equipment(
    session: Session,
    payload: Dict[str, Any],
) -> Tuple[bool, str, Optional[int]]:
    """
    Validate and insert equipment.

    Equipment must belong to an existing site.

    Returns:
        (success, message, equipment_id)
    """

    try:
        validated = EquipmentValidationModel(**payload)
        data = validated.model_dump()

        # ----------------------------------------------------
        # Verify site exists
        # ----------------------------------------------------

        site_exists = session.execute(
            text(
                """
                SELECT site_id
                FROM sites
                WHERE site_id = :site_id;
                """
            ),
            {
                "site_id": data["site_id"],
            },
        ).fetchone()

        if not site_exists:
            return (
                False,
                (
                    f"Site ID {data['site_id']} does not exist. "
                    "Create the site before adding equipment."
                ),
                None,
            )

        # ----------------------------------------------------
        # Duplicate protection
        # ----------------------------------------------------

        duplicate = session.execute(
            text(
                """
                SELECT equipment_id
                FROM equipment
                WHERE site_id = :site_id
                  AND equipment_type = :equipment_type
                  AND manufacturer IS NOT DISTINCT FROM :manufacturer
                  AND model IS NOT DISTINCT FROM :model
                LIMIT 1;
                """
            ),
            {
                "site_id": data["site_id"],
                "equipment_type": data["equipment_type"],
                "manufacturer": data["manufacturer"],
                "model": data["model"],
            },
        ).fetchone()

        if duplicate:
            return (
                False,
                "This equipment already exists at the selected site.",
                None,
            )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        result = session.execute(
            text(
                """
                INSERT INTO equipment (
                    site_id,
                    equipment_type,
                    manufacturer,
                    model,
                    installation_date,
                    status
                )
                VALUES (
                    :site_id,
                    :equipment_type,
                    :manufacturer,
                    :model,
                    :installation_date,
                    :status
                )
                RETURNING equipment_id;
                """
            ),
            data,
        )

        equipment_id = result.scalar_one()

        _commit_if_session(session)

        return (
            True,
            f"Equipment #{equipment_id} saved successfully.",
            equipment_id,
        )

    except Exception as err:
        _rollback_if_session(session)

        return (
            False,
            f"Equipment insertion failed: {str(err)}",
            None,
        )


# ============================================================
# MEASUREMENT VALIDATION
# ============================================================

class MeasurementValidationModel(BaseModel):
    """Validation contract for the measurements table."""

    equipment_id: int = Field(..., ge=1)

    site_id: int = Field(..., ge=1)

    measured_at: datetime = Field(...)

    traffic_mb: Optional[float] = Field(
        default=None,
        ge=0,
    )

    latency_ms: Optional[float] = Field(
        default=None,
        ge=0,
        le=10000,
    )

    packet_loss_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    signal_strength_dbm: Optional[float] = Field(
        default=None,
        ge=-150,
        le=0,
    )

    availability_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )


def ingest_network_measurement(
    session: Session,
    payload: Dict[str, Any],
) -> Tuple[bool, str, Optional[int]]:
    """
    Validate and insert a raw network measurement.

    Measurements are inserted into the RAW `measurements`
    table, not directly into `silver_measurements`.

    Returns:
        (success, message, measurement_id)
    """

    try:
        validated = MeasurementValidationModel(**payload)
        data = validated.model_dump()

        # ----------------------------------------------------
        # Verify site exists
        # ----------------------------------------------------

        site_exists = session.execute(
            text(
                """
                SELECT site_id
                FROM sites
                WHERE site_id = :site_id;
                """
            ),
            {
                "site_id": data["site_id"],
            },
        ).fetchone()

        if not site_exists:
            return (
                False,
                f"Site ID {data['site_id']} does not exist.",
                None,
            )

        # ----------------------------------------------------
        # Verify equipment exists
        # ----------------------------------------------------

        equipment = session.execute(
            text(
                """
                SELECT equipment_id, site_id
                FROM equipment
                WHERE equipment_id = :equipment_id;
                """
            ),
            {
                "equipment_id": data["equipment_id"],
            },
        ).fetchone()

        if not equipment:
            return (
                False,
                (
                    f"Equipment ID {data['equipment_id']} "
                    "does not exist."
                ),
                None,
            )

        if equipment.site_id != data["site_id"]:
            return (
                False,
                (
                    f"Equipment ID {data['equipment_id']} belongs "
                    f"to Site ID {equipment.site_id}, not "
                    f"Site ID {data['site_id']}."
                ),
                None,
            )

        # ----------------------------------------------------
        # Prevent duplicate measurement
        # ----------------------------------------------------

        duplicate = session.execute(
            text(
                """
                SELECT measurement_id
                FROM measurements
                WHERE equipment_id = :equipment_id
                  AND site_id = :site_id
                  AND measured_at = :measured_at
                LIMIT 1;
                """
            ),
            {
                "equipment_id": data["equipment_id"],
                "site_id": data["site_id"],
                "measured_at": data["measured_at"],
            },
        ).fetchone()

        if duplicate:
            return (
                False,
                (
                    "A measurement already exists for this "
                    "equipment, site, and timestamp."
                ),
                None,
            )

        # ----------------------------------------------------
        # Insert into RAW measurements
        # ----------------------------------------------------

        result = session.execute(
            text(
                """
                INSERT INTO measurements (
                    equipment_id,
                    site_id,
                    measured_at,
                    traffic_mb,
                    latency_ms,
                    packet_loss_pct,
                    signal_strength_dbm,
                    availability_pct
                )
                VALUES (
                    :equipment_id,
                    :site_id,
                    :measured_at,
                    :traffic_mb,
                    :latency_ms,
                    :packet_loss_pct,
                    :signal_strength_dbm,
                    :availability_pct
                )
                RETURNING measurement_id;
                """
            ),
            data,
        )

        measurement_id = result.scalar_one()

        _commit_if_session(session)

        return (
            True,
            f"Measurement #{measurement_id} saved successfully.",
            measurement_id,
        )

    except Exception as err:
        _rollback_if_session(session)

        return (
            False,
            f"Measurement insertion failed: {str(err)}",
            None,
        )


# ============================================================
# INCIDENT VALIDATION
# ============================================================

class IncidentValidationModel(BaseModel):
    """Validation contract for the incidents table."""

    site_id: int = Field(..., ge=1)

    equipment_id: Optional[int] = Field(
        default=None,
        ge=1,
    )

    incident_type: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    severity: str = Field(...)

    start_time: datetime = Field(...)

    end_time: Optional[datetime] = Field(
        default=None,
    )

    status: str = Field(...)

    description: Optional[str] = Field(
        default=None,
    )

    @field_validator("incident_type")
    @classmethod
    def clean_incident_type(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Incident type cannot be empty.")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value if value else None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        allowed = [
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ]

        normalized = value.strip().upper()

        if normalized not in allowed:
            raise ValueError(
                f"Severity must be one of: {', '.join(allowed)}"
            )

        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = [
            "OPEN",
            "IN_PROGRESS",
            "RESOLVED",
            "CLOSED",
        ]

        normalized = value.strip().upper()

        if normalized not in allowed:
            raise ValueError(
                f"Status must be one of: {', '.join(allowed)}"
            )

        return normalized

    @model_validator(mode="after")
    def validate_incident_timestamps(self):
        # ----------------------------------------------------
        # End cannot happen before start
        # ----------------------------------------------------

        if self.end_time and self.end_time < self.start_time:
            raise ValueError(
                "Chronology Error: 'End Time' cannot occur "
                "before 'Start Time'."
            )

        # ----------------------------------------------------
        # Resolved/closed incidents require an end timestamp
        # ----------------------------------------------------

        if (
            self.status in {"RESOLVED", "CLOSED"}
            and self.end_time is None
        ):
            raise ValueError(
                "Operational Rule Mismatch: A resolved or "
                "closed incident requires an 'End Time'."
            )

        return self


def ingest_incident(
    session: Session,
    payload: Dict[str, Any],
) -> Tuple[bool, str, Optional[int]]:
    """
    Validate and insert a raw operational incident.

    Returns:
        (success, message, incident_id)
    """

    try:
        validated = IncidentValidationModel(**payload)
        data = validated.model_dump()

        # ----------------------------------------------------
        # Verify site
        # ----------------------------------------------------

        site_exists = session.execute(
            text(
                """
                SELECT site_id
                FROM sites
                WHERE site_id = :site_id;
                """
            ),
            {
                "site_id": data["site_id"],
            },
        ).fetchone()

        if not site_exists:
            return (
                False,
                f"Site ID {data['site_id']} does not exist.",
                None,
            )

        # ----------------------------------------------------
        # Verify optional equipment
        # ----------------------------------------------------

        if data["equipment_id"] is not None:

            equipment = session.execute(
                text(
                    """
                    SELECT equipment_id, site_id
                    FROM equipment
                    WHERE equipment_id = :equipment_id;
                    """
                ),
                {
                    "equipment_id": data["equipment_id"],
                },
            ).fetchone()

            if not equipment:
                return (
                    False,
                    (
                        f"Equipment ID {data['equipment_id']} "
                        "does not exist."
                    ),
                    None,
                )

            if equipment.site_id != data["site_id"]:
                return (
                    False,
                    (
                        f"Equipment ID {data['equipment_id']} "
                        f"belongs to Site ID {equipment.site_id}, "
                        f"not Site ID {data['site_id']}."
                    ),
                    None,
                )

        # ----------------------------------------------------
        # Prevent duplicate incident
        # ----------------------------------------------------

        duplicate = session.execute(
            text(
                """
                SELECT incident_id
                FROM incidents
                WHERE site_id = :site_id
                  AND equipment_id IS NOT DISTINCT FROM :equipment_id
                  AND incident_type = :incident_type
                  AND start_time = :start_time
                LIMIT 1;
                """
            ),
            {
                "site_id": data["site_id"],
                "equipment_id": data["equipment_id"],
                "incident_type": data["incident_type"],
                "start_time": data["start_time"],
            },
        ).fetchone()

        if duplicate:
            return (
                False,
                "This incident already exists.",
                None,
            )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        result = session.execute(
            text(
                """
                INSERT INTO incidents (
                    site_id,
                    equipment_id,
                    incident_type,
                    severity,
                    start_time,
                    end_time,
                    status,
                    description
                )
                VALUES (
                    :site_id,
                    :equipment_id,
                    :incident_type,
                    :severity,
                    :start_time,
                    :end_time,
                    :status,
                    :description
                )
                RETURNING incident_id;
                """
            ),
            data,
        )

        incident_id = result.scalar_one()

        _commit_if_session(session)

        return (
            True,
            f"Incident #{incident_id} saved successfully.",
            incident_id,
        )

    except Exception as err:
        _rollback_if_session(session)

        return (
            False,
            f"Incident insertion failed: {str(err)}",
            None,
        )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def ingest_pipeline_incident(
    session: Session,
    payload: Dict[str, Any],
) -> Tuple[bool, str, Optional[int]]:
    """
    Backward-compatible wrapper.

    Older dashboard code may still call
    `ingest_pipeline_incident()`.

    The implementation writes to the real `incidents` table.
    """

    return ingest_incident(
        session=session,
        payload=payload,
    )