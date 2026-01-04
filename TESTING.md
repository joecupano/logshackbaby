# LogShackBaby Testing Guide

## Prerequisites

Before testing, ensure:
- Docker and Docker Compose are installed
- Ports 80, 443, and 5000 are available
- You have the sample_log.adi file

## Quick Test Procedure

### 1. Start the Application

```bash
cd /home/joe/source/logshackbaby
./start.sh
```

Wait for all containers to start (about 10-15 seconds).

### 2. Verify Containers are Running

```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  STATUS              PORTS
logshackbaby-app        "gunicorn..."            Up                  0.0.0.0:5000->5000/tcp
logshackbaby-db         "docker-entrypoint..."   Up (healthy)        5432/tcp
logshackbaby-nginx      "/docker-entrypoint..."  Up                  0.0.0.0:80->80/tcp
```

### 3. Test Health Endpoint

```bash
curl http://localhost/api/health
```

Expected: `{"status":"healthy"}`

### 4. Test User Registration

```bash
curl -X POST http://localhost/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "TEST1",
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

Expected: Registration successful message

### 5. Test User Login

```bash
curl -X POST http://localhost/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "TEST1",
    "password": "TestPassword123"
  }'
```

Save the `session_token` from the response.

### 6. Create API Key

Using the session token from step 5:

```bash
SESSION_TOKEN="your_session_token_here"

curl -X POST http://localhost/api/keys \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: $SESSION_TOKEN" \
  -d '{"description": "Test Key"}'
```

Save the `api_key` from the response.

### 7. Upload Sample Log

```bash
API_KEY="your_api_key_here"

curl -X POST http://localhost/api/logs/upload \
  -H "X-API-Key: $API_KEY" \
  -F "file=@sample_log.adi"
```

Expected: Upload successful with counts of new/duplicate records

### 8. View Statistics

```bash
curl -X GET http://localhost/api/logs/stats \
  -H "X-Session-Token: $SESSION_TOKEN"
```

Should show 10 QSOs from the sample log.

### 9. Search Logs

```bash
# Get all logs
curl -X GET "http://localhost/api/logs?page=1" \
  -H "X-Session-Token: $SESSION_TOKEN"

# Search by callsign
curl -X GET "http://localhost/api/logs?callsign=W1ABC" \
  -H "X-Session-Token: $SESSION_TOKEN"

# Filter by band
curl -X GET "http://localhost/api/logs?band=20m" \
  -H "X-Session-Token: $SESSION_TOKEN"
```

## Web UI Testing

### 1. Open Browser

Navigate to: `http://localhost`

### 2. Test Registration Flow

1. Click "Register"
2. Enter callsign: `WEBTEST`
3. Enter email: `web@test.com`
4. Enter password: `WebTest123`
5. Confirm password
6. Click "Register"
7. Should redirect to login

### 3. Test Login Flow

1. Enter callsign: `WEBTEST`
2. Enter password: `WebTest123`
3. Click "Login"
4. Should see dashboard

### 4. Test MFA Setup

1. Go to "Settings" tab
2. Click "Enable 2FA"
3. Scan QR code with authenticator app (or enter secret manually)
4. Enter 6-digit code
5. Click "Verify & Enable"
6. Logout and login again to test MFA

### 5. Test API Key Creation

1. Go to "API Keys" tab
2. Click "Create New API Key"
3. Enter description: "Test Upload Key"
4. Copy the displayed API key
5. Verify key appears in the list

### 6. Test Log Upload

1. Go to "Upload" tab
2. Click "Choose File"
3. Select `sample_log.adi`
4. Click "Upload ADIF File"
5. Enter API key when prompted
6. Verify success message
7. Check upload history

### 7. Test Log Viewing

1. Go to "My Logs" tab
2. Verify 10 QSOs are displayed
3. Check statistics cards show correct counts
4. Test filters:
   - Enter "W1" in callsign filter
   - Select "20m" in band filter
   - Click "Apply"
5. Verify filtered results

## Automated Test Script

Save as `test_logshackbaby.sh`:

