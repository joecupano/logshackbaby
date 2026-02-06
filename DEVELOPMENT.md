# LogShackBaby Development Guide

**Version 1.0.0** | Last Updated: February 5, 2026

Complete technical documentation for developers working with LogShackBaby.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [ADIF Processing](#adif-processing)
- [Authentication System](#authentication-system)
- [Testing](#testing)
- [Code Organization](#code-organization)
- [Contributing](#contributing)
- [API Examples](#api-examples)

---

## Architecture Overview

LogShackBaby follows a three-tier architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  (Web Browser - HTML/CSS/JavaScript - No Frameworks)    │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS/HTTP
                   ↓
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│            NGINX Reverse Proxy (Optional)                │
│       - SSL/TLS Termination                             │
│       - Static File Serving                             │
│       - Load Balancing                                  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP
                   ↓
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│        Flask (Python) + Gunicorn WSGI Server            │
│  - REST API Endpoints                                   │
│  - Business Logic                                       │
│  - Authentication & Authorization                        │
│  - ADIF Parsing & Processing                            │
│  - Session Management                                    │
└──────────────────┬──────────────────────────────────────┘
                   │ PostgreSQL Protocol
                   ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│             PostgreSQL 16 Database                       │
│  - User Accounts                                        │
│  - QSO Records                                          │
│  - API Keys                                             │
│  - Session Storage                                       │
│  - Upload History                                        │
└─────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Frontend, backend, and database are clearly separated
2. **Stateless API**: RESTful API design with session tokens
3. **Security First**: bcrypt passwords, TOTP 2FA, API key authentication
4. **Database Isolation**: PostgreSQL only accessible via application
5. **No Frontend Frameworks**: Vanilla JavaScript for simplicity and performance
6. **Container Native**: Docker-first design with local fallback
7. **ADIF Compliance**: Full ADIF 3.1.6 specification support

---

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Web Framework**: Flask 3.0.0
- **WSGI Server**: Gunicorn 21.2.0
- **ORM**: SQLAlchemy 3.1.1 (via Flask-SQLAlchemy)
- **Database Driver**: psycopg2-binary 2.9.9
- **Password Hashing**: bcrypt 4.1.2
- **2FA/TOTP**: pyotp 2.9.0
- **QR Codes**: qrcode 7.4.2
- **CORS**: Flask-CORS 4.0.0

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design, CSS Grid, Flexbox
- **JavaScript**: ES6+, vanilla (no frameworks)
- **No Build Process**: Direct file serving

### Database
- **PostgreSQL**: Version 16 (Alpine in Docker)
- **Persistent Storage**: Docker volumes or local filesystem

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: NGINX (Alpine)
- **SSL/TLS**: Let's Encrypt or self-signed

### Development Tools
- **Version Control**: Git
- **Testing**: Python unittest, manual testing
- **Documentation**: Markdown

---

## Project Structure

```
LogShackBaby/
├── backend/                      # Python Flask application
│   ├── app.py                    # Main application (1066 lines)
│   ├── models.py                 # Database models (180 lines)
│   ├── auth.py                   # Authentication utilities (150 lines)
│   ├── adif_parser.py            # ADIF parser (250 lines)
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend container
│
├── frontend/                     # Web interface
│   ├── index.html                # Single-page application (350 lines)
│   ├── css/
│   │   └── style.css             # Responsive styles (500 lines)
│   └── js/
│       └── app.js                # Client application (600 lines)
│
├── database/                     # Database configuration
│   ├── Dockerfile                # PostgreSQL container
│   └── README.md                 # Database documentation
│
├── nginx/                        # Reverse proxy
│   ├── nginx.conf                # NGINX configuration
│   └── ssl/
│       └── README.md             # SSL setup instructions
│
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── sample_log.adi                # Test ADIF file
├── test_adif_fields.py           # ADIF field tests
│
├── README.md                     # Main documentation
│── USERGUIDE.md                  # End user guide
│── ADMINISTRATION.md             # Admin guide
│── DEVELOPMENT.md                # This file
│── PROJECT_FILES.txt             # Project structure
│
├── docker-compose.yml            # Container orchestration
├── docker-compose.dev.yml        # Development configuration
├── install-docker.sh             # Docker installation
├── start-docker.sh               # Start Docker containers
├── stop-docker.sh                # Stop Docker containers
│
├── install-local.sh              # Local installation
├── start-local.sh                # Start local app
└── stop-local.sh                 # Stop local app
```

---

## Development Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git
- Text editor or IDE

### Local Development Environment

#### 1. Clone Repository

```bash
git clone <repository-url>
cd LogShackBaby
```

#### 2. Set Up Database

```bash
# Create database
sudo -u postgres createdb logshackbaby
sudo -u postgres createuser logshackbaby
sudo -u postgres psql <<EOF
ALTER USER logshackbaby WITH PASSWORD 'devpassword';
GRANT ALL PRIVILEGES ON DATABASE logshackbaby TO logshackbaby;
EOF
```

#### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

#### 4. Configure Environment

```bash
# Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://logshackbaby:devpassword@localhost:5432/logshackbaby
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF
```

#### 5. Run Development Server

```bash
cd backend
python app.py
```

Access at: `http://localhost:5000`

**Note:** On first run, the database schema and default contest templates are automatically initialized.

### Using Docker for Development

```bash
# Copy development compose file
cp docker-compose.dev.yml docker-compose.override.yml

# Start services
docker-compose up

# View logs
docker-compose logs -f app
```

---

## API Documentation

### Authentication

Two authentication methods:

1. **Session Tokens** (Web UI)
   - Header: `X-Session-Token: <token>`
   - Obtained from `/api/login`

2. **API Keys** (Programmatic)
   - Header: `X-API-Key: <key>`
   - Created in user dashboard

### Endpoint Categories

- **Authentication**: Registration, login, logout
- **MFA**: Setup, enable, verify, disable
- **API Keys**: Create, list, delete
- **Logs**: Upload, retrieve, export, statistics
- **Admin**: User management, reports

### Complete API Reference

#### POST /api/register

Register a new user account.

**Request:**
```json
{
  "callsign": "W1ABC",
  "email": "w1abc@example.com",
  "password": "secure_password"
}
```

**Response:** `201 Created`
```json
{
  "message": "Registration successful",
  "callsign": "W1ABC"
}
```

**Errors:**
- `400`: Missing fields or invalid data
- `409`: Callsign or email already exists

---

#### POST /api/login

Authenticate user and receive session token.

**Request:**
```json
{
  "callsign": "W1ABC",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "session_token": "abc123...",
  "callsign": "W1ABC",
  "role": "user",
  "mfa_required": false,
  "must_change_password": false
}
```

If MFA enabled:
```json
{
  "session_token": "abc123...",
  "callsign": "W1ABC", 
  "role": "user",
  "mfa_required": true,
  "must_change_password": false
}
```

If password reset by admin:
```json
{
  "session_token": "abc123...",
  "callsign": "W1ABC",
  "role": "user", 
  "mfa_required": false,
  "must_change_password": true
}
```

**Notes:**
- If `must_change_password` is TRUE, user will be forced to change password
- If both `mfa_required` and `must_change_password` are TRUE, MFA verification happens first
- After MFA verification, the `/api/mfa/verify` response also includes `must_change_password` flag

**Errors:**
- `400`: Missing credentials
- `401`: Invalid credentials

---

#### POST /api/mfa/verify

Verify MFA code during login.

**Request:**
```json
{
  "mfa_token": "temp_token",
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "session_token": "abc123...",
  "callsign": "W1ABC",
  "role": "user"
}
```

---

#### POST /api/logout

Invalidate session token.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

---

#### POST /api/change-password

Change user's password. Works for both voluntary password changes and forced password changes after admin reset.

**Headers:** `X-Session-Token`

**Request:**
```json
{
  "current_password": "current_or_temporary_password",
  "new_password": "new_secure_password"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

**Errors:**
- `400`: Missing required fields or new password too short
- `401`: Current password is incorrect

**Notes:**
- New password must be at least 8 characters
- Current password must be verified before change
- Automatically clears `must_change_password` flag
- This endpoint is accessible even when `must_change_password = TRUE` (all other endpoints are blocked)

---

#### POST /api/admin/users/:user_id/reset-password

Reset a user's password with automatically generated temporary password. User will be forced to change password on next login.

**Role Required:** `sysop`

**Headers:** `X-Session-Token`

**Parameters:**
- `user_id` (URL path): The ID of the user whose password to reset

**Response:** `200 OK`
```json
{
  "message": "Password reset successfully",
  "temporary_password": "Ab3dEf9hIjKl",
  "callsign": "W1ABC"
}
```

**Errors:**
- `401`: Authentication required
- `403`: Insufficient permissions (not sysop)
- `404`: User not found

**Behavior:**
- Generates secure 12-character random temporary password
- Sets user's `must_change_password = TRUE`
- Invalidates all existing sessions for that user
- Returns temporary password (shown only once)

**Security Notes:**
- Temporary password is only returned in this response - not stored anywhere
- All user sessions are terminated immediately
- User must log in with temporary password and change it before accessing features
- Temporary password uses cryptographically secure random generation

---

#### POST /api/mfa/setup

Initialize MFA for user account.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "secret": "ABC123XYZ...",
  "qr_code": "data:image/png;base64,...",
  "manual_entry": "ABC1 23XY Z..."
}
```

---

#### POST /api/mfa/enable

Enable MFA after verification.

**Headers:** `X-Session-Token`

**Request:**
```json
{
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA enabled successfully"
}
```

---

#### POST /api/mfa/disable

Disable MFA.

**Headers:** `X-Session-Token`

**Request:**
```json
{
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA disabled successfully"
}
```

---

#### GET /api/keys

List all API keys for current user.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "keys": [
    {
      "id": 1,
      "description": "N1MM Logger",
      "key_prefix": "lsb_abc123",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

---

#### POST /api/keys

Create new API key.

**Headers:** `X-Session-Token`

**Request:**
```json
{
  "description": "Python Upload Script"
}
```

**Response:** `201 Created`
```json
{
  "api_key": "lsb_abc123def456ghi789...",
  "description": "Python Upload Script",
  "created_at": "2026-02-05T12:00:00Z"
}
```

**Note:** Full key shown only once.

---

#### DELETE /api/keys/:id

Delete an API key.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "message": "API key deleted successfully"
}
```

---

#### POST /api/logs/upload

Upload ADIF log file.

**Headers:** `X-API-Key`

**Request:** `multipart/form-data`
- `file`: ADIF file (max 16MB)

**Response:** `200 OK`
```json
{
  "message": "Upload successful",
  "total": 150,
  "new": 145,
  "duplicates": 5,
  "errors": 0,
  "upload_id": 42
}
```

**Errors:**
- `400`: No file provided, invalid ADIF
- `401`: Invalid API key
- `413`: File too large

---

#### GET /api/logs

Retrieve user's logs with pagination and filtering.

**Headers:** `X-Session-Token`

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 50, max: 100)
- `callsign` (partial match)
- `band` (exact match)
- `mode` (exact match)
- `date_from` (YYYY-MM-DD)
- `date_to` (YYYY-MM-DD)

**Response:** `200 OK`
```json
{
  "logs": [
    {
      "id": 1,
      "qso_date": "20260201",
      "time_on": "143000",
      "call": "W2DEF",
      "band": "20m",
      "mode": "SSB",
      "freq": "14.250",
      "rst_sent": "59",
      "rst_rcvd": "59",
      "station_callsign": "W1ABC",
      "my_gridsquare": "FN42",
      "gridsquare": "FN31",
      "name": "John",
      "qth": "Boston",
      "comment": "Great QSO",
      "additional_fields": {
        "tx_pwr": "100",
        "operator": "K1XYZ"
      },
      "uploaded_at": "2026-02-05T10:00:00Z"
    }
  ],
  "total": 1500,
  "page": 1,
  "per_page": 50,
  "pages": 30
}
```

---

#### GET /api/logs/stats

Get statistics about user's logs.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "total_qsos": 1500,
  "unique_callsigns": 800,
  "bands": {
    "20m": 500,
    "40m": 300,
    "80m": 200
  },
  "modes": {
    "FT8": 800,
    "SSB": 500,
    "CW": 200
  },
  "date_range": {
    "first": "2020-01-01",
    "last": "2026-02-05"
  }
}
```

---

#### GET /api/logs/export

Export logs as ADIF file.

**Headers:** `X-Session-Token`

**Query Parameters:** (same as GET /api/logs)

**Response:** `200 OK`
- Content-Type: `text/plain`
- Content-Disposition: `attachment; filename="logbook.adi"`
- Body: ADIF formatted text

---

#### GET /api/uploads

Get upload history.

**Headers:** `X-Session-Token`

**Response:** `200 OK`
```json
{
  "uploads": [
    {
      "id": 42,
      "filename": "n1mm_log.adi",
      "total_records": 150,
      "new_records": 145,
      "duplicate_records": 5,
      "error_records": 0,
      "uploaded_at": "2026-02-05T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/admin/users (Sysop Only)

List all users with full details.

**Headers:** `X-Session-Token` (sysop role required)

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": 1,
      "callsign": "W1ABC",
      "email": "w1abc@example.com",
      "role": "user",
      "is_active": true,
      "mfa_enabled": true,
      "created_at": "2026-01-01T00:00:00Z",
      "log_count": 1500
    }
  ]
}
```

---

#### POST /api/admin/users (Sysop Only)

Create new user.

**Headers:** `X-Session-Token` (sysop)

**Request:**
```json
{
  "callsign": "K2XYZ",
  "email": "k2xyz@example.com",
  "password": "secure_password",
  "role": "user"
}
```

**Response:** `201 Created`

---

#### PUT /api/admin/users/:id (Sysop Only)

Update user details.

**Headers:** `X-Session-Token` (sysop)

**Request:**
```json
{
  "email": "newemail@example.com",
  "role": "logadmin",
  "is_active": true
}
```

**Response:** `200 OK`

---

#### DELETE /api/admin/users/:id (Sysop Only)

Delete user and all their data.

**Headers:** `X-Session-Token` (sysop)

**Response:** `200 OK`
```json
{
  "message": "User and all associated data deleted"
}
```

---

#### GET /api/contestadmin/available-fields

Get list of available ADIF fields with data indicators.

**Headers:** `X-Session-Token` (contestadmin)

**Response:** `200 OK`
```json
{
  "standard_fields": ["qso_date", "time_on", "call", ...],
  "additional_fields": ["tx_pwr", "operator", "contest_id", ...],
  "fields_with_data": ["tx_pwr", "operator"]
}
```

---

#### POST /api/contestadmin/report

Generate custom report from all user logs.

**Headers:** `X-Session-Token` (contestadmin)

**Request:**
```json
{
  "fields": ["user_callsign", "qso_date", "call", "band"],
  "filters": {
    "date_from": "2026-01-01",
    "date_to": "2026-01-31",
    "bands": ["20m", "40m"],
    "modes": ["FT8"]
  }
}
```

**Response:** `200 OK`
```json
{
  "report": [
    {
      "user_callsign": "W1ABC",
      "qso_date": "20260115",
      "call": "W2DEF",
      "band": "20m"
    }
  ],
  "total": 1,
  "fields": ["user_callsign", "qso_date", "call", "band"]
}
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    callsign VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    mfa_secret VARCHAR(32),
    mfa_enabled BOOLEAN DEFAULT false,
    must_change_password BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**Roles:** `user`, `contestadmin`, `logadmin`, `sysop`

**Password Reset Fields:**
- `must_change_password`: Set to TRUE when admin resets password, forces user to change password on next login
- When TRUE, user cannot access any endpoints except `/api/change-password`

### API Keys Table

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key_prefix VARCHAR(20) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Log Entries Table

```sql
CREATE TABLE log_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    qso_date VARCHAR(8) NOT NULL,
    time_on VARCHAR(6) NOT NULL,
    call VARCHAR(50) NOT NULL,
    band VARCHAR(10),
    mode VARCHAR(20),
    freq VARCHAR(20),
    rst_sent VARCHAR(10),
    rst_rcvd VARCHAR(10),
    station_callsign VARCHAR(50),
    my_gridsquare VARCHAR(10),
    gridsquare VARCHAR(10),
    name VARCHAR(100),
    qth VARCHAR(100),
    comment TEXT,
    qso_date_off VARCHAR(8),
    time_off VARCHAR(6),
    qso_hash VARCHAR(64) UNIQUE,
    additional_fields JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_call (call),
    INDEX idx_band (band),
    INDEX idx_mode (mode),
    INDEX idx_qso_date (qso_date)
);
```

**Note:** `additional_fields` stores all non-core ADIF fields as JSON.

### Upload Logs Table

```sql
CREATE TABLE upload_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255),
    total_records INTEGER,
    new_records INTEGER,
    duplicate_records INTEGER,
    error_records INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sessions Table

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    mfa_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_session_token (session_token),
    INDEX idx_user_id (user_id)
);
```

---

## ADIF Processing

### Supported ADIF Version

**ADIF 3.1.6** - Full compliance with backward compatibility for 3.x

### Field Categories

#### Core Fields (16 fields - dedicated columns)
- QSO_DATE, TIME_ON, CALL (required)
- BAND, MODE, FREQ
- RST_SENT, RST_RCVD
- STATION_CALLSIGN
- MY_GRIDSQUARE, GRIDSQUARE
- NAME, QTH, COMMENT
- QSO_DATE_OFF, TIME_OFF

#### Additional Fields (100+ fields - JSON storage)
All other ADIF 3.1.6 fields are automatically captured and stored in the `additional_fields` JSON column.

### Parser Implementation

Located in `backend/adif_parser.py`:

```python
class ADIFParser:
    """Parse ADIF 3.x log files"""
    
    def parse_file(self, file_content):
        """Parse entire ADIF file"""
        
    def parse_record(self, record_text):
        """Parse single QSO record"""
        
    def extract_field(self, field_text):
        """Extract field name and value"""
        
    def normalize_band(self, band):
        """Normalize band designation"""
        
    def calculate_hash(self, record):
        """Calculate unique hash for deduplication"""
```

### Deduplication Strategy

QSO hash calculated from:
```python
hash_string = f"{callsign}_{qso_date}_{time_on}_{band}_{mode}"
qso_hash = hashlib.sha256(hash_string.encode()).hexdigest()
```

Duplicates are detected and skipped during upload.

---

## Authentication System

### Password Security

**Hashing:** bcrypt with automatic salt
```python
from bcrypt import hashpw, gensalt, checkpw

# Hash password
password_hash = hashpw(password.encode('utf-8'), gensalt())

# Verify password
checkpw(password.encode('utf-8'), stored_hash)
```

**Password Reset Flow:**

When an administrator resets a user's password:

1. **Generate Temporary Password:**
   ```python
   import secrets
   import string
   alphabet = string.ascii_letters + string.digits
   temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
   ```

2. **Update User Record:**
   ```python
   user.password_hash = AuthManager.hash_password(temp_password)
   user.must_change_password = True
   ```

3. **Invalidate Sessions:**
   ```python
   Session.query.filter_by(user_id=user.id).delete()
   ```

4. **Enforce Password Change:**
   - The `require_auth` decorator checks `must_change_password` flag
   - If TRUE, blocks all requests except to `/api/change-password`
   - User redirected to password change screen in frontend
   - After successful password change, flag is set to FALSE

**Password Change Endpoint:**
```python
@app.route('/api/change-password', methods=['POST'])
@require_auth
def change_password():
    # Verify current password
    # Validate new password (min 8 chars)
    # Update password_hash
    # Set must_change_password = False
```

### Multi-Factor Authentication

**Protocol:** TOTP (Time-based One-Time Password) - RFC 6238

**Implementation:**
```python
import pyotp

# Generate secret
secret = pyotp.random_base32()

# Create TOTP instance
totp = pyotp.TOTP(secret)

# Verify code
totp.verify(user_code, valid_window=1)
```

**Compatible Apps:**
- Google Authenticator
- Microsoft Authenticator
- Authy
- Any TOTP app

### API Key Security

**Format:** `lsb_` + 32 random bytes (base64url)
```python
import secrets

api_key = f"lsb_{secrets.token_urlsafe(32)}"
```

**Storage:** bcrypt hashed, only prefix stored in plain text

### Session Management

**Tokens:** 32-byte random tokens
**Storage:** Database-backed (supports multiple workers)
**Expiration:** Configurable (default 7 days)

---

## Testing

### Manual Testing

See `docs/TESTING.md` (legacy) or follow these steps:

#### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

#### 2. Registration
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"callsign":"TEST1","email":"test@example.com","password":"TestPass123"}'
```

#### 3. Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"callsign":"TEST1","password":"TestPass123"}'
```

#### 4. Upload Test
```bash
curl -X POST http://localhost:5000/api/logs/upload \
  -H "X-API-Key: your_api_key" \
  -F "file=@sample_log.adi"
```

### Automated ADIF Field Testing

```bash
python3 test_adif_fields.py
```

### Unit Testing

Create tests in `backend/tests/`:

```python
import unittest
from app import app, db

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    def test_health_endpoint(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
    def test_register(self):
        response = self.client.post('/api/register', json={
            'callsign': 'TEST',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
```

Run with:
```bash
python -m unittest discover backend/tests
```

---

## Code Organization

### Backend Structure

**app.py** - Main application
- Flask app initialization
- Route definitions
- Middleware
- Error handlers

**models.py** - Data models
- User model
- APIKey model
- LogEntry model
- UploadLog model
- Session model

**auth.py** - Authentication utilities
- Password hashing
- MFA functions
- API key generation
- Session management

**adif_parser.py** - ADIF parsing
- File parsing
- Field extraction
- Normalization
- Hash calculation

### Frontend Structure

**index.html** - Single-page app
- Login/register forms
- Dashboard layout
- Tab navigation
- Modal dialogs

**style.css** - Styling
- Responsive layout
- Component styles
- Utility classes
- Mobile breakpoints

**app.js** - Client application
- API client
- State management
- Event handling
- DOM manipulation

### Coding Standards

**Python:**
- PEP 8 style guide
- Docstrings for functions
- Type hints where beneficial
- Error handling with try/except

**JavaScript:**
- ES6+ features
- Consistent naming (camelCase)
- Comments for complex logic
- Error handling with try/catch

**SQL:**
- Parameterized queries (SQLAlchemy ORM)
- Indexes on frequently queried columns
- Proper foreign key constraints

---

## Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Update documentation
5. Submit pull request

### Adding New Features

#### Example: Adding a New API Endpoint

1. **Define route in app.py:**
```python
@app.route('/api/myfeature', methods=['POST'])
@require_auth
def my_feature():
    # Implementation
    return jsonify({'message': 'Success'}), 200
```

2. **Add database model if needed (models.py):**
```python
class MyFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255))
```

3. **Update frontend (app.js):**
```javascript
async function callMyFeature() {
    const response = await fetch('/api/myfeature', {
        method: 'POST',
        headers: {
            'X-Session-Token': sessionToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({data: 'value'})
    });
    return await response.json();
}
```

4. **Add tests**
5. **Update documentation**

---

## API Examples

### Python Upload Example

```python
import requests

def upload_log(api_key, file_path):
    url = "http://localhost:5000/api/logs/upload"
    headers = {"X-API-Key": api_key}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['new']} new, {data['duplicates']} dups")
        return True
    else:
        print(f"❌ Error: {response.json().get('error')}")
        return False

# Usage
upload_log("lsb_abc123...", "my_log.adi")
```

### Bash Upload Script

```bash
#!/bin/bash
API_KEY="lsb_your_key_here"
LOG_FILE="$1"

if [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <adif_file>"
    exit 1
fi

curl -X POST http://localhost:5000/api/logs/upload \
    -H "X-API-Key: $API_KEY" \
    -F "file=@$LOG_FILE" \
    | jq .

echo "Upload complete!"
```

### JavaScript Fetch Example

```javascript
async function uploadLog(apiKey, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/logs/upload', {
        method: 'POST',
        headers: {
            'X-API-Key': apiKey
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log(`✅ Uploaded: ${data.new} new QSOs`);
    } else {
        console.error(`❌ Error: ${data.error}`);
    }
}
```

---

## Performance Considerations

### Database Optimization

**Indexes:** Created on frequently queried columns
- `user_id` (foreign keys)
- `call`, `band`, `mode` (search filters)
- `qso_hash` (deduplication)
- `session_token` (session lookups)

**Connection Pooling:** SQLAlchemy manages connection pool

**Query Optimization:**
- Pagination for large result sets
- Selective field loading
- Proper use of JOINs

### Application Optimization

**Gunicorn Workers:** Formula: (2 × CPU cores) + 1

**Static File Serving:** NGINX handles static files

**Database Sessions:** Database-backed for multi-worker support

### Frontend Optimization

**No Build Step:** Direct file serving

**Minimal Dependencies:** Vanilla JavaScript for speed

**Lazy Loading:** Only load data when needed

---

## Security Considerations

### Input Validation

- All user inputs validated
- SQL injection prevented (ORM with parameterized queries)
- XSS prevented (proper escaping)
- File upload validation (ADIF format, size limits)

### Authentication

- bcrypt password hashing
- TOTP 2FA optional
- API keys hashed
- Session tokens random and secure

### Network Security

- Database not exposed to internet
- CORS configured
- Optional reverse proxy with SSL
- Rate limiting (via NGINX)

### Best Practices

- Keep dependencies updated
- Regular security audits
- Monitor for suspicious activity
- Educate users on 2FA

---

**Happy Developing!** 🚀

*For user instructions, see USERGUIDE.md*  
*For administration, see ADMINISTRATION.md*

**73!** 📻✨
