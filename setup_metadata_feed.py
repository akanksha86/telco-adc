import json
import subprocess
import urllib.request
import urllib.error

def get_access_token():
    result = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    return result.stdout.strip()

def setup_feed():
    token = get_access_token()
    if not token:
        print("Failed to get gcloud token. Please ensure you are authenticated.")
        return
        
    project_id = "telco-kc"
    location = "us-central1"
    feed_id = "telco-aspect-feed"
    
    url = f"https://dataplex.googleapis.com/v1/projects/{project_id}/locations/{location}/metadataFeeds?metadataFeedId={feed_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "pubsubTopic": f"projects/{project_id}/topics/dataplex-metadata-changes",
        "scope": {
            "projects": [f"projects/{project_id}"]
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    print(f"Creating Dataplex Metadata Change Feed '{feed_id}' via REST API...")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print("Success! Metadata Feed created. Knowledge Catalog will now publish aspect updates to Pub/Sub.")
            print(result)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        if "ALREADY_EXISTS" in error_msg:
            print("The Metadata Feed already exists! You are good to go.")
        else:
            print(f"Failed to create feed. HTTP {e.code}: {error_msg}")

if __name__ == "__main__":
    setup_feed()
