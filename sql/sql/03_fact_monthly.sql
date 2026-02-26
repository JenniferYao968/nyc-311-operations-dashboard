-- ========================================
-- FACT TABLE: Monthly Complaint Counts
-- Aggregated metrics for BI layer
-- ========================================

CREATE TABLE monthly_complaints
WITH (
  format = 'PARQUET',
  external_location = 's3://jennifer-311-nyc-data/fact/monthly_complaints/'
) AS
SELECT
  date_format(time, '%Y-%m') AS year_month,
  COUNT(*) AS complaint_count
FROM nyc_311_cleaned
GROUP BY 1;
