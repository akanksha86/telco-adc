# Dataplex Metadata Mapping Guide

This guide outlines the manual mappings required in the Dataplex Knowledge Catalog UI to link the custom Aspect Types and Business Glossary terms created for the Telco demo.

## 1. Attaching Aspects (Table Level)
*Navigate to Knowledge Catalog > Entries, search for the tables below, select them, and use the "Attach Aspect" button on the top right of the table entry page.*

| BigQuery Table | Custom Aspect Type to Attach | Data to enter in UI |
| :--- | :--- | :--- |
| **`customer_data`** | `data-owner` | **Owner Name**: `customer-support@acme.com` |
| | `contains-pii` | **Has PII**: `True` |
| **`pm_data`** | `data-owner` | **Owner Name**: `network-engineering@acme.com` |
| | `contains-pii` | **Has PII**: `False` |
| **`am_data`** | `data-owner` | **Owner Name**: `network-engineering@acme.com` |
| | `contains-pii` | **Has PII**: `True` |
| **`am_data_streaming`** | `data-owner` | **Owner Name**: `network-engineering@acme.com` |
| | `contains-pii` | **Has PII**: `True` |

---

## 2. Attaching Glossary Terms (Column Level)
*Inside each Table's entry view, go to the "Schema" tab. Hover over the specific column and click "Attach Glossary Term".*

| BigQuery Table | Target Column | Glossary Term to Attach |
| :--- | :--- | :--- |
| **`pm_data`** | `latency_ms` | **High Latency Ratio (%)** |
| | `packet_drop_rate_percent` | **Average Packet Drop Rate (%)** |
| | `traffic_volume_gb` | **Total Traffic Volume (TB)** |
| **`am_data`** | `severity` | **Critical Alarm Count** |
| **`am_data_streaming`** | `severity` | **Critical Alarm Count** |
| **`customer_data`** | `plan_type` | **Premium Customer Impact Count** |
