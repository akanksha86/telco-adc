import csv
import json
import random
import uuid
from datetime import datetime, timedelta
import os

# Create data directory
os.makedirs('data', exist_ok=True)

# Expand nodes to increase volume
nodes = {f"AMF-{i:02d}": f"10.240.1.{i+10}" for i in range(1, 6)}
nodes.update({f"SMF-{i:02d}": f"10.240.2.{i+10}" for i in range(1, 6)})
nodes.update({f"UPF-{i:02d}": f"10.240.3.{i+10}" for i in range(1, 11)})

# Generate a pool of 1000 customers
print("Generating Customer Data (CII)...")
customers = []
first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
plans = ['Premium 5G', 'Standard 5G', 'Prepaid Data']

for i in range(1000):
    customers.append({
        'customer_id': str(uuid.uuid4()),
        'imsi': f"310150{random.randint(100000000, 999999999)}",
        'msisdn': f"+1{random.randint(2000000000, 9999999999)}",
        'first_name': random.choice(first_names),
        'last_name': random.choice(last_names),
        'email': f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}{random.randint(1,99)}@example.com",
        'plan_type': random.choice(plans),
        'active_status': 'ACTIVE'
    })

with open('data/customer_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['customer_id', 'imsi', 'msisdn', 'first_name', 'last_name', 'email', 'plan_type', 'active_status'])
    writer.writeheader()
    writer.writerows(customers)

# 1. Generate PM Data (Structured - CSV) - 7 Days
print("Generating PM Data (High Volume)...")
pm_data = []
start_time = datetime.now() - timedelta(days=7)
current_time = start_time

while current_time < datetime.now():
    for node_id, ip in nodes.items():
        latency = random.uniform(5.0, 15.0)
        packet_drop = random.uniform(0.0, 0.05)
        
        # Simulate spike in AMF-01 over the last 24 hours
        if node_id == 'AMF-01' and (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 40000:
            latency = random.uniform(80.0, 200.0)
            packet_drop = random.uniform(2.0, 8.0)

        pm_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': node_id,
            'node_ip': ip,
            'latency_ms': round(latency, 2),
            'packet_drop_rate_percent': round(packet_drop, 2),
            'traffic_volume_gb': round(random.uniform(50.0, 250.0), 2)
        })
    current_time += timedelta(minutes=5) # 5 min intervals for higher volume

with open('data/pm_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'node_id', 'node_ip', 'latency_ms', 'packet_drop_rate_percent', 'traffic_volume_gb'])
    writer.writeheader()
    writer.writerows(pm_data)

# 2. Generate AM Data (Semi-Structured - JSONL)
print("Generating AM Data...")
am_data = []
current_time = start_time

while current_time < datetime.now():
    node_id = random.choice(list(nodes.keys()))
    if random.random() < 0.2:
        customer = random.choice(customers)
        am_data.append({
            'timestamp': current_time.isoformat(),
            'node_id': node_id,
            'node_ip': nodes[node_id],
            'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
            'severity': random.choice(['MINOR', 'WARNING']),
            'description': f'Routine node sync issue affecting subscriber {customer["imsi"]}',
            'error_code': random.choice(['ERR-001', 'ERR-002']),
            'affected_imsi': customer['imsi'],
            'affected_msisdn': customer['msisdn']
        })
    
    # Critical alarms for AMF-01
    if (datetime.now() - current_time).total_seconds() < 86400 and (datetime.now() - current_time).total_seconds() > 40000:
        if random.random() < 0.6:
             customer = random.choice(customers)
             am_data.append({
                'timestamp': current_time.isoformat(),
                'node_id': 'AMF-01',
                'node_ip': nodes['AMF-01'],
                'alarm_id': f'ALARM-{random.randint(1000, 9999)}',
                'severity': 'CRITICAL',
                'description': f'High latency and packet drop detected in control plane signaling for UE {customer["imsi"]}',
                'error_code': 'ERR-5G-CORE-099',
                'affected_imsi': customer['imsi'],
                'affected_msisdn': customer['msisdn']
            })

    current_time += timedelta(minutes=15)

with open('data/am_data.jsonl', 'w') as f:
    for record in am_data:
        f.write(json.dumps(record) + '\n')

print("Data generation complete. Customer, PM, and AM data saved.")


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
