# Backend - LogShackBaby

This directory contains the backend services for LogShackBaby, an Amateur Radio log management system.

## Overview

LogShackBaby is a Flask-based REST API server that manages amateur radio contact logs in ADIF (Amateur Data Interchange Format) format. The system supports user authentication, multi-factor authentication (MFA), API key management, log uploads, and amateur radio contest management.

## Files

### Core Application Files

#### `app.py`
Main Flask application serving the LogShackBaby API. Handles:
- User authentication and session management
- API key authentication
- Role-based access control (user, contestadmin, logadmin, sysop)
- ADIF log file uploads and parsing
- QSO (contact) log management with deduplication
- Search, filtering, and export of log entries
- Frontend static file serving

**Key Features:**
- Session-based authentication with MFA support
- API key authentication for programmatic access
- Upload deduplication using QSO hashing
- PostgreSQL database integration
- CORS support for web clients
- 16MB file upload limit

#### `models.py`
SQLAlchemy database models defining the data schema. Includes:

**Models:**
- `User` - User accounts with callsign, email, password, MFA settings, and role-based permissions
- `APIKey` - API keys for programmatic access with hashed storage
- `LogEntry` - Amateur radio contact logs with ADIF fields and deduplication
- `Session` - User session management with MFA verification tracking
- `UploadLog` - Upload tracking with statistics (new/duplicate/error records)
- `Contest` - Contest definitions with rules and scoring configuration
- `ContestEntry` - Contest participation entries linking users, contests, and log entries

**Database Features:**
- Indexed fields for efficient queries (callsign, call, station_callsign, qso_hash)
- JSON storage for additional ADIF fields
- Cascade delete for data integrity
- Unique constraints for deduplication

#### `adif_parser.py`
ADIF 3.1.6 format parser for amateur radio logs. Features:
- Complete ADIF 3.1.6 specification support
- Parses both ADI (text) and ADX (XML) formats
- Core field extraction for indexed database columns
- Additional field storage in JSON for full compatibility
- QSO hash generation for deduplication
- Field validation for bands and modes
- Header parsing for ADIF metadata

**Supported Formats:**
- ADI (ADIF Data Interchange) - text-based format
- ADX (ADIF XML) - XML-based format

#### `auth.py`
Authentication and security utilities. Provides:
- Password hashing using bcrypt
- TOTP-based multi-factor authentication (MFA)
- QR code generation for MFA setup
- API key generation and verification
- Secure credential management

**Security Features:**
- Bcrypt password hashing with automatic salt generation
- Time-based One-Time Password (TOTP) for MFA
- Secure random API key generation (32 bytes)
- Key prefix storage for identification
- Token validation with time window tolerance

#### `contest_service.py`
Standalone Flask microservice for contest management. Handles:
- Contest creation and management (contestadmin role required)
- Contest entry submission and validation
- Real-time scoring and leaderboard generation
- Time-based contest filtering
- User participation tracking

**Contest Features:**
- Flexible rules configuration (bands, modes, time constraints)
- Customizable scoring system (base points, multipliers, bonuses)
- Automatic score calculation
- Leaderboard with rank calculation
- User statistics tracking

### Configuration Files

#### `requirements.txt`
Python package dependencies:
- `Flask==3.0.0` - Web framework
- `Flask-SQLAlchemy==3.1.1` - Database ORM
- `Flask-CORS==4.0.0` - Cross-Origin Resource Sharing
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `pyotp==2.9.0` - TOTP authentication
- `qrcode==7.4.2` - QR code generation
- `Pillow==10.1.0` - Image processing
- `bcrypt==4.1.2` - Password hashing
- `python-dotenv==1.0.0` - Environment variable management
- `gunicorn==21.2.0` - WSGI HTTP server

#### `Dockerfile`
Docker container definition for the main application service. Builds a Python 3.11-slim container with all dependencies installed and runs the Flask app using Gunicorn.

#### `Dockerfile.contest`
Docker container definition for the contest management microservice. Separate container for isolated contest functionality.

## Database Schema

The application uses PostgreSQL with the following tables:
- **users** - User accounts and authentication
- **api_keys** - API authentication credentials
- **log_entries** - Amateur radio contact logs (QSOs)
- **sessions** - Active user sessions
- **upload_logs** - File upload history and statistics
- **contests** - Contest definitions
- **contest_entries** - Contest participation and scoring

## API Authentication

Two authentication methods are supported:

1. **Session Authentication** - For web UI
   - Header: `X-Session-Token: <token>`
   - Supports MFA verification
   - Automatic session timeout tracking

2. **API Key Authentication** - For programmatic access
   - Header: `X-API-Key: <key>`
   - No MFA required
   - Usage tracking

## Role-Based Access Control

Four user roles with hierarchical permissions:
- **user** (0) - Basic access, own logs only
- **contestadmin** (1) - Contest management
- **logadmin** (2) - All logs access
- **sysop** (3) - Full system administration

## Environment Variables

Configure via `.env` file or environment:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask session secret (change in production!)
- `FLASK_ENV` - Development/production mode

## Running the Backend

### Development
```bash
python app.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```bash
docker-compose up
```

## API Endpoints

See [API_EXAMPLES.md](../docs/API_EXAMPLES.md) for comprehensive API documentation.

## ADIF Support

Supports ADIF 3.1.6 specification with:
- All standard ADIF fields
- Contest fields (contest_id, srx, stx, etc.)
- Award tracking fields
- Digital mode fields
- QSL information
- Application-specific fields

Core fields are indexed in dedicated columns; additional fields are stored in JSON for complete compatibility.
