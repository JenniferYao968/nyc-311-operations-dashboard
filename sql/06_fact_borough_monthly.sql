-- ========================================
-- FACT TABLE: Borough-Level Monthly Trends
-- Enables time-series breakdown per borough
-- ========================================

CREATE TABLE borough_monthly_complaints
WITH (
  format = 'PARQUET',
  external_location = 's3://jennifer-311-nyc-data/fact/borough_monthly_complaints/'
) AS
SELECT
  borough,
  date_format(time, '%Y-%m') AS year_month,
  COUNT(*) AS complaint_count
FROM nyc_311_cleaned
GROUP BY borough, 2;
