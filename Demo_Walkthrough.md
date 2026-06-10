# Agentic Data Cloud Demo Walkthrough

## Step 1: Agentic Ingestion (Hybrid to Cloud)
Run the ingestion script. This will use the Python agent to read the hybrid AM data and mask it in-flight, while uploading the PM data completely **RAW** so we can demo native BigQuery Active Scanning later.

```bash
python3 agentic_ingestion.py
```

## Step 2: Setting up BigQuery DLP Remote Function Architecture

BigQuery Remote Functions require a proxy (like Cloud Functions or Cloud Run) to parse the BigQuery request schema and pass it to the DLP API.

1. **Create the DLP Template**: Run the setup script to create the DLP De-identify Template in `us-central1`.
```bash
python3 setup_dlp_template.py
```

2. **Deploy the Cloud Function Proxy**: We've included a Python script that acts as the proxy. Deploy it using the provided shell script:
```bash
chmod +x deploy_function.sh
./deploy_function.sh
```
*(Once deployed, copy the HTTPS Trigger URL from the terminal output)*

3. **Create the BigQuery Connection**: In your terminal, create a Cloud Resource connection for BigQuery to call the function:
```bash
bq mk --connection --location=us-central1 --project_id=telco-kc --connection_type=CLOUD_RESOURCE dlp-conn
```

4. **Grant IAM Permissions**: Get the Service Account ID of the connection you just created:
```bash
bq show --connection telco-kc.us-central1.dlp-conn
```
*(Copy the `serviceAccountId` from the output and run the following commands, replacing `<SERVICE_ACCOUNT_EMAIL>`)*
```bash
gcloud projects add-iam-policy-binding telco-kc \
  --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" \
  --role="roles/dlp.user"

gcloud run services add-iam-policy-binding dlp-proxy \
  --region=us-central1 \
  --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" \
  --role="roles/run.invoker" \
  --project=telco-kc
```

4. **Get the Cloud Function URL**: Run this to get your Cloud Function's Endpoint URL:
```bash
gcloud functions describe dlp_proxy --region us-central1 --format="value(serviceConfig.uri)"
```

## Step 3: Demoing with the Data Engineering Agent

Now, open **BigQuery Studio** in the Google Cloud Console.

### Phase 3A: Active Scanning (Remote Function)
Open the **Data Engineering Agent (Gemini)** pane and use the following prompt (replace `<YOUR_CLOUD_FUNCTION_URL>` with the URL from Step 2):

> *"Write a SQL script to create a BigQuery remote function named `mask_ip` in the `raw_telco_data` dataset. It should use the connection `telco-kc.us-central1.dlp-conn` and the endpoint `<YOUR_CLOUD_FUNCTION_URL>`. Then, use this function to select all data from `pm_data`, masking the `node_ip` column, and save the result into a new table called `pm_data_secured`."*

Gemini will generate the `CREATE OR REPLACE FUNCTION` and the `CREATE TABLE AS SELECT` statements, automatically routing the data through your Cloud Function proxy for DLP masking!

### Phase 3B: Conversational Correlation & Proactive Outreach
Now that all data is in BigQuery (including the new Customer table), use the Data Engineering Agent to synthesize the silos and identify high-value impact:

> *"Join `pm_data_secured`, `am_data`, and `customer_data`. Find all 'Premium 5G' customers who were affected by 'CRITICAL' latency alarms on node 'AMF-01' over the last 48 hours. I need their first names and emails so we can proactively send them an apology credit, but make sure to exclude their raw IMSI/MSISDN in the final output to maintain compliance."*

Gemini will automatically generate the complex multi-table `JOIN` logic, filtering by the Premium plan, and omitting the restricted PII identifiers as requested.

### Phase 3C: Real-time Streaming Insights
To showcase real-time Agentic capabilities, start the streaming simulator in your local terminal:
```bash
python3 streaming_agent.py
```
*(Leave this running in the background)*

Then, back in BigQuery Studio, ask the Agent:
> *"Query the `am_data_streaming` table to show me a live count of alarms fired in the last 5 minutes, grouped by severity."*

This demonstrates that the Data Engineering Agent can instantly interface with live, streaming tables using the BigQuery Storage Write API without waiting for batch pipelines.

## Step 4: BigQuery Notebooks, BQML & Unstructured AI

Now we bring in Unstructured Data (Network Troubleshooting Manuals and Customer Support Call Transcripts) and combine them with our structured metrics using the **Data Science Agent**!

1. **Upload Data & Automate Setup**: Run the two helper scripts to upload your unstructured data to Cloud Storage and automatically create the BigQuery Vertex AI Connection (`gemini-conn`) and the Object Table (`support_transcripts`):
```bash
./upload_unstructured_to_gcs.sh
./setup_vertex_ai_bq.sh
```

2. **Open BigQuery Notebooks**: In BigQuery Studio, click on **Notebooks** and create a new Python notebook. Open the **Data Science Agent (Gemini)** pane on the side.