```bash
#!/bin/bash

set -e

BASE_URL="http://localhost"
API="${BASE_URL}/api"

echo "🧪 LogShackBaby Automated Test Suite"
echo "=================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check..."
HEALTH=$(curl -s ${API}/health)
if echo $HEALTH | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Register User
echo ""
echo "Test 2: User Registration..."
REGISTER=$(curl -s -X POST ${API}/register \
    -H "Content-Type: application/json" \
    -d '{"callsign":"AUTO1","email":"auto@test.com","password":"AutoTest123"}')

if echo $REGISTER | grep -q "successful"; then
    echo "✅ Registration passed"
else
    echo "❌ Registration failed"
    echo $REGISTER
    exit 1
fi

# Test 3: Login
echo ""
echo "Test 3: User Login..."
LOGIN=$(curl -s -X POST ${API}/login \
    -H "Content-Type: application/json" \
    -d '{"callsign":"AUTO1","password":"AutoTest123"}')

SESSION_TOKEN=$(echo $LOGIN | grep -o '"session_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$SESSION_TOKEN" ]; then
    echo "✅ Login passed"
    echo "   Session token: ${SESSION_TOKEN:0:20}..."
else
    echo "❌ Login failed"
    echo $LOGIN
    exit 1
fi

# Test 4: Create API Key
echo ""
echo "Test 4: Create API Key..."
API_KEY_RESPONSE=$(curl -s -X POST ${API}/keys \
    -H "Content-Type: application/json" \
    -H "X-Session-Token: $SESSION_TOKEN" \
    -d '{"description":"Automated Test"}')

API_KEY=$(echo $API_KEY_RESPONSE | grep -o '"api_key":"[^"]*' | cut -d'"' -f4)

if [ -n "$API_KEY" ]; then
    echo "✅ API key creation passed"
    echo "   API key: ${API_KEY:0:20}..."
else
    echo "❌ API key creation failed"
    echo $API_KEY_RESPONSE
    exit 1
fi

# Test 5: Upload Log
echo ""
echo "Test 5: Upload ADIF Log..."
if [ -f "sample_log.adi" ]; then
    UPLOAD=$(curl -s -X POST ${API}/logs/upload \
        -H "X-API-Key: $API_KEY" \
        -F "file=@sample_log.adi")
    
    if echo $UPLOAD | grep -q "Upload successful"; then
        echo "✅ Upload passed"
        echo $UPLOAD | grep -o '"new":[0-9]*' | tr -d '"'
    else
        echo "❌ Upload failed"
        echo $UPLOAD
        exit 1
    fi
else
    echo "⚠️  sample_log.adi not found, skipping upload test"
fi

# Test 6: Get Statistics
echo ""
echo "Test 6: Get Statistics..."
STATS=$(curl -s -X GET ${API}/logs/stats \
    -H "X-Session-Token: $SESSION_TOKEN")

if echo $STATS | grep -q "total_qsos"; then
    echo "✅ Statistics passed"
    TOTAL=$(echo $STATS | grep -o '"total_qsos":[0-9]*' | cut -d: -f2)
    echo "   Total QSOs: $TOTAL"
else
    echo "❌ Statistics failed"
    echo $STATS
    exit 1
fi

# Test 7: Get Logs
echo ""
echo "Test 7: Get Logs..."
LOGS=$(curl -s -X GET "${API}/logs?page=1" \
    -H "X-Session-Token: $SESSION_TOKEN")

if echo $LOGS | grep -q "logs"; then
    echo "✅ Get logs passed"
else
    echo "❌ Get logs failed"
    echo $LOGS
    exit 1
fi

# Test 8: Logout
echo ""
echo "Test 8: Logout..."
LOGOUT=$(curl -s -X POST ${API}/logout \
    -H "X-Session-Token: $SESSION_TOKEN")

if echo $LOGOUT | grep -q "successfully"; then
    echo "✅ Logout passed"
else
    echo "❌ Logout failed"
    echo $LOGOUT
    exit 1
fi

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo "=================================="
```

Make it executable and run:
```bash
chmod +x test_logshackbaby.sh
./test_logshackbaby.sh
```

## Performance Testing

### Load Test with Apache Bench

Test concurrent uploads:
```bash
# Create multiple ADIF files
for i in {1..10}; do
    cp sample_log.adi test_log_${i}.adi
done

# Test upload performance
ab -n 100 -c 10 \
   -H "X-API-Key: your_api_key" \
   -p sample_log.adi \
   -T "multipart/form-data; boundary=1234567890" \
   http://localhost/api/logs/upload
```

### Database Performance

```bash
# Connect to database
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby

# Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Security Testing

### Test Password Hashing
```bash
# Passwords should never appear in logs
docker-compose logs app | grep -i password || echo "✅ No passwords in logs"
```

### Test MFA
```bash
# MFA secrets should be encrypted/hashed
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby -c \
    "SELECT callsign, mfa_enabled, LENGTH(mfa_secret) as secret_length FROM users WHERE mfa_enabled = true;"
```

### Test API Key Security
```bash
# API keys should be hashed
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby -c \
    "SELECT key_prefix, LENGTH(key_hash) as hash_length, created_at FROM api_keys LIMIT 5;"
```

## Troubleshooting Tests

### If tests fail:

1. **Check container status**
   ```bash
   docker-compose ps
   docker-compose logs
   ```

2. **Verify database connection**
   ```bash
   docker exec logshackbaby-db pg_isready -U logshackbaby
   ```

3. **Check application logs**
   ```bash
   docker-compose logs -f app
   ```

4. **Reset and retry**
   ```bash
   docker-compose down -v
   docker-compose up -d
   sleep 10
   ./test_logshack.sh
   ```

## Expected Test Results

After running all tests, you should have:
- ✅ 1-3 registered users
- ✅ 1-3 API keys
- ✅ 10+ log entries (from sample_log.adi)
- ✅ Upload history showing successful imports
- ✅ Statistics showing correct counts

## Clean Up After Testing

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove all test files
rm -f test_log_*.adi
```

## Continuous Testing

For ongoing testing, consider:
1. Setting up automated tests in CI/CD
2. Creating a test environment separate from production
3. Regular backup and restore testing
4. Load testing with realistic data volumes

---

**Happy Testing!** 🧪✨
