# API Usage Examples

These examples work with both Docker and Local deployments. Use the appropriate base URL:
- **Docker (via NGINX)**: `http://localhost/api/`
- **Docker (direct) or Local**: `http://localhost:5000/api/`

Replace `localhost` with your server's IP or domain name for remote access.

## cURL Examples

### Upload a log file
```bash
# Docker (via NGINX)
curl -X POST http://localhost/api/logs/upload \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -F "file=@/path/to/your/logfile.adi"

# Local or Docker (direct)
curl -X POST http://localhost:5000/api/logs/upload \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -F "file=@/path/to/your/logfile.adi"
```

### Get your log statistics
```bash
curl -X GET http://localhost:5000/api/logs/stats \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

### Search logs by callsign
```bash
curl -X GET "http://localhost:5000/api/logs?callsign=W1ABC&page=1&per_page=50" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

### Export logs to ADIF file
```bash
# Export all logs
curl -X GET "http://localhost:5000/api/logs/export" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN" \
  --output my_logbook.adi

# Export filtered logs (20m SSB only)
curl -X GET "http://localhost:5000/api/logs/export?band=20m&mode=SSB" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN" \
  --output 20m_ssb.adi
```

## Python Examples

### Upload Log with Python
```python
import requests

# Base URL - adjust based on deployment
BASE_URL = "http://localhost:5000/api"  # Local or Docker direct
# BASE_URL = "http://localhost/api"  # Docker via NGINX

def upload_adif_log(api_key, file_path):
    """Upload an ADIF log file to LogShackBaby"""
    url = f"{BASE_URL}/logs/upload"
    headers = {"X-API-Key": api_key}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   Total: {data['total']}")
        print(f"   New: {data['new']}")
        print(f"   Duplicates: {data['duplicates']}")
    else:
        print(f"❌ Upload failed: {response.json().get('error')}")

# Usage
api_key = "your_api_key_here"
upload_adif_log(api_key, "my_log.adi")
```

### Get Log Statistics
```python
import requests

BASE_URL = "http://localhost:5000/api"

def get_log_stats(session_token):
    """Get statistics about your logs"""
    url = f"{BASE_URL}/logs/stats"
    headers = {"X-Session-Token": session_token}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total QSOs: {data['total_qsos']}")
        print(f"Unique Callsigns: {data['unique_callsigns']}")
        print(f"Bands: {', '.join(data['bands'].keys())}")
        print(f"Modes: {', '.join(data['modes'].keys())}")
    else:
        print("Failed to get stats")

# Usage
session_token = "your_session_token"
get_log_stats(session_token)
```

### Retrieve Logs with Additional ADIF Fields
```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

def get_logs_with_details(session_token, page=1, per_page=10):
    """Get logs including all additional ADIF fields"""
    url = f"{BASE_URL}/logs?page={page}&per_page={per_page}"
    headers = {"X-Session-Token": session_token}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        for log in data['logs']:
            print(f"\nQSO: {log['call']} on {log['band']} {log['mode']}")
            
            # Show additional fields if present
            if log.get('additional_fields'):
                print(f"  Additional fields: {len(log['additional_fields'])} found")
                for field, value in log['additional_fields'].items():
                    print(f"    {field.upper()}: {value}")
    else:
        print("Failed to get logs")

# Usage
get_logs_with_details("your_session_token")
```

### Retrieve Logs with Additional ADIF Fields
```python
import requests
import json

def get_logs_with_details(session_token, page=1, per_page=10):
    """Get logs including all additional ADIF fields"""
    url = f"http://localhost/api/logs?page={page}&per_page={per_page}"
    headers = {"X-Session-Token": session_token}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        for log in data['logs']:
            print(f"\nQSO: {log['call']} on {log['band']} {log['mode']}")
            
            # Show additional fields if present
            if log.get('additional_fields'):
                print(f"  Additional fields: {len(log['additional_fields'])} found")
                for field, value in log['additional_fields'].items():
                    print(f"    {field.upper()}: {value}")
    else:
        print("Failed to get logs")

# Usage
get_logs_with_details("your_session_token")
```

### Login and Get Session Token
```python
import requests

def login(callsign, password):
    """Login and get session token"""
    url = "http://localhost/api/login"
    data = {
        "callsign": callsign,
        "password": password
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        data = response.json()
        return data['session_token']
    else:
        print(f"Login failed: {response.json().get('error')}")
        return None

# Usage
session_token = login("W1ABC", "your_password")
print(f"Session token: {session_token}")
```

