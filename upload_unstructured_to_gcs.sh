#!/bin/bash
PROJECT_ID=${GCP_PROJECT:-"telco-kc"}
REGION="us-central1"
BUCKET_NAME="${PROJECT_ID}-unstructured-data"

echo "Creating GCS Bucket: gs://$BUCKET_NAME..."
gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION --project=$PROJECT_ID 2>/dev/null || true

echo "Uploading Manuals to GCS..."
gcloud storage cp -r data/manuals/* gs://$BUCKET_NAME/manuals/

echo "Uploading Customer Transcripts to GCS..."
gcloud storage cp -r data/transcripts/* gs://$BUCKET_NAME/transcripts/

echo ""
echo "Upload complete! Your files are at: gs://$BUCKET_NAME/"
echo "You can now create an Object Table in BigQuery over this bucket."
