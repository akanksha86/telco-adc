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
    if "message" not in cloud_event.data:
        print("Invalid Pub/Sub payload structure.")
        return

    pubsub_message = cloud_event.data["message"]
    if "data" not in pubsub_message:
        print("No data in Pub/Sub message.")
        return
        
    decoded_data = base64.b64decode(pubsub_message["data"]).decode('utf-8')
    print(f"Decoded metadata change event: {decoded_data}")
    
    try:
        payload = json.loads(decoded_data)
        
        # 2. Extract Entry Name
        entry_name = payload.get("entryName")
        if not entry_name:
            print("No entryName found in payload.")
            return
            
        print(f"Fetching full Entry snapshot from Dataplex for: {entry_name}")
        
        # 3. Fetch the full Aspect payload from Dataplex API (requires view=ALL)
        import google.auth
        import google.auth.transport.requests
        import urllib.request
        
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        url = f"https://dataplex.googleapis.com/v1/{entry_name}?view=FULL"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {credentials.token}")
        
        try:
            with urllib.request.urlopen(req) as response:
                entry_data = json.loads(response.read().decode())
        except Exception as e:
            print(f"Failed to fetch Dataplex entry: {e}")
            return
            
        # 4. Search for retention_days inside the fetched Entry aspects
        retention_days = None
        def find_retention_days(d):
            if isinstance(d, dict):
                if "retention_days" in d:
                    return d["retention_days"]
                for v in d.values():
                    res = find_retention_days(v)
                    if res is not None:
                        return res
            elif isinstance(d, list):
                for item in d:
                    res = find_retention_days(item)
                    if res is not None:
                        return res
            return None
            
        retention_days = find_retention_days(entry_data.get("aspects", {}))
        
        if retention_days is None:
            print("No 'retention_days' aspect update found on this entry. Ignoring.")
            return
            
        # Extract BQ table name from fullyQualifiedName (e.g. bigquery:telco-kc.raw_telco_data.am_data_streaming)
        fqn = payload.get("fullyQualifiedName", "")
        if fqn.startswith("bigquery:"):
            resource_name = fqn.split(":", 1)[1]
        else:
            resource_name = "telco-kc.raw_telco_data.am_data_streaming"
            
        resource_type = "TABLE" if "tables" in entry_name else "DATASET"
        
        
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