3. **Train a BQML Model for Anomaly Detection**: Ask the Data Science Agent to generate code using BigQuery DataFrames (`bigframes`) to train an anomaly detection clustering model on your secure network metrics:
> *"Using BigQuery DataFrames (`bigframes`), write code to train a K-Means clustering model named `node_risk_clusters` on the `raw_telco_data.pm_data_secured` table. Cluster the nodes based on `latency_ms` and `packet_drop_rate_percent` using 3 clusters to identify high-risk nodes."*
*(Run the generated cell. This demonstrates how data scientists can build BQML models directly in Python without writing SQL!)*

4. **"What-If" Inference with BigFrames**: Let's see the model in action on synthetic edge-case data! Ask the Data Science Agent:
> *"Create a pandas DataFrame with 5 hypothetical network nodes. Make one of the nodes ('AMF-01') have extremely high `latency_ms` (150ms) and `packet_drop_rate_percent` (4.5%), and make the other 4 nodes have normal metrics (20ms latency, 0.1% packet drop). Convert this pandas DataFrame to a BigQuery DataFrame (`bigframes`), and then use the `node_risk_clusters` BQML K-Means model to predict the clusters for this new data. Display the results."*

5. **Cluster Explainability**: We can use generative AI to assign human-readable descriptions to our mathematical clusters. Ask the Agent:
> *"For the K-Means model created above `node_risk_clusters`, help create the description for the 3 clusters and append it to the results from running the prediction."*

6. **Multi-Modal Data Correlation**: This is the magic moment. We will use `ML.GENERATE_TEXT` with Gemini to extract the customer's phone number from the raw text transcript, and instantly join it with our structured PM/AM data!
In the notebook, ask the Data Science Agent:
> *"Write a SQL query using the `%%bigquery` magic command. Use `ML.GENERATE_TEXT` with the `gemini-pro` model and connection `gemini-conn` to extract the customer's MSISDN phone number from the `raw_telco_data.support_transcripts` object table text. Ensure you trim whitespace from the extracted string. Then, join that extracted MSISDN with `customer_data.msisdn` using the `ENDS_WITH` function (to account for missing country codes or '+' signs). Next, join `customer_data` to `am_data` on `imsi = affected_imsi`. Finally, join `am_data` to `pm_data_secured` on `node_id`. Return the customer name, the text snippet of their complaint, the alarm severity, and the node's latency."*

Gemini will generate a powerful multi-modal query right in your notebook that bridges the gap between angry customer calls and physical 5G antenna telemetry!

## Step 5: Automated Governance & Security (RBAC, RLS, CLS)

The final pillar of the Agentic Data Cloud is making security, compliance, and governance effortless.

1. **Active Metadata Governance (The Retention Agent)**:
In the Agentic Data Cloud, we don't write manual retention scripts. Instead, we use a **Retention Agent** connected to the Knowledge Catalog's **Metadata Change Feeds**.
* **Setup**: 
  First, grant the default compute service account the permissions needed to execute BigQuery DDL on behalf of the Cloud Function (replace `<PROJECT_ID>` and `<PROJECT_NUMBER>` accordingly, e.g. `telco-kc` and `568311752105`):
  ```bash
  gcloud projects add-iam-policy-binding <PROJECT_ID> \
      --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
      --role="roles/bigquery.admin"
  ```
  Then, deploy the agent using the included script:
  ```bash
  chmod +x deploy_retention_agent.sh
  ./deploy_retention_agent.sh
  ```
* **Demo**: In the Knowledge Catalog UI, find the `raw_telco_data.am_data_streaming` table and attach a Custom Aspect representing your Retention Policy (e.g., 7 days).
* **The Magic**: The moment you save the Aspect in the UI, Dataplex fires a Metadata Change Feed event to Pub/Sub. The Retention Agent Cloud Function intercepts this event, parses your declarative policy, and automatically translates it into the physical BigQuery DDL (`ALTER TABLE ... SET OPTIONS`) behind the scenes! Your Data Stewards never have to write SQL.

2. **Dataset & Table RBAC**:
> *"Write a SQL statement to grant the `roles/bigquery.dataViewer` role on the `raw_telco_data` dataset to the group `data-analysts@acme.com`. Then, grant the same role explicitly on the `pm_data_secured` table to `contractor@acme.com`."*

3. **Row-Level Security (RLS)**:
> *"Write a SQL statement to create a row access policy on the `customer_data` table named `filter_premium_customers`. It should grant access to `support-tier1@acme.com` but filter the rows so they can only see customers where `plan_type = 'Basic'`."*

4. **Column-Level Security (CLS)**:
*(Note: To execute this, you need to have a pre-existing taxonomy in Data Catalog. If you don't, you can just show the generated code!)*
> *"Write a SQL statement to alter the `customer_data` table and apply a Data Catalog policy tag (e.g., `projects/telco-kc/locations/us-central1/taxonomies/123/policyTags/456`) to the `imsi` column to restrict access to highly sensitive identifiers."*

By using the Agent, administrators don't need to memorize complex BigQuery DCL/DDL syntax—they just describe their compliance requirements in plain English!
