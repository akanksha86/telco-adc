# Agentic Data Cloud: Telco Demo

This repository contains the setup and ingestion scripts for the **Agentic Data Cloud Telco Demo**, which showcases how Google Cloud's Data Engineering Agent (Gemini in BigQuery) can securely manage, analyze, and stream telecommunications data.

## Features & Scripts

1. **`generate_data.py`**
   - Generates synthetic Telco data including Performance Management (PM) metrics, Fault Management (AM) alarms (JSONL), and Customer Information (CII).
   - Simulates realistic anomalies like latency spikes and packet drops on specific 5G Core nodes (e.g., AMF-01).

2. **`agentic_ingestion.py`**
   - A Python ingestion pipeline that securely loads the generated data into BigQuery (`telco-kc.raw_telco_data`).
   - Demonstrates **in-flight masking** by using the Cloud DLP API to dynamically de-identify sensitive PII (IPs, IMSIs, MSISDNs) from unstructured/semi-structured fields before landing in BigQuery.

3. **`streaming_agent.py`**
   - A continuous streaming simulator that generates real-time 5G Core network alarms and streams them directly into the `am_data_streaming` BigQuery table using the Storage Write API.

4. **`setup_dlp_template.py`**
   - Programmatically creates a Cloud DLP De-identify template (`mask-ip-template`) used for BigQuery Active Scanning and Remote Functions.

5. **`dlp_proxy_function/` & `deploy_function.sh`**
   - A Google Cloud Function that acts as a proxy for BigQuery Remote Functions.
   - Allows BigQuery SQL to seamlessly call Cloud DLP to mask specific columns natively within a SQL query.
   - Includes automatic batching/chunking to optimize performance and adhere to API limits.

6. **`upload_unstructured_to_gcs.sh` & `setup_vertex_ai_bq.sh`**
   - Helper scripts to upload unstructured PDFs/Transcripts to Cloud Storage and automatically create the necessary BigQuery Object Tables and Vertex AI connections (`gemini-conn`) for multi-modal analysis.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Synthetic Data:**
   ```bash
   python3 generate_data.py
   ```

3. **Run Batch Ingestion:**
   ```bash
   python3 agentic_ingestion.py
   ```

4. **Start the Streaming Agent:**
   ```bash
   python3 streaming_agent.py
   ```

5. **Deploy the DLP Proxy (For BigQuery Remote Functions):**
   ```bash
   ./deploy_function.sh
   ```

6. **Setup Unstructured Data & AI Connections:**
   ```bash
   ./upload_unstructured_to_gcs.sh
   ./setup_vertex_ai_bq.sh
   ```

*See `Demo_Walkthrough.md` (Artifact) for the exact Data Engineering Agent prompts and BigQuery configurations used during the live demonstration.*
