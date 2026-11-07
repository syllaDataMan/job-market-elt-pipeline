import os
import boto3
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

# 1. Point to your Google Cloud credentials JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# Initialize clients
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
bq_client = bigquery.Client()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DATASET_ID = "job_market_dw"
TABLE_ID = "raw_jobs_staging"
FULL_TABLE_ID = f"{bq_client.project}.{DATASET_ID}.{TABLE_ID}"

def fetch_latest_file_from_s3():
    """
    Finds and downloads the latest raw JSON job file from the AWS S3 Data Lake.
    """
    print(f"Searching for files in S3 bucket: {BUCKET_NAME}...")
    
    # List objects under the raw/jobs/ prefix
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix="raw/jobs/data_engineer/"
    )
    
    if "Contents" not in response:
        print("No files found in the S3 Data Lake prefix.")
        return None

    # Sort objects by LastModified timestamp to get the latest file
    files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
    latest_file_key = files[0]["Key"]
    
    print(f"Found latest file in S3: {latest_file_key}")
    
    # Download locally to a temporary path
    os.makedirs("data/temp", exist_ok=True)
    local_temp_path = "data/temp/latest_jobs.json"
    
    s3_client.download_file(BUCKET_NAME, latest_file_key, local_temp_path)
    print(f"Downloaded file temporarily to {local_temp_path}")
    
    return local_temp_path

def load_json_to_bigquery(file_path):
    """
    Loads the temporary JSON file into Google BigQuery Staging table.
    """
    if not file_path:
        return

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,  # Automatically detect schema from JSON keys
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND, # Append daily data
    )

    with open(file_path, "rb") as source_file:
        load_job = bq_client.load_table_from_file(
            source_file,
            FULL_TABLE_ID,
            job_config=job_config
        )

    # Wait for BigQuery job to finish
    load_job.result()

    table = bq_client.get_table(FULL_TABLE_ID)
    print(f"Successfully loaded data into BigQuery! Total rows in table: {table.num_rows}")

if __name__ == "__main__":
    temp_file = fetch_latest_file_from_s3()
    if temp_file:
        load_json_to_bigquery(temp_file)