-- Migration: 011
-- Description: Deploy unique composite index on gold_site_daily_performance (site_id, measurement_date)

CREATE UNIQUE INDEX IF NOT EXISTS uq_gold_site_daily_performance_site_date
ON gold_site_daily_performance (
    site_id,
    measurement_date
);
