-- ========================================
-- FACT TABLE: Complaints by Borough
-- Aggregates total complaints per borough
-- ========================================

CREATE TABLE borough_complaints
WITH (
  format = 'PARQUET',
  external_location = 's3://jennifer-311-nyc-data/fact/borough_complaints/'
) AS
SELECT
  borough,
  COUNT(*) AS complaint_count
FROM nyc_311_cleaned
GROUP BY borough;
