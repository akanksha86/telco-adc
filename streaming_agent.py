import os
import json
import random
import time
from datetime import datetime
from google.cloud import bigquery

PROJECT_ID = os.environ.get('GCP_PROJECT', 'telco-kc')
DATASET_ID = 'raw_telco_data'
TABLE_ID = 'am_data_streaming'

os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = PROJECT_ID

bq_client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# First, ensure table exists based on am_data schema
try:
    bq_client.get_table(table_ref)
except Exception:
    schema = [
        bigquery.SchemaField("timestamp", "STRING"),
        bigquery.SchemaField("node_id", "STRING"),
        bigquery.SchemaField("node_ip", "STRING"),
        bigquery.SchemaField("alarm_id", "STRING"),
        bigquery.SchemaField("severity", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("error_code", "STRING"),
        bigquery.SchemaField("affected_imsi", "STRING"),
        bigquery.SchemaField("affected_msisdn", "STRING"),
    ]
    table = bigquery.Table(table_ref, schema=schema)
    bq_client.create_table(table)
    print(f"Created streaming table {table_ref}")

print(f"Starting real-time alarm stream into {table_ref}...")
print("Press Ctrl+C to stop.")

nodes = {f"AMF-{i:02d}": f"10.240.1.{i+10}" for i in range(1, 6)}
nodes.update({f"SMF-{i:02d}": f"10.240.2.{i+10}" for i in range(1, 6)})

try:
    while True:
        node_id = random.choice(list(nodes.keys()))
        record = {
            'timestamp': datetime.now().isoformat(),
            'node_id': node_id,
            'node_ip': nodes[node_id],
            'alarm_id': f'ALARM-STREAM-{random.randint(1000, 9999)}',
            'severity': random.choice(['MINOR', 'WARNING', 'CRITICAL']),
            'description': f'Live streaming event detected on {node_id}',
            'error_code': random.choice(['ERR-001', 'ERR-002', 'ERR-5G-CORE-099']),
            'affected_imsi': f"310150{random.randint(100000000, 999999999)}",
            'affected_msisdn': f"+1{random.randint(2000000000, 9999999999)}"
        }
        
        errors = bq_client.insert_rows_json(table_ref, [record])
        if not errors:
            print(f"[{record['timestamp']}] Streamed alarm {record['alarm_id']} ({record['severity']}) -> BigQuery")
        else:
            print(f"Encountered errors while streaming: {errors}")
            
        time.sleep(random.uniform(1.0, 3.0)) # Stream 1 event every 1-3 seconds
except KeyboardInterrupt:
    print("Streaming stopped.")
