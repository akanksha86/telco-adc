import google.auth
import google.auth.transport.requests
import urllib.request
import urllib.parse
import json

try:
    credentials, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    
    entry_name = "projects/568311752105/locations/us-central1/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/telco-kc/datasets/raw_telco_data/tables/am_data_streaming"
    
    # We must URL encode the entry ID part because it contains slashes
    parts = entry_name.split("/entries/")
    if len(parts) == 2:
        entry_id = urllib.parse.quote(parts[1], safe="")
        encoded_name = f"{parts[0]}/entries/{entry_id}"
    else:
        encoded_name = entry_name
        
    url = f"https://dataplex.googleapis.com/v1/{encoded_name}?view=FULL"
    print(f"Fetching: {url}")
    
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {credentials.token}")
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Success! Aspect Keys:", data.get("aspects", {}).keys())
except Exception as e:
    print(f"REST Failed: {e}")
