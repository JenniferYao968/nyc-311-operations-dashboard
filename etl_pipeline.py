import pandas as pd
import boto3
import requests
from io import StringIO
import os

# --- Configuration ---
# In a real production environment, use os.getenv() for keys.
# For this script, you can temporarily paste them here, but DO NOT push keys to GitHub.
AWS_ACCESS_KEY = 'YOUR_ACCESS_KEY_ID_HERE'
AWS_SECRET_KEY = 'YOUR_SECRET_ACCESS_KEY_HERE'
BUCKET_NAME = 'jennifer-311-nyc-data'
FILE_NAME = 'nyc_311_2025_cleaned.csv'


# --- 1. EXTRACT: Fetch data from NYC Open Data API ---
print("🔌 Connecting to NYC Open Data API...")
# The endpoint for 311 Service Requests
url = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"

# SoQL (Socrata Query Language) Parameters
# We filter STRICTLY for the year 2025 to analyze historical trends.
# We limit to 50,000 rows to ensure the dashboard remains fast.
params = {
    "$where": "created_date >= '2025-10-01T00:00:00' AND created_date <= '2025-12-31T23:59:59'",
    "$limit": 1000000,
    "$order": "created_date DESC"
}

response = requests.get(url, params=params)
if response.status_code == 200:
    print("Data downloaded successfully. Starting transformation")
    
    
    # --- 2. TRANSFORM: Clean the data in memory ---
    # Read the raw CSV text into a Pandas DataFrame
    df = pd.read_csv(StringIO(response.text))
    # Select only relevant columns to optimize storage
    cols_to_keep = ['created_date', 'complaint_type', 'borough', 'latitude', 'longitude', 'status']
    df = df[cols_to_keep]
    # Drop rows with missing location data (crucial for mapping)
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    print(f"📊 Transformed Data: {len(df)} rows ready for upload.")
    
    
    # --- 3. LOAD: Upload to AWS S3 ---
    print("☁️ Uploading to AWS S3...")
    # Create the S3 Client
    s3_client = boto3.client("s3", region_name="us-east-1")

    
    # Convert DataFrame to CSV buffer (in-memory)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    print("DEBUG AWS_ACCESS_KEY_ID (from script):", os.environ.get("AWS_ACCESS_KEY_ID"))
    # Put the object into the bucket
    s3_client.put_object(
    Bucket=BUCKET_NAME,
    Key=FILE_NAME,
    Body=csv_buffer.getvalue()
    )
    print(f"🚀 Success! File saved to S3 bucket: {BUCKET_NAME}/{FILE_NAME}")

else:
    print(f"❌ Error fetching data: {response.status_code}")
    print(response.text)