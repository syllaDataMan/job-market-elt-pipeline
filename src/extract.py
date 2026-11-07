import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_jobs(what="data engineer", where="New York", max_pages=1):
    """
    Fetches job postings from the Adzuna API.
    """
    all_jobs = []
    
    for page in range(1, max_pages + 1):
        # Using the US endpoint. Ensure your app_id and app_key match this region.
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
        
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": what,
            "where": where,
            "content-type": "application/json"
        }
        
        print(f"Fetching page {page} for '{what}' in '{where}'...")
        response = requests.get(url, params=params)
        
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"Found {len(results)} jobs on this page.")
            if not results:
                break
            all_jobs.extend(results)
        else:
            print(f"Error: Failed to fetch data. Status code: {response.status_code}")
            print(response.text)
            break
            
    return all_jobs

def transform_raw_data(jobs_list):
    """
    Flattens the raw JSON into a clean tabular structure suitable for a Data Lake.
    """
    parsed_data = []
    for job in jobs_list:
        parsed_data.append({
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "contract_type": job.get("contract_type"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "created": job.get("created"),
            "redirect_url": job.get("redirect_url"),
            "extracted_at": datetime.utcnow().isoformat()
        })
    return pd.DataFrame(parsed_data)

if __name__ == "__main__":
    # Test with a major US tech hub location
    raw_jobs = fetch_jobs(what="data engineer", where="New York", max_pages=1)
    
    if raw_jobs:
        df = transform_raw_data(raw_jobs)
        print(f"Successfully extracted {len(df)} jobs.")
        
        # Save a local raw backup to prove the pipeline works locally
        output_path = "data/raw_jobs.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved local raw data backup to {output_path}")
    else:
        print("Extraction completed, but no job records were returned.")