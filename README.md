# LogShackBaby 📻

**Amateur Radio Log Server** - A web-based ADIF log management system for amateur radio operators.

LogShackBaby provides a secure, containerized solution for uploading, storing, and managing amateur radio QSO logs in ADIF 3.1.6 format with multi-factor authentication and API support.

## 📚 Documentation

- **[User Guide](docs/USERGUIDE.md)** - Complete guide for end users
- **[Administration Guide](docs/ADMINISTRATION.md)** - Setup, deployment, and maintenance
- **[Development Guide](docs/DEVELOPMENT.md)** - Technical documentation and API reference

## Features

### Core Functionality
- ✅ **ADIF 3.1.6 Support** - Full compliance with ADIF 3.1.6 specification
- ✅ **Complete ADIF Field Processing** - Captures ALL ADIF fields from uploaded logs
- ✅ **ADIF Log Upload** - Parse and store amateur radio logs in ADIF format
- ✅ **ADIF Log Export** - Download logs in standard ADIF format
- ✅ **Automatic Deduplication** - Prevent duplicate QSO entries
- ✅ **Web Interface** - Clean, responsive UI for log management
- ✅ **Search & Filter** - Find logs by callsign, band, mode, and date
- ✅ **Statistics Dashboard** - View QSO counts, bands, modes, and more
- ✅ **Additional Fields Display** - View all extra ADIF fields captured in logs

### Security
- 🔐 **User Registration & Authentication** - Secure account management
- 🔐 **Role-Based Access Control** - Four user roles: user, contestadmin, logadmin, sysop
- 🔐 **Multi-Factor Authentication (MFA)** - TOTP support for Google Authenticator, Authy, and Microsoft Authenticator
- 🔐 **API Keys** - Secure programmatic access for log uploads
- 🔐 **Password Hashing** - bcrypt-based secure password storage
- 🔐 **Session Management** - Database-backed sessions for multi-worker support

### Architecture
- 🐳 **Containerized** - Docker-based deployment
- 🐍 **Python Backend** - Flask web framework with SQLAlchemy ORM
- 🗄️ **PostgreSQL Database** - Reliable data storage with persistent volumes
- 🌐 **JavaScript Frontend** - Client-side rendering, no frameworks required
- 🔒 **NGINX Reverse Proxy** - SSL/TLS termination support

## Quick Start

### Docker Deployment (Recommended)

```bash
cd /home/pi/source/LogShackBaby
./install-docker.sh  # First time setup
./start-docker.sh    # Start services
```

Access at: `http://localhost`

### Local Deployment (No Docker)

```bash
cd /home/pi/source/LogShackBaby
./install-local.sh   # First time setup
./start-local.sh     # Start services
```

Access at: `http://localhost:5000`

**📖 For detailed installation instructions, see [Administration Guide](docs/ADMINISTRATION.md)**

### First Time Setup

1. **Register an account**
   - Click "Register" on the login page
   - Enter your callsign (e.g., W1ABC)
   - Provide your email and password
   - Click "Register"
   - **Note**: The first registered user automatically becomes a **sysop** (system administrator)

2. **User Roles**
   - **user** (default) - Can manage their own logs
   - **contestadmin** - Read-only access to all user logs with custom report generator
   - **logadmin** - Can view and reset logs for all users
   - **sysop** - Full administrative access to create, modify, and delete users

3. **Enable Two-Factor Authentication** (Recommended)
   - Login to your account
   - Go to Settings tab
   - Click "Enable 2FA"
   - Scan QR code with your authenticator app
   - Enter the 6-digit code to verify

4. **Create an API Key**
   - Go to "API Keys" tab
   - Click "Create New API Key"
   - Add a description (e.g., "N1MM Logger")
   - **Save the key immediately** - it won't be shown again!

5. **Upload Your First Log**
   - Go to "Upload" tab
   - Choose your ADIF file (.adi or .adif)
   - Click "Upload ADIF File"
   - Enter your API key when prompted

## Contest Administration

### Report Generator
For **contestadmin** users, a powerful report generator is available:

1. **Navigate to Contest Admin Tab**
   - Click "Report Generator" subtab

2. **Select Fields**
   - Choose from standard ADIF fields (QSO Date, Time, Call, Band, Mode, etc.)
   - **All 100+ ADIF 3.1.6 fields** are displayed as selection options
   - Fields marked with ● contain actual data in uploaded logs
   - Fields without marker are available for future logs

3. **Apply Filters** (Optional)
   - Date range (from/to)
   - Bands (comma-separated: 20m, 40m, 80m)
   - Modes (comma-separated: FT8, SSB, CW)

4. **Generate Report**
   - Click "Generate Report" to view results
   - Export to CSV for analysis in Excel or other tools

5. **Features**
   - Read-only access to all user logs
   - Complete ADIF 3.1.6 field selection (100+ fields available)
   - Visual indicators show which fields contain data
   - CSV export for external analysis
   - Up to 10,000 records per report

## API Documentation

### Authentication
All API endpoints except `/register` and `/login` require authentication via:
- **Session Token** (Web UI): `X-Session-Token` header
- **API Key** (Programmatic): `X-API-Key` header