### Search Logs
```python
import requests

def search_logs(session_token, callsign=None, band=None, mode=None, page=1):
    """Search logs with filters"""
    url = "http://localhost/api/logs"
    headers = {"X-Session-Token": session_token}
    params = {"page": page, "per_page": 50}
    
    if callsign:
        params['callsign'] = callsign
    if band:
        params['band'] = band
    if mode:
        params['mode'] = mode
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} matching QSOs")
        for log in data['logs']:
            print(f"{log['qso_date']} {log['time_on']} - {log['call']} on {log['band']} {log['mode']}")
    else:
        print("Search failed")

# Usage
search_logs(session_token, callsign="W1", band="20m")
```

### Export Logs to ADIF
```python
import requests

def export_logs(session_token, filename="my_logbook.adi", callsign=None, band=None, mode=None):
    """Export logs to ADIF file"""
    url = "http://localhost/api/logs/export"
    headers = {"X-Session-Token": session_token}
    params = {}
    
    if callsign:
        params['callsign'] = callsign
    if band:
        params['band'] = band
    if mode:
        params['mode'] = mode
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        with open(filename, 'w') as f:
            f.write(response.text)
        print(f"✅ Exported to {filename}")
        return True
    else:
        print(f"❌ Export failed: {response.status_code}")
        return False

# Usage examples
# Export all logs
export_logs(session_token, "all_logs.adi")

# Export only 20m contacts
export_logs(session_token, "20m_contacts.adi", band="20m")

# Export SSB contacts with specific callsign
export_logs(session_token, "w1abc_ssb.adi", callsign="W1ABC", mode="SSB")
```

## Bash Script for Automatic Upload

Save this as `upload_logs.sh`:

```bash
#!/bin/bash

API_KEY="your_api_key_here"
API_URL="http://localhost/api/logs/upload"
LOG_DIR="/path/to/your/logs"

# Upload all ADIF files in directory
for file in "$LOG_DIR"/*.adi "$LOG_DIR"/*.adif; do
    if [ -f "$file" ]; then
        echo "Uploading $file..."
        curl -X POST "$API_URL" \
          -H "X-API-Key: $API_KEY" \
          -F "file=@$file" \
          -s | jq '.'
        echo ""
    fi
done

echo "Upload complete!"
```

Make it executable:
```bash
chmod +x upload_logs.sh
./upload_logs.sh
```

## Integration with Logging Software

### N1MM Logger+
1. Export log: File → ADIF/Cabrillo → Export ADIF
2. Use the Python script or cURL to upload the exported file
3. Set up a scheduled task to upload daily

### Logger32
1. Export: File → Export → ADIF
2. Upload using the provided scripts

### Ham Radio Deluxe
1. Logbook → Export → ADIF Format
2. Upload to LogShackBaby

### WSJT-X / JTDX
1. Find the wsjtx_log.adi file in your log directory
2. Upload periodically using the automated script

## Automated Daily Upload (Cron Job)

Add to your crontab (`crontab -e`):

```bash
# Upload logs daily at 2 AM
0 2 * * * /path/to/upload_logs.sh >> /var/log/logshack_upload.log 2>&1
```

## Error Handling

```python
import requests
import sys

def upload_with_error_handling(api_key, file_path):
    """Upload with proper error handling"""
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "http://localhost/api/logs/upload",
                headers={"X-API-Key": api_key},
                files={'file': f},
                timeout=300  # 5 minute timeout for large files
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['new']} new QSOs added")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key")
            return False
        else:
            print(f"❌ Error: {response.json().get('error', 'Unknown error')}")
            return False
            
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Upload timeout - file may be too large")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to LogShackBaby server")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Usage
success = upload_with_error_handling("your_api_key", "log.adi")
sys.exit(0 if success else 1)
```
## Administrative API Examples

### Sysop Operations (System Administrator)

#### List All Users
```bash
curl -X GET "http://localhost/api/admin/users" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

#### Create New User
```bash
curl -X POST "http://localhost/api/admin/users" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "W2XYZ",
    "email": "w2xyz@example.com",
    "password": "secure_password",
    "role": "user"
  }'
```

#### Update User Role
```bash
curl -X PUT "http://localhost/api/admin/users/5" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "logadmin"
  }'
```

#### Delete User (and all their logs)
```bash
curl -X DELETE "http://localhost/api/admin/users/5" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

