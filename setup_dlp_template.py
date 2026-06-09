import os
from google.cloud import dlp_v2

PROJECT_ID = 'telco-kc'
REGION = 'us-central1'
TEMPLATE_ID = 'mask-ip-template'

os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = PROJECT_ID

dlp_client = dlp_v2.DlpServiceClient()
parent = f"projects/{PROJECT_ID}/locations/{REGION}"

def create_deidentify_template():
    # Define the template configuration
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "info_types": [{"name": "IP_ADDRESS"}, {"name": "PHONE_NUMBER"}],
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

    template = {
        "display_name": "Mask IPs and Phones",
        "description": "Template to mask IP addresses and Phone numbers for BQ Remote Function",
        "deidentify_config": deidentify_config,
    }

    try:
        response = dlp_client.create_deidentify_template(
            request={
                "parent": parent,
                "deidentify_template": template,
                "template_id": TEMPLATE_ID,
            }
        )
        print(f"Successfully created DLP Template: {response.name}")
    except Exception as e:
        if "Already exists" in str(e) or "409" in str(e):
            print(f"Template {TEMPLATE_ID} already exists.")
        else:
            print(f"Error creating template: {e}")

if __name__ == "__main__":
    create_deidentify_template()
