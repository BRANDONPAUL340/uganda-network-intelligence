
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy import text

from src.config import PIPELINE_NAME
from src.database import engine


def check_database_connection() -> bool:
    '''
    Return True when PostgreSQL is reachable, otherwise False.
    '''
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return True
    except Exception:
        return False


def get_pipeline_kpis() -> pd.DataFrame:
    '''
    Return the current operational KPI summary.
    '''
    query = text(
        '''
        WITH pipeline_stats AS (
            SELECT
                COUNT(*) AS total_runs,
                COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs
            FROM pipeline_runs
        ),
        network_stats AS (
            SELECT
                COALESCE(
                    AVG(
                        CASE
                            WHEN network_health = 'HEALTHY' THEN 100.0
                            ELSE 0.0
                        END
                    ),
                    0
                ) AS healthy_percentage,
                COALESCE(SUM(total_incidents), 0) AS total_alerts,
                COALESCE(SUM(critical_incidents), 0) AS total_critical_alerts
            FROM gold_network_intelligence
        )
        SELECT
            CASE
                WHEN ps.total_runs = 0 THEN 0
                ELSE ROUND(
                    ps.successful_runs * 100.0 / ps.total_runs,
                    2
                )
            END AS pipeline_success_rate,
            ROUND(ns.healthy_percentage, 2) AS healthy_percentage,
            ns.total_alerts,
            ns.total_critical_alerts
        FROM pipeline_stats ps
        CROSS JOIN network_stats ns
        '''
    )

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def get_current_health() -> pd.DataFrame:
    '''
    Return the current overall pipeline health.
    '''
    query = text(
        '''
        SELECT
            CASE
                WHEN pipeline_status = 'SUCCESS'
                    THEN 'HEALTHY'
                WHEN pipeline_status = 'RUNNING'
                    THEN 'WARNING'
                WHEN pipeline_status = 'FAILED'
                    THEN 'CRITICAL'
                ELSE 'UNKNOWN'
            END AS overall_status,
            pipeline_completed_at AS checked_at
        FROM pipeline_operational_metrics
        WHERE pipeline_name = :pipeline_name
        ORDER BY run_id DESC
        LIMIT 1
        '''
    )

    with engine.connect() as connection:
        return pd.read_sql(
            query,
            connection,
            params={'pipeline_name': PIPELINE_NAME},
        )


def get_daily_health() -> pd.DataFrame:
    '''
    Return daily network health percentages from the Gold layer.
    '''
    query = text(
        '''
        SELECT
            measurement_date AS health_date,
            ROUND(
                AVG(
                    CASE
                        WHEN network_health = 'HEALTHY'
                            THEN 100.0
                        ELSE 0.0
                    END
                ),
                2
            ) AS healthy_percentage
        FROM gold_network_intelligence
        GROUP BY measurement_date
        ORDER BY measurement_date
        '''
    )

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def get_stage_summary() -> pd.DataFrame:
    '''
    Return the latest pipeline stage execution summary.
    '''
    query = text(
        '''
        SELECT
            stage_name,
            status,
            records_read,
            records_inserted,
            records_rejected,
            records_skipped,
            duration_seconds,
            started_at,
            completed_at
        FROM pipeline_stage_runs
        WHERE run_id = (
            SELECT MAX(run_id)
            FROM pipeline_runs
            WHERE pipeline_name = :pipeline_name
        )
        ORDER BY stage_run_id
        '''
    )

    with engine.connect() as connection:
        return pd.read_sql(
            query,
            connection,
            params={'pipeline_name': PIPELINE_NAME},
        )


def get_site_performance(
    region: Optional[str] = None,
    district: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    '''
    Return Gold site-level daily network performance.
    '''
    query = text(
        '''
        SELECT
            site_id,
            site_name,
            region,
            district,
            measurement_date,
            measurement_count,
            avg_traffic_mb,
            avg_latency_ms,
            avg_packet_loss_pct,
            avg_signal_strength_dbm,
            avg_availability_pct,
            updated_at
        FROM gold_site_daily_performance
        WHERE (CAST(:region AS VARCHAR) IS NULL
               OR region = CAST(:region AS VARCHAR))
          AND (CAST(:district AS VARCHAR) IS NULL
               OR district = CAST(:district AS VARCHAR))
          AND (CAST(:start_date AS DATE) IS NULL
               OR measurement_date >= CAST(:start_date AS DATE))
          AND (CAST(:end_date AS DATE) IS NULL
               OR measurement_date <= CAST(:end_date AS DATE))
        ORDER BY measurement_date, site_id
        '''
    )

    params = {
        'region': region,
        'district': district,
        'start_date': start_date,
        'end_date': end_date,
    }

    with engine.connect() as connection:
        return pd.read_sql(query, connection, params=params)


def get_network_summary(
    region: Optional[str] = None,
    district: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    '''
    Return aggregated network performance for the selected filters.
    '''
    query = text(
        '''
        SELECT
            COUNT(DISTINCT site_id) AS total_sites,
            COALESCE(SUM(measurement_count), 0) AS total_measurements,
            ROUND(AVG(avg_traffic_mb), 2) AS avg_traffic_mb,
            ROUND(AVG(avg_latency_ms), 2) AS avg_latency_ms,
            ROUND(AVG(avg_packet_loss_pct), 2) AS avg_packet_loss_pct,
            ROUND(AVG(avg_signal_strength_dbm), 2) AS avg_signal_strength_dbm,
            ROUND(AVG(avg_availability_pct), 2) AS avg_availability_pct
        FROM gold_site_daily_performance
        WHERE (CAST(:region AS VARCHAR) IS NULL
               OR region = CAST(:region AS VARCHAR))
          AND (CAST(:district AS VARCHAR) IS NULL
               OR district = CAST(:district AS VARCHAR))
          AND (CAST(:start_date AS DATE) IS NULL
               OR measurement_date >= CAST(:start_date AS DATE))
          AND (CAST(:end_date AS DATE) IS NULL
               OR measurement_date <= CAST(:end_date AS DATE))
        '''
    )

    params = {
        'region': region,
        'district': district,
        'start_date': start_date,
        'end_date': end_date,
    }

    with engine.connect() as connection:
        return pd.read_sql(query, connection, params=params)
