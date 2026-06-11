#!/bin/bash
PROJECT_ID=${GCP_PROJECT:-"telco-kc"}
REGION="us-central1"
DATASET_ID="raw_telco_data"
BUCKET_NAME="${PROJECT_ID}-unstructured-data"

echo "1. Creating Vertex AI Connection 'gemini-conn' in BigQuery..."
bq mk --connection --location=$REGION --project_id=$PROJECT_ID --connection_type=CLOUD_RESOURCE gemini-conn 2>/dev/null || true

echo "2. Retrieving Service Account for the connection..."
# Using python to reliably parse JSON output
SA_EMAIL=$(bq show --format=json --connection ${PROJECT_ID}.${REGION}.gemini-conn | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('cloudResource', {}).get('serviceAccountId', ''))")

if [ -z "$SA_EMAIL" ]; then
    echo "Error: Could not retrieve service account email for the connection."
    exit 1
fi
echo "Service Account: $SA_EMAIL"

echo "3. Granting Vertex AI User role to the Service Account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user" > /dev/null

echo "4. Creating Object Table 'support_transcripts'..."
bq query --use_legacy_sql=false \
"CREATE EXTERNAL TABLE IF NOT EXISTS \`${PROJECT_ID}.${DATASET_ID}.support_transcripts\`
WITH CONNECTION \`${PROJECT_ID}.${REGION}.gemini-conn\`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://${BUCKET_NAME}/transcripts/*']
);"

echo "5. Creating Object Table 'network_manuals'..."
bq query --use_legacy_sql=false \
"CREATE EXTERNAL TABLE IF NOT EXISTS \`${PROJECT_ID}.${DATASET_ID}.network_manuals\`
WITH CONNECTION \`${PROJECT_ID}.${REGION}.gemini-conn\`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://${BUCKET_NAME}/manuals/*']
);"

echo ""
echo "Setup Complete! The Vertex AI connection and Object Tables are ready for ML."
