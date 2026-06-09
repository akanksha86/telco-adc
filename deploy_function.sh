#!/bin/bash
echo "Deploying DLP Proxy Cloud Function to telco-kc..."

cd dlp_proxy_function

gcloud functions deploy dlp_proxy \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=dlp_proxy \
  --trigger-http \
  --project=telco-kc

PROJECT_NUMBER=$(gcloud projects describe telco-kc --format="value(projectNumber)")

echo "Granting DLP and Service Usage permissions to Cloud Function service account..."
gcloud projects add-iam-policy-binding telco-kc \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/dlp.user" > /dev/null

gcloud projects add-iam-policy-binding telco-kc \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer" > /dev/null

echo ""
echo "Deployment initiated. Once complete, copy the HTTPS Trigger URL."
echo "You will use this URL as the 'endpoint' in your BigQuery CREATE FUNCTION statement."
