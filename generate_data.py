import csv
import json
import random
from datetime import datetime, timedelta
import os

# Create data directory
os.makedirs('data', exist_ok=True)

nodes = {
    'AMF-01': '10.240.1.15',
    'AMF-02': '10.240.1.16',
    'SMF-01': '10.240.2.10',
    'UPF-01': '10.240.3.5',
    'UPF-02': '10.240.3.6'
}

def generate_imsi():
    return f"310150{random.randint(100000000, 999999999)}"

def generate_msisdn():
    return f"+1{random.randint(2000000000, 9999999999)}"

# 1. Generate PM Data (Structured - CSV)
print("Generating PM Data...")
pm_data = []
start_time = datetime.now() - timedelta(days=2)
current_time = start_time

while current_time < datetime.now():
    for node_id, ip in nodes.items():
        # Normal behavior
        latency = random.uniform(10.0, 20.0)
        packet_drop = random.uniform(0.0, 0.1)
        
        # Simulate spike in AMF-01 roughly 24 hours ago
        if node_id == 'AMF-01' and (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 80000:
            latency = random.uniform(80.0, 150.0)
            packet_drop = random.uniform(2.0, 5.0)

        pm_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': node_id,
            'node_ip': ip,
            'latency_ms': round(latency, 2),
            'packet_drop_rate_percent': round(packet_drop, 2),
            'traffic_volume_gb': round(random.uniform(50.0, 200.0), 2)
        })
    current_time += timedelta(minutes=15)

with open('data/pm_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'node_id', 'node_ip', 'latency_ms', 'packet_drop_rate_percent', 'traffic_volume_gb'])
    writer.writeheader()
    writer.writerows(pm_data)


# 2. Generate AM Data (Semi-Structured - JSONL)
print("Generating AM Data...")
am_data = []
current_time = start_time
error_codes = ['ERR-001', 'ERR-002', 'ERR-5G-CORE-099']

while current_time < datetime.now():
    node_id = random.choice(list(nodes.keys()))
    # Random regular alarms
    if random.random() < 0.1:
        am_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': node_id,
            'node_ip': nodes[node_id],
            'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
            'severity': random.choice(['MINOR', 'WARNING']),
            'description': f'Routine node sync issue affecting subscriber {generate_imsi()}',
            'error_code': random.choice(['ERR-001', 'ERR-002']),
            'affected_msisdn': generate_msisdn() if random.random() < 0.5 else None
        })
    
    # Critical alarms for AMF-01 during the spike
    if (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 80000:
        if random.random() < 0.5:
             am_data.append({
                'timestamp': current_time.isoformat(),
                'node_id': 'AMF-01',
                'node_ip': nodes['AMF-01'],
                'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
                'severity': 'CRITICAL',
                'description': f'High latency and packet drop detected in control plane signaling for UE {generate_imsi()}',
                'error_code': 'ERR-5G-CORE-099',
                'affected_msisdn': generate_msisdn()
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
