# Dataplex Data Governance & Metadata Guide

This guide outlines the data governance structure, manual metadata mappings, recommended Data Quality rules, and Data Product topologies for the ADC Telco environment.

## 1. Metadata Mapping (Aspects & Glossary)

*Attach Aspects via Knowledge Catalog > Entries > Attach Aspect.*
*Attach Glossary Terms via Knowledge Catalog > Entries > Schema Tab > Attach Glossary Term.*

### Core Tables
| BigQuery Table | Custom Aspect Type to Attach | Data to enter in UI | Glossary Terms (Column Level) |
| :--- | :--- | :--- | :--- |
| **`customer_data`** | `data-owner` | `customer-support@acme.com` | `plan_type` -> **Premium Customer Impact Count** |
| | `contains-pii` | `True` | |
| **`pm_data_secured`** | `data-owner` | `network-engineering@acme.com` | `latency_ms` -> **High Latency Ratio (%)** |
| | `contains-pii` | `False` | `packet_drop_rate_percent` -> **Avg Packet Drop Rate (%)** <br> `traffic_volume_gb` -> **Total Traffic Volume (TB)** |
| **`am_data`** | `data-owner` | `network-engineering@acme.com` | `severity` -> **Critical Alarm Count** |
| | `contains-pii` | `True` | |
| **`am_data_streaming`**| `data-owner` | `network-engineering@acme.com` | `severity` -> **Critical Alarm Count** |
| | `contains-pii` | `True` | |

### Aggregated / Unified Views
| BigQuery Table | Custom Aspect Type to Attach | Data to enter in UI | Glossary Terms (Column Level) |
| :--- | :--- | :--- | :--- |
| **`premium_5g_main`** | `data-owner` | `vip-support@acme.com` | Inherits from underlying columns |
| | `contains-pii` | `True` | |
| **`unified_main`** | `data-owner` | `data-platform-team@acme.com` | Inherits from underlying columns |
| | `contains-pii` | `True` | |

---

## 2. Architecture Recommendation: AM Streaming Data

**Should `am_data_streaming` be added to the Main table?**
* **Yes, but via a View or Materialized View.** The Main table is typically a large historical repository. Injecting high-velocity streaming alarm data directly into a static batch table can cause performance and cost issues. 
* **Best Practice**: Create the Main table as a **BigQuery View** (or Materialized View) that performs a `UNION ALL` between the historical `am_data` table and the real-time `am_data_streaming` table. This ensures the Conversational Agent can instantly query the latest network alarms alongside historical trends without degrading database performance.

---

## 3. Recommended Data Quality Rules (AutoDQ)

Dataplex AutoDQ now supports advanced reusability and machine learning features. We recommend showcasing these capabilities in your demo:

### A. Rule Templates & Glossary-Based Association (Highlight Feature)
Instead of creating isolated rules for each table, build **Rule Templates** and associate them directly with your Business Glossary terms. Any column tagged with that term automatically inherits the rule!
*(Note: Dataplex Rule Templates use SQL expressions that must return the **invalid** rows. Use the `${data()}` and `${column()}` variables.)*

* **Template 1: `valid_imsi_format`**
  * **SQL Expression**: `SELECT * FROM ${data()} WHERE NOT REGEXP_CONTAINS(CAST(${column()} AS STRING), r'^[0-9]{15}$')`
  * *Associate with Glossary Term: **IMSI***
* **Template 2: `valid_latency_range`**
  * **SQL Expression**: `SELECT * FROM ${data()} WHERE NOT(${column()} >= 0 AND ${column()} <= 10000)`
  * *Associate with Glossary Term: **High Latency Ratio (%)***
* **Template 3: `valid_packet_drop`**
  * **SQL Expression**: `SELECT * FROM ${data()} WHERE NOT(${column()} >= 0 AND ${column()} <= 10)`
  * *Associate with Glossary Term: **Average Packet Drop Rate (%)***
> **Demo Value**: Show how tagging the `latency_ms` column in the `premium_5g_main` table with the glossary term automatically secures it with the underlying DQ rule without manual mapping.



### B. Machine Learning Anomaly Detection (Highlight Feature)
Dataplex AutoDQ can automatically learn the normal behavior of your data to detect hidden issues without static thresholds.
* **Volume Anomaly Detection on `am_data_streaming`**: Enable this to automatically detect sudden, abnormal spikes or drops in network alarms (e.g., a massive fiber cut causing an explosion of critical alarms).
* **Freshness Anomaly Detection on `premium_5g_main`**: Detect if the real-time data pipeline for VIP customers silently stalls or lags outside of historical norms.

### C. Standard Table-Level Rules
* **Uniqueness**: The combination of `customer_id` + `timestamp` must be **UNIQUE** on the `unified_main` table.
* **Completeness**: `msisdn` must **NOT BE NULL** on the `premium_5g_main` table (100% completeness required to identify affected VIP users).
* **Value Set**: `plan_type` MUST EQUAL `Premium 5G` on the `premium_5g_main` table.

---

## 4. Recommended Data Products

To package this data logically in Dataplex Knowledge Catalog, we recommend creating the following **Data Products**:

### Data Product 1: `VIP Network Assurance`
* **Target Audience**: Premium Support Team, Executive Dashboarding.
* **Included Assets**: `premium_5g_main`, `am_data_streaming`.
* **Business Use Case**: Real-time SLA monitoring, proactive VIP customer outreach during network outages.

### Data Product 2: `Core Telemetry & Diagnostics`
* **Target Audience**: Network Engineering, Capacity Planning.
* **Included Assets**: `unified_main`, `pm_data_secured`, `am_data`.
* **Business Use Case**: Historical trend analysis, capacity planning, anomaly detection models.

## 5. Conversational Analytics with BigQuery Data Agent

Try asking the Data Agent these prompts on your `main` table (which is the joined result of PM, AM, and Customer data):

1. **The KPI Aggregation Prompt**
   > *"What is the average packet drop rate and high latency ratio across all network nodes over the last 7 days?"*
   * **The Magic**: The Agent doesn't just look for literal columns. It looks up "Average Packet Drop Rate" and "High Latency Ratio" in your Dataplex Business Glossary, finds the mapped physical calculations (`packet_drop_rate_percent` and `latency_ms`), and generates the correct SQL aggregation automatically.

2. **The Metric Correlation Prompt**
   > *"Which top 5 network nodes had the highest critical alarm count yesterday, and what was their total traffic volume (TB)?"*
   * **The Magic**: It automatically translates your business KPIs ("Critical Alarm Count", "Total Traffic Volume (TB)") into the physical schema logic (`COUNTIF(severity = 'CRITICAL')` and `SUM(traffic_volume_gb) / 1024`) to generate the complex `GROUP BY` and `ORDER BY DESC` SQL.

3. **The Business Impact Prompt**
   > *"Show me the premium customer impact count for the node 'AMF-01'."*
   * **The Magic**: "Premium Customer Impact Count" is a complex business metric. The agent uses the rich Glossary definition to understand that it needs to filter `plan_type = 'Premium 5G'` and count the distinct `affected_imsi`, abstracting the technical details away from the user!

4. **The "Out-of-Bounds" Clarification Prompt**
   > *"What is the average revenue lost due to network outages on node AMF-01?"*
   * **The Magic**: The Agent will pause and ask for clarification! Because "revenue" or "financial loss" does not exist in the physical schema (`am_data`, `pm_data`, `customer_data`) and is not defined in the Business Glossary, the Agent safely refuses to hallucinate data. It will ask you how to calculate revenue or prompt you to join a billing table.
