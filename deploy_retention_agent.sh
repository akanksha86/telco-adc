#!/bin/bash
PROJECT_ID="telco-kc"
REGION="us-central1"
TOPIC_NAME="dataplex-metadata-changes"

echo "1. Ensuring Pub/Sub topic exists for Dataplex Metadata Change Feeds..."
gcloud pubsub topics create $TOPIC_NAME --project=$PROJECT_ID 2>/dev/null || true

echo "2. Deploying the Retention Agent Cloud Function..."
cd retention_agent_function

gcloud functions deploy retention_agent \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=process_metadata_change \
  --trigger-topic=$TOPIC_NAME \
  --project=$PROJECT_ID

echo ""
echo "Deployment Complete! The Retention Agent is now listening to the $TOPIC_NAME topic."
echo "Whenever a 'Retention Policy' Aspect is updated in Knowledge Catalog, this agent will automatically enforce it in BigQuery."
