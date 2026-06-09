import os
import functions_framework
from google.cloud import dlp_v2
from flask import jsonify

os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = os.environ.get('GCP_PROJECT', 'telco-kc')

PROJECT_ID = os.environ.get('GCP_PROJECT', 'telco-kc')
REGION = 'us-central1'
TEMPLATE_ID = 'mask-ip-template'

dlp_client = dlp_v2.DlpServiceClient()
parent = f"projects/{PROJECT_ID}/locations/{REGION}"
template_name = f"{parent}/deidentifyTemplates/{TEMPLATE_ID}"

@functions_framework.http
def dlp_proxy(request):
    """
    BigQuery Remote Function endpoint.
    Expects JSON body: {"calls": [["string_to_mask"], ["another_string"]]}
    Returns JSON body: {"replies": ["masked_string", "another_masked_string"]}
    """
    request_json = request.get_json(silent=True)
    if not request_json or 'calls' not in request_json:
        return jsonify({"errorMessage": "Invalid request format. 'calls' array is missing."}), 400

    calls = request_json['calls']
    
    inspect_config = {
        "info_types": [{"name": "IP_ADDRESS"}, {"name": "PHONE_NUMBER"}],
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

    # Process in chunks to avoid "Too many findings" error from DLP API
    CHUNK_SIZE = 200
    all_replies = []
    
    try:
        for i in range(0, len(calls), CHUNK_SIZE):
            chunk = calls[i:i + CHUNK_SIZE]
            
            headers = [{"name": "text"}]
            rows = []
            
            for call in chunk:
                text = call[0] if call and len(call) > 0 and call[0] else ""
                rows.append({"values": [{"string_value": str(text)}]})
                
            item = {"table": {"headers": headers, "rows": rows}}
            
            response = dlp_client.deidentify_content(
                request={
                    "parent": parent,
                    "deidentify_config": deidentify_config,
                    "inspect_config": inspect_config,
                    "item": item,
                }
            )
            
            for row in response.item.table.rows:
                masked_val = row.values[0].string_value
                all_replies.append(masked_val if masked_val else None)
                
        return jsonify({"replies": all_replies})
        
    except Exception as e:
        # If any batch fails, return the error for all rows so BigQuery shows it
        return jsonify({"replies": [f"ERROR: {str(e)}" for _ in calls]})
