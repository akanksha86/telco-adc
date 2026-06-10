import json
import subprocess
import urllib.request
import urllib.error

def get_access_token():
    result = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    return result.stdout.strip()

def make_request(url, payload, token, method='POST'):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            return json.loads(result)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        if "ALREADY_EXISTS" in error_msg or "already exists" in error_msg.lower():
            print(f"Resource already exists at {url}")
            return None
        print(f"Failed to call {url}. HTTP {e.code}: {error_msg}")
        return None

def setup_glossary_and_aspect():
    token = get_access_token()
    if not token:
        print("Failed to get gcloud token.")
        return
        
    project_id = "telco-kc"
    location = "us-central1"
    
    # 1. Create Aspect Types (Simple Fields)
    # Aspect A: Data Owner (String)
    aspect_type_id_owner = "data-owner"
    print(f"Creating Aspect Type '{aspect_type_id_owner}'...")
    url_owner = f"https://dataplex.googleapis.com/v1/projects/{project_id}/locations/{location}/aspectTypes?aspectTypeId={aspect_type_id_owner}"
    payload_owner = {
        "displayName": "Data Owner",
        "description": "Simple string aspect indicating the team or email address responsible for this asset.",
        "metadataTemplate": {
            "name": "data_owner_template",
            "type": "RECORD",
            "recordFields": [
                {
                    "name": "owner_name",
                    "type": "STRING",
                    "index": 1,
                    "annotations": {
                        "display_name": "Owner Email/Team",
                        "description": "The team or email address."
                    }
                }
            ]
        }
    }
    make_request(url_owner, payload_owner, token)

    # Aspect B: Contains PII (Boolean)
    aspect_type_id_pii = "contains-pii"
    print(f"Creating Aspect Type '{aspect_type_id_pii}'...")
    url_pii = f"https://dataplex.googleapis.com/v1/projects/{project_id}/locations/{location}/aspectTypes?aspectTypeId={aspect_type_id_pii}"
    payload_pii = {
        "displayName": "Contains PII",
        "description": "Simple boolean aspect indicating if the asset contains Personally Identifiable Information.",
        "metadataTemplate": {
            "name": "contains_pii_template",
            "type": "RECORD",
            "recordFields": [
                {
                    "name": "has_pii",
                    "type": "STRING",
                    "index": 1,
                    "annotations": {
                        "display_name": "Has PII (True/False)",
                        "description": "True if the asset contains PII."
                    }
                }
            ]
        }
    }
    make_request(url_pii, payload_pii, token)

    # 2. Create Glossary
    glossary_id = "telco-business-glossary"
    print(f"\nCreating Business Glossary '{glossary_id}'...")
    url = f"https://dataplex.googleapis.com/v1/projects/{project_id}/locations/{location}/glossaries?glossaryId={glossary_id}"
    payload = {
        "displayName": "Telco Analytics Glossary",
        "description": "Glossary containing core definitions and calculations for the Telco dataset."
    }
    make_request(url, payload, token)

    # 3. Create Glossary Terms
    terms = [
        {
            "id": "high-latency-ratio",
            "displayName": "High Latency Ratio (%)",
            "description": "The percentage of network nodes experiencing latency above 50ms.\nCalculation: `(COUNTIF(latency_ms > 50) / COUNT(*)) * 100`"
        },
        {
            "id": "critical-alarm-count",
            "displayName": "Critical Alarm Count",
            "description": "Total number of network alarms with severity level 'CRITICAL' in a given time period.\nCalculation: `COUNTIF(severity = 'CRITICAL')`"
        },
        {
            "id": "average-packet-drop",
            "displayName": "Average Packet Drop Rate (%)",
            "description": "The mean packet drop rate across all active nodes.\nCalculation: `AVG(packet_drop_rate_percent)`"
        },
        {
            "id": "premium-customer-impact",
            "displayName": "Premium Customer Impact Count",
            "description": "Number of affected unique premium customers experiencing service degradation.\nCalculation: `COUNT(DISTINCT IF(plan_type = 'Premium 5G', affected_imsi, NULL))`"
        },
        {
            "id": "total-traffic-volume-tb",
            "displayName": "Total Traffic Volume (TB)",
            "description": "Total data traffic volume processed in Terabytes.\nCalculation: `SUM(traffic_volume_gb) / 1024`"
        }
    ]

    for term in terms:
        term_id = term["id"]
        print(f"Creating Glossary Term '{term_id}'...")
        url = f"https://dataplex.googleapis.com/v1/projects/{project_id}/locations/{location}/glossaries/{glossary_id}/terms?termId={term_id}"
        payload = {
            "parent": f"projects/{project_id}/locations/{location}/glossaries/{glossary_id}",
            "displayName": term["displayName"],
            "description": term["description"]
        }
        make_request(url, payload, token)
        
    print("\nGlossary and Aspect creation completed.")

if __name__ == "__main__":
    setup_glossary_and_aspect()