### Log Admin Operations

#### List All Users with Log Counts
```bash
curl -X GET "http://localhost/api/logadmin/users" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

#### View User's Logs
```bash
curl -X GET "http://localhost/api/logadmin/users/5/logs?page=1&per_page=50" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

#### Reset User's Logs (delete all)
```bash
curl -X DELETE "http://localhost/api/logadmin/users/5/logs" \
  -H "X-Session-Token: YOUR_SESSION_TOKEN"
```

### Python Admin Examples

#### Create Multiple Users
```python
import requests

def create_user(session_token, callsign, email, password, role='user'):
    """Create a new user (sysop only)"""
    url = "http://localhost/api/admin/users"
    headers = {
        "X-Session-Token": session_token,
        "Content-Type": "application/json"
    }
    data = {
        "callsign": callsign,
        "email": email,
        "password": password,
        "role": role
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"✅ User {callsign} created successfully")
        return response.json()
    else:
        print(f"❌ Failed to create user: {response.json().get('error')}")
        return None

# Usage
session_token = "your_sysop_session_token"
create_user(session_token, "W3ABC", "w3abc@example.com", "password123", "user")
create_user(session_token, "K4XYZ", "k4xyz@example.com", "password456", "logadmin")
```

#### Reset User Logs
```python
import requests

def reset_user_logs(session_token, user_id):
    """Reset all logs for a user (logadmin only)"""
    url = f"http://localhost/api/logadmin/users/{user_id}/logs"
    headers = {"X-Session-Token": session_token}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
    else:
        print(f"❌ Failed: {response.json().get('error')}")

# Usage
session_token = "your_logadmin_session_token"
reset_user_logs(session_token, 5)
```

## User Roles Reference

| Role | Permissions |
|------|-------------|
| **user** | Manage own logs, API keys, and settings |
| **contestadmin** | Read-only access to all user logs, generate custom reports from all logs |
| **logadmin** | View all user logs, reset user logs |
| **sysop** | Full system administration: create/modify/delete users, assign roles |

**Note**: The first user registered automatically becomes a sysop.

## Contest Admin Examples

### Get Available Additional Fields
```bash
curl -X GET http://localhost/api/contestadmin/available-fields \
  -H "X-Session-Token: YOUR_CONTESTADMIN_SESSION_TOKEN"
```

Response:
```json
{
  "additional_fields": ["contest_id", "arrl_sect", "srx", "stx", "operator"]
}
```

### Generate Custom Report
```bash
curl -X POST http://localhost/api/contestadmin/report \
  -H "X-Session-Token: YOUR_CONTESTADMIN_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": ["user_callsign", "qso_date", "time_on", "call", "band", "mode", "json:contest_id"],
    "filters": {
      "date_from": "2025-12-01",
      "date_to": "2025-12-31",
      "bands": ["20m", "40m"],
      "modes": ["FT8", "SSB"]
    }
  }'
```

Response:
```json
{
  "report": [
    {
      "user_callsign": "W1ABC",
      "qso_date": "20251215",
      "time_on": "143000",
      "call": "K2DEF",
      "band": "20m",
      "mode": "FT8",
      "json:contest_id": "ARRL-10M"
    }
  ],
  "total": 1,
  "fields": ["user_callsign", "qso_date", "time_on", "call", "band", "mode", "json:contest_id"]
}
```

### Python Contest Admin Example
```python
import requests
import csv

def generate_contest_report(session_token, fields, filters=None):
    """Generate a custom report from all user logs"""
    url = "http://localhost/api/contestadmin/report"
    headers = {
        "X-Session-Token": session_token,
        "Content-Type": "application/json"
    }
    data = {"fields": fields}
    if filters:
        data["filters"] = filters
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Report generated: {result['total']} records")
        return result['report']
    else:
        print(f"❌ Failed: {response.json().get('error')}")
        return None

def export_to_csv(report, fields, filename):
    """Export report to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report)
    print(f"✅ Exported to {filename}")

# Usage
session_token = "your_contestadmin_session_token"

# Generate report with filters
fields = ["user_callsign", "qso_date", "time_on", "call", "band", "mode"]
filters = {
    "date_from": "2025-12-01",
    "date_to": "2025-12-31",
    "bands": ["20m", "40m"]
}

report = generate_contest_report(session_token, fields, filters)
if report:
    export_to_csv(report, fields, "contest_report.csv")
```