### Endpoints

#### User Registration
```http
POST /api/register
Content-Type: application/json

{
  "callsign": "W1ABC",
  "email": "w1abc@example.com",
  "password": "secure_password"
}
```

#### User Login
```http
POST /api/login
Content-Type: application/json

{
  "callsign": "W1ABC",
  "password": "secure_password"
}
```

Response:
```json
{
  "session_token": "...",
  "callsign": "W1ABC",
  "mfa_required": false
}
```

#### Upload ADIF Log
```http
POST /api/logs/upload
X-API-Key: your_api_key_here
Content-Type: multipart/form-data

file: <ADIF file>
`` Getting Started

### First Time Setup

1. **Register an account** - First user automatically becomes system administrator
2. **Enable Two-Factor Authentication** (recommended)
3. **Create an API Key** for log uploads
4. **Upload your logs** via web interface or API

**📖 For complete instructions, see [User Guide](docs/USERGUIDE.md)**

## User Roles

- **user** - Manage own logs, API keys, and settings
- **contestadmin** - Generate reports from all user logs
- **logadmin** - View and manage all user logs
- **sysop** - Full system administration

**📖 For details on roles and permissions, see [User Guide](docs/USERGUIDE.md)**

## API Overview

LogShackBaby provides a complete REST API for programmatic access.

**Authentication:** Session tokens or API keys  
**Endpoints:** 30+ endpoints for logs, users, and administration

**Common Operations:**
```bash
# Upload log
curl -X POST http://localhost/api/logs/upload \
  -H "X-API-Key: your_key" \
  -F "file=@log.adi"

# Get statistics
curl http://localhost:5000/api/logs/stats \
  -H "X-Session-Token: your_token"
```

**📖 For complete API documentation, see [Development Guide](docs/DEVELOPMENT.md)**
   # Backup with date
   docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup-$(date +%Y%m%d).sql
   ```

5. **Update regularly**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Maintenance

### View Logs
```bash
docker-compose logs -f app
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart app
docker-compose restart db
```

### Update Application
```bash
git pull  # or extract new version
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Backup**ADIF 3.1.6** and captures **all 100+ ADIF fields**.

**Core Fields** are stored in dedicated database columns for fast searching:
- QSO_DATE, TIME_ON, CALL (required)
- BAND, MODE, FREQ, RST_SENT, RST_RCVD
- STATION_CALLSIGN, MY_GRIDSQUARE, GRIDSQUARE
- NAME, QTH, COMMENT

**Additional Fields** (100+ fields) are automatically captured in JSON storage:
- Contest information, QSL tracking, power/propagation
- Station details, awards, digital modes
- Location data, and more

**📖 For ADIF implementation details, see [Development Guide](docs/DEVELOPMENT.md)**

### MFA issues
- Ensure time is synchronized on server and client
- TOTP codes are time-sensitive (30-second window)
- Try codes before and after current code

## Development

### Run locally without Docker
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://logshackbaby:password@localhost:5432/logshackbaby"
export SECRET_KEY="your-secret-key"

# Initialize database
flask --app app init-db

# Run development server
python app.py
```

### Project Structure
```
logshackbaby/
├── backend/              # Python Flask application
│   ├── app.py           # Main application
│   ├── models.py        # Database models
│   ├── auth.py          # Authentication utilities
│   ├── adif_parser.py   # ADIF file parser
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── frontend/            # Web interface
│   ├── index.html      # Main HTML
│   ├── css/
│   │   └── style.css   # Styles
│   └── js/ & Maintenance

**📖 For complete deployment instructions, see [Administration Guide](docs/ADMINISTRATION.md)**

### Quick Commands

```bash
# Docker
./start-docker.sh          # Start services
./stop-docker.sh           # Stop services
docker-compose logs -f     # View logs

# Local
./start-local.sh           # Start application
./stop-local.sh            # Stop application

# Backup
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql
```

## Troubleshooting

**Common Issues:**
- Container won't start → Check logs: `docker-compose logs`
- Database connection error → Restart: `docker-compose restart app`
- Upload fails → Check file format and API key
-  Project Structure

```
LogShackBaby/
├── backend/              # Python Flask application
├── frontend/             # Web interface (HTML/CSS/JS)
├── database/             # PostgreSQL configuration
├── nginx/                # NGINX reverse proxy
├── docs/                 # Documentation
│   ├── USERGUIDE.md      # User guide
│   ├── ADMINISTRATION.md # Admin guide
│   └── DEVELOPMENT.md    # Technical docs
├── docker-compose.yml    # Container orchestration
└── README.md             # This file
```

## Technology Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy, Gunicorn
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker, NGINX
- **Security**: bcrypt, TOTP 2FA, API keys

## Contributing

Contributions welcome! See [Development Guide](docs/DEVELOPMENT.md) for:
- Development environment setup
- Code organization
- API documentation
- Testing procedures

## Resources

- **[ADIF Specification](http://www.adif.org/)**
- **[ARRL](http://www.arrl.org/)**
- **[QRZ.com](https://www.qrz.com/)**

## License

This project is provided as-is for amateur radio use.