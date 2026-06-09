import csv
import json
import random
from datetime import datetime, timedelta
import os

# Create data directory
os.makedirs('data', exist_ok=True)

nodes = ['AMF-01', 'AMF-02', 'SMF-01', 'UPF-01', 'UPF-02']

# 1. Generate PM Data (Structured - CSV)
print("Generating PM Data...")
pm_data = []
start_time = datetime.now() - timedelta(days=2)
current_time = start_time

while current_time < datetime.now():
    for node in nodes:
        # Normal behavior
        latency = random.uniform(10.0, 20.0)
        packet_drop = random.uniform(0.0, 0.1)
        
        # Simulate spike in AMF-01 roughly 24 hours ago
        if node == 'AMF-01' and (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 80000:
            latency = random.uniform(80.0, 150.0)
            packet_drop = random.uniform(2.0, 5.0)

        pm_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': node,
            'latency_ms': round(latency, 2),
            'packet_drop_rate_percent': round(packet_drop, 2),
            'traffic_volume_gb': round(random.uniform(50.0, 200.0), 2)
        })
    current_time += timedelta(minutes=15)

with open('data/pm_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'node_id', 'latency_ms', 'packet_drop_rate_percent', 'traffic_volume_gb'])
    writer.writeheader()
    writer.writerows(pm_data)


# 2. Generate AM Data (Semi-Structured - JSONL)
print("Generating AM Data...")
am_data = []
current_time = start_time
error_codes = ['ERR-001', 'ERR-002', 'ERR-5G-CORE-099']

while current_time < datetime.now():
    # Random regular alarms
    if random.random() < 0.1:
        am_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': random.choice(nodes),
            'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
            'severity': random.choice(['MINOR', 'WARNING']),
            'description': 'Routine node sync issue',
            'error_code': random.choice(['ERR-001', 'ERR-002'])
        })
    
    # Critical alarms for AMF-01 during the spike
    if (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 80000:
        if random.random() < 0.5:
             am_data.append({
                'timestamp': current_time.isoformat(),
                'node_id': 'AMF-01',
                'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
                'severity': 'CRITICAL',
                'description': 'High latency and packet drop detected in control plane signaling.',
                'error_code': 'ERR-5G-CORE-099'
            })

    current_time += timedelta(minutes=30)

with open('data/am_data.jsonl', 'w') as f:
    for record in am_data:
        f.write(json.dumps(record) + '\n')


# 3. Generate Unstructured Data (Markdown Manual)
print("Generating Unstructured Data...")
manual_content = """# Ericsson 5G Core Network Troubleshooting Manual v4.2

## Section 1: Overview
This document provides troubleshooting steps for the Ericsson 5G Core Network nodes including AMF, SMF, and UPF.

## Section 2: Error Codes and Remediation

### ERR-001: Minor Sync Issue
* **Description:** Temporary synchronization loss between nodes.
* **Remediation:** No action required. Node will auto-recover within 5 minutes.

### ERR-002: Link Degradation Warning
* **Description:** Optical link degradation detected.
* **Remediation:** Schedule maintenance to inspect physical connections.

### ERR-5G-CORE-099: Critical Control Plane Latency
* **Description:** Severe latency and packet drops in the Access and Mobility Management Function (AMF) signaling plane. Usually caused by misconfigured flow control parameters under high load.
* **Remediation:** 
    1. Isolate the affected AMF node.
    2. Access the node configuration terminal.
    3. Update the parameter `flow_control_window_size` from default (1024) to 4096.
    4. Restart the `amf-signaling` service.
    5. Monitor PM data for 15 minutes to confirm latency returns to < 20ms.

## Section 3: PII and Security Guidelines
Remember to always mask Customer Identifiable Information (CII) such as IMSI, MSISDN, and node IP addresses before exporting any logs from the secure exploration zone.
"""

with open('data/Ericsson_Core_Network_Manual_v4.2.md', 'w') as f:
    f.write(manual_content)

print("Data generation complete. Files saved in 'data' directory.")
