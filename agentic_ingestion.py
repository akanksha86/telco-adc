import os
import json
import pandas as pd
from google.cloud import bigquery
from google.cloud import dlp_v2

PROJECT_ID = 'telco-kc'
DATASET_ID = 'raw_telco_data'
REGION = 'us-central1'

os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = PROJECT_ID

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
dlp_client = dlp_v2.DlpServiceClient()
parent = f"projects/{PROJECT_ID}/locations/global"

from google.api_core.exceptions import NotFound

def create_dataset_if_not_exists():
    dataset_ref = bq_client.dataset(DATASET_ID)
    try:
        bq_client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = REGION
        dataset = bq_client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {DATASET_ID} in {REGION}.")

def mask_text_with_dlp(text):
    if not isinstance(text, str) or not text:
        return text
    
    inspect_config = {
        "info_types": [
            {"name": "IP_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "IMSI_ID"}, # Custom or built-in
            {"name": "MAC_ADDRESS"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"}
        ],
        "min_likelihood": dlp_v2.Likelihood.POSSIBLE,
    }

    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "character_mask_config": {
                            "masking_character": "*",
                            "number_to_mask": 0,
                            "reverse_order": False,
                        }
                    }
                }
            ]
        }
    }

    item = {"value": text}
    try:
        response = dlp_client.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )
        return response.item.value
    except Exception as e:
        print(f"DLP Error: {e}")
        return text

def load_and_mask_am_data():
    print("Loading and masking AM Data...")
    records = []
    with open('data/am_data.jsonl', 'r') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    
    # Process a sample of records to avoid long runtimes for the demo
    # In a real scenario, this would be a bulk job or Dataflow pipeline
    print(f"Processing {len(records)} AM records through DLP (in-flight masking)...")
    for i, r in enumerate(records):
        # Mask PII fields
        r['node_ip'] = mask_text_with_dlp(r.get('node_ip', ''))
        r['description'] = mask_text_with_dlp(r.get('description', ''))
        if r.get('affected_msisdn'):
            r['affected_msisdn'] = mask_text_with_dlp(r.get('affected_msisdn'))
        
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{len(records)} records...")
            
    df = pd.DataFrame(records)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.am_data"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {job.output_rows} rows into {table_id}.")

def load_pm_data():
    # We will upload the PM data RAW to demonstrate the BigQuery DLP Remote Function
    print("Loading RAW PM Data (No masking applied yet)...")
    df = pd.read_csv('data/pm_data.csv')
    
    table_id = f"{PROJECT_ID}.{DATASET_ID}.pm_data"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {job.output_rows} raw rows into {table_id}.")

def load_customer_data():
    print("Loading Customer Data (CII)...")
    df = pd.read_csv('data/customer_data.csv')
    
    table_id = f"{PROJECT_ID}.{DATASET_ID}.customer_data"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {job.output_rows} rows into {table_id}.")

if __name__ == "__main__":
    create_dataset_if_not_exists()
    load_and_mask_am_data()
    load_pm_data()
    load_customer_data()
    print("Agentic Ingestion complete!")
