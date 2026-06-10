from google.cloud import logging

def fetch_logs():
    client = logging.Client(project="telco-kc")
    # Fetch logs for the Cloud Function
    filter_str = 'resource.type="cloud_run_revision" AND resource.labels.service_name="retention-agent"'
    
    print("Fetching recent logs for Retention Agent Cloud Function...")
    entries = client.list_entries(filter_=filter_str, order_by=logging.DESCENDING, max_results=10)
    
    found = False
    for entry in entries:
        found = True
        print(f"[{entry.timestamp}] {entry.payload}")
        
    if not found:
        print("No logs found. The Cloud Function has not been triggered.")
        
if __name__ == "__main__":
    fetch_logs()
