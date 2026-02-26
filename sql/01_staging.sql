-- ========================================
-- STAGING LAYER
-- Reads raw NYC 311 CSV from S3
-- No transformations applied
-- ========================================

CREATE EXTERNAL TABLE nyc_311_raw (
  created_date string,
  complaint_type string,
  borough string,
  latitude double,
  longitude double,
  status string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\"",
  "escapeChar"    = "\\"
)
LOCATION 's3://jennifer-311-nyc-data/'
TBLPROPERTIES ("skip.header.line.count"="1");
