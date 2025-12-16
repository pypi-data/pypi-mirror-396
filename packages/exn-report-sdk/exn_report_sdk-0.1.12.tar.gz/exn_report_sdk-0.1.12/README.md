# Exnodes Report Service SDK

Version: 0.1.0

# Khởi tạo client - install SDK
```
from exn_salon_report_sdk import ReportClient, ReportSDKException

api_key = "your_api_key"
secret_key = "your_secret_key"
client = ReportClient(api_key, secret_key)

# Gọi API để lấy báo cáo
try:
    report_id = "12345"
    report = client.get_report(report_id)
    print("Report:", report)

    # Tạo mới một báo cáo
    new_report_data = {
        "name": "Sales Report",
        "filters": {"date_range": "2025-01-01 to 2025-01-20"},
    }
    new_report = client.create_report(new_report_data)
    print("New Report Created:", new_report)
    
except ReportSDKException as e:
    print("SDK Error:", str(e))
```

---------------------------------


# Xử lý phía Service Report
## 1. Lấy API key từ header.
```
api_key = request.headers.get("API-Key")
if not api_key:
    return {"error": "API key is required"}, 401

secret_key = get_secret_key_from_db(api_key)
if not secret_key:
    return {"error": "Invalid API key"}, 401

```

## 2. Xác minh chữ ký
```
import hmac
import hashlib
import base64

def verify_signature(secret_key, signature_payload, signature):
    expected_signature = hmac.new(
        secret_key.encode(), 
        signature_payload.encode(), 
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(expected_signature).decode()
    return hmac.compare_digest(expected_signature, signature)

# Xử lý chữ ký
signature_payload = f"{api_key}{timestamp}{request_payload}"
if not verify_signature(secret_key, signature_payload, received_signature):
    return {"error": "Invalid signature"}, 401
```

## 3. Kiểm tra timestamp (chống replay attack):
```
from datetime import datetime, timedelta

def is_timestamp_valid(request_timestamp, max_skew_minutes=5):
    try:
        timestamp = datetime.fromisoformat(request_timestamp)
        now = datetime.utcnow()
        return abs((now - timestamp).total_seconds()) <= max_skew_minutes * 60
    except ValueError:
        return False

if not is_timestamp_valid(timestamp):
    return {"error": "Invalid or expired timestamp"}, 401
```