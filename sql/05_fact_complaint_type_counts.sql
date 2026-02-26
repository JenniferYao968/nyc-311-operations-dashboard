-- ========================================
-- FACT TABLE: Complaints by Complaint Type
-- Shows distribution of issue categories
-- ========================================

CREATE TABLE complaint_type_counts
WITH (
  format = 'PARQUET',
  external_location = 's3://jennifer-311-nyc-data/fact/complaint_type_counts/'
) AS
SELECT
  complaint_type,
  COUNT(*) AS complaint_count
FROM nyc_311_cleaned
GROUP BY complaint_type;
