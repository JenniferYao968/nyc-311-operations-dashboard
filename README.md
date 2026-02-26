# nyc-311-operations-dashboard
Cloud-native analytics dashboard powered by AWS S3 + Streamlit, with additional BI layer powered by AWS Athena

# Project Overview
This project implements a layered lakehouse architecture on AWS to process, transform, and analyze NYC 311 complaint data.
The system demonstrates:
- Cloud-based data storage (S3)
- Serverless SQL transformations (Athena)
- Layered data modeling (Staging → Integration → Fact)
- Parquet-based analytics optimization
- BI visualization via Streamlit

# This repository contains both the transformation logic (SQL + ETL) and the presentation layer (dashboard).
