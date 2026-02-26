-- ========================================
-- INTEGRATION LAYER
-- Converts raw strings to proper types
-- Stores data in Parquet format
-- ========================================

CREATE TABLE nyc_311_cleaned
WITH (
  format = 'PARQUET',
  external_location = 's3://jennifer-311-nyc-data/integration/nyc_311_cleaned/'
) AS
SELECT
  CAST(from_iso8601_timestamp(created_date) AS TIMESTAMP) AS time,
  complaint_type,
  borough,
  latitude,
  longitude,
  status
FROM nyc_311_raw
WHERE created_date IS NOT NULL;
