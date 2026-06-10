import base64
import json
import functions_framework
from google.cloud import bigquery

bq_client = bigquery.Client()

@functions_framework.cloud_event
def process_metadata_change(cloud_event):
    """
    Triggered by a Dataplex Metadata Change Feed Pub/Sub message.
    Translates Declarative Aspects in Knowledge Catalog into physical BigQuery DDL.
    """
    print(f"Received event: {cloud_event}")
    
    # 1. Extract Pub/Sub Message payload
    if "data" not in cloud_event.data or "message" not in cloud_event.data["data"]:
        print("Invalid Pub/Sub payload structure.")
        return

    pubsub_message = cloud_event.data["data"]["message"]
    if "data" not in pubsub_message:
        print("No data in Pub/Sub message.")
        return
        
    decoded_data = base64.b64decode(pubsub_message["data"]).decode('utf-8')
    print(f"Decoded metadata change event: {decoded_data}")
    
    try:
        # 2. Parse the Dataplex Event
        payload = json.loads(decoded_data)
        
        # Real Dataplex Metadata Change Feeds deliver complex JSON containing Entry and Aspect details.
        # We need to dynamically extract the table/dataset name and search for our 'retention_policy' aspect.
        
        retention_days = None
        # Recursively search for the "retention_days" key anywhere in the payload (in case of nested Aspect payloads)
        def find_retention_days(d):
            if isinstance(d, dict):
                if "retention_days" in d:
                    return d["retention_days"]
                for v in d.values():
                    res = find_retention_days(v)
                    if res is not None:
                        return res
            return None
            
        retention_days = find_retention_days(payload)
        
        # In a real environment, you parse the BigQuery FQN from the Dataplex Entry Name:
        # e.g., 'bigquery:telco-kc.raw_telco_data.am_data_streaming'
        # For demo fallback, we attempt to extract it or default to the streaming table.
        resource_name = payload.get("resource_name", "telco-kc.raw_telco_data.am_data_streaming")
        resource_type = payload.get("resource_type", "TABLE").upper()
        
        if retention_days is None:
            print("No 'retention_days' aspect update found in this event. Ignoring.")
            return
            
        print(f"Agent Triggered: Enforcing {retention_days} days retention on {resource_type} {resource_name}")
        
        # 3. Generate the physical DDL command
        if resource_type == "TABLE":
            expiration_hours = int(retention_days) * 24
            query = f"ALTER TABLE `{resource_name}` SET OPTIONS(expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL {expiration_hours} HOUR));"
        elif resource_type == "DATASET":
            # Dataset retention is configured via default_table_expiration_days
            # BigQuery DDL for dataset options expects expiration in milliseconds (days * 24 * 60 * 60 * 1000) or using the correct option.
            # DDL: ALTER SCHEMA `my_project.my_dataset` SET OPTIONS(default_table_expiration_days=X)
            query = f"ALTER SCHEMA `{resource_name}` SET OPTIONS(default_table_expiration_days={retention_days});"
        else:
            print(f"Unsupported resource type: {resource_type}")
            return
            
        print(f"Executing BigQuery DDL: {query}")
        
        # 4. Execute the governance policy physically in the database
        job = bq_client.query(query)
        job.result()
        
        print("Successfully synchronized Knowledge Catalog Aspect with BigQuery Storage Engine!")
        
    except Exception as e:
        print(f"Agent failed to process metadata change: {e}")
