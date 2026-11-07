import os
import json
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv
from extract import fetch_jobs

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def upload_to_s3(data_list, job_keyword):
    """
    Uploads raw data as Newline-Delimited JSON (JSONL) to the AWS S3 Data Lake.
    """
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    timestamp = now_utc.strftime("%H%M%S")
    
    # Save with a .jsonl extension to denote newline-delimited format
    file_name = f"raw/jobs/{job_keyword}/{date_str}/jobs_{timestamp}.jsonl"
    
    try:
        # Convert list of dictionaries into JSONL format (one JSON object per line)
        jsonl_data = "\n".join([json.dumps(job) for job in data_list])
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=jsonl_data,
            ContentType="application/x-ndjson"
        )
        print(f"Successfully uploaded {len(data_list)} records as JSONL to s3://{BUCKET_NAME}/{file_name}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")

if __name__ == "__main__":
    keyword = "data_engineer"
    raw_jobs = fetch_jobs(what="data engineer", where="New York", max_pages=1)
    
    if raw_jobs:
        upload_to_s3(raw_jobs, keyword)
    else:
        print("No jobs to upload.")