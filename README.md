# LogShackBaby 📻

**Amateur Radio Log Server** - A web-based ADIF log management system for amateur radio operators.

LogShackBaby provides a secure, containerized solution for uploading, storing, and managing amateur radio QSO logs in ADIF format with multi-factor authentication and API support.

## Features

### Core Functionality
- ✅ **ADIF Log Upload** - Parse and store amateur radio logs in ADIF format
- ✅ **ADIF Log Export** - Download logs in standard ADIF format
- ✅ **Automatic Deduplication** - Prevent duplicate QSO entries
- ✅ **Web Interface** - Clean, responsive UI for log management
- ✅ **Search & Filter** - Find logs by callsign, band, mode, and date
- ✅ **Statistics Dashboard** - View QSO counts, bands, modes, and more

### Security
- 🔐 **User Registration & Authentication** - Secure account management
- 🔐 **Role-Based Access Control** - Three user roles: user, logadmin, sysop
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

### Prerequisites
- Docker and Docker Compose
- 2GB RAM minimum
- 10GB disk space for logs

### Installation

1. **Clone or extract the project**
   ```bash
   cd /home/joe/source/logshackbaby
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your secure passwords
   ```

3. **Generate a secure secret key**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   # Add this to your .env file as SECRET_KEY
   ```

4. **Start the containers**
   ```bash
   docker-compose up -d
   ```

5. **Check the logs**
   ```bash
   docker-compose logs -f
   ```

6. **Access the application**
   - Open your browser to: `http://localhost` (or your server IP)
   - For SSL: Configure NGINX with your certificates (see NGINX Configuration)

### First Time Setup

1. **Register an account**
   - Click "Register" on the login page
   - Enter your callsign (e.g., W1ABC)
   - Provide your email and password
   - Click "Register"
   - **Note**: The first registered user automatically becomes a **sysop** (system administrator)

2. **User Roles**
   - **user** (default) - Can manage their own logs
   - **logadmin** - Can view and reset logs for all users
   - **sysop** - Full administrative access to create, modify, and delete users

3. **Enable Two-Factor Authentication** (Recommended)
4  - Login to your account
   - Go to Settings tab
   - Click "Enable 2FA"
   - Scan QR code with your authenticator app
   - Enter the 6-digit code to verify

3. **Create an API Key**
   - Go to "API Keys" tab
   - Click "Create New API Key"
   - Add a description (e.g., "N1MM Logger")
   - **Save the key immediately** - it won't be shown again!

5. **Upload Your First Log**
   - Go to "Upload" tab
   - Choose your ADIF file (.adi or .adif)
   - Click "Upload ADIF File"
   - Enter your API key when prompted

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
```

Response:
```json
{
  "message": "Upload successful",
  "total": 150,
  "new": 145,
  "duplicates": 5,
  "errors": 0
}
```

#### Get Logs
```http
GET /api/logs?page=1&per_page=50&callsign=W1ABC&band=20m&mode=SSB
X-Session-Token: your_session_token
```

#### Get Statistics
```http
GET /api/logs/stats
X-Session-Token: your_session_token
```

#### Export Logs (ADIF)
```http
GET /api/logs/export?callsign=W1ABC&band=20m&mode=SSB
X-Session-Token: your_session_token
```

Response: ADIF file download

#### Create API Key
```http
POST /api/keys
X-Session-Token: your_session_token
Content-Type: application/json

{
  "description": "N1MM Logger"
}
```

### Example: Upload Log with cURL

```bash
curl -X POST http://localhost/api/logs/upload \
  -H "X-API-Key: your_api_key_here" \
  -F "file=@my_log.adi"
```

### Example: Upload Log with Python

```python
import requests

api_key = "your_api_key_here"
log_file = "my_log.adi"

with open(log_file, 'rb') as f:
    response = requests.post(
        'http://localhost/api/logs/upload',
        headers={'X-API-Key': api_key},
        files={'file': f}
    )

print(response.json())
```

## ADIF Format Support

LogShackBaby supports standard ADIF 3.x format files. Core fields extracted include:

### Required Fields
- `QSO_DATE` - Date of QSO (YYYYMMDD)
- `TIME_ON` - Start time (HHMMSS)
- `CALL` - Contacted station's callsign

### Supported Optional Fields
- `BAND` - Band (e.g., 20m, 2m)
- `MODE` - Mode (e.g., SSB, CW, FT8)
- `FREQ` - Frequency in MHz
- `RST_SENT` / `RST_RCVD` - Signal reports
- `STATION_CALLSIGN` - Your callsign
- `MY_GRIDSQUARE` - Your grid square
- `GRIDSQUARE` - Contacted station's grid
- `NAME` - Operator name
- `QTH` - Location
- `COMMENT` - QSO notes

All additional ADIF fields are stored as JSON for future use.

## Deployment

### Production Deployment with Existing NGINX

If you have an existing NGINX reverse proxy with SSL:

1. **Disable the built-in NGINX container**
   
   Edit `docker-compose.yml` and comment out the nginx service.

2. **Configure your existing NGINX**
   
   Add this location block to your NGINX config:
   
   ```nginx
   location / {
       proxy_pass http://localhost:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       client_max_body_size 20M;
   }
   ```

3. **Ensure Docker network access**
   
   If your NGINX is in a Docker container, add it to the `logshackbaby-network`:
   
   ```yaml
   networks:
     logshackbaby-network:
       external: true
   ```

### Security Hardening

1. **Change default passwords**
   - Update `DB_PASSWORD` in `.env`
   - Generate secure `SECRET_KEY`

2. **Enable HTTPS**
   - Configure SSL certificates in NGINX
   - Force HTTPS redirects

3. **Firewall rules**
   - Only expose port 80/443 to internet
   - Keep port 5000 internal

4. **Regular backups**
   ```bash
   # Backup database
   docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql
   
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

### Database Backup
```bash
# Create backup
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql

# Restore backup
docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < backup.sql
```

### Access Database
```bash
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby
```

### Clean Up Old Data
```sql
-- Delete logs older than 5 years
DELETE FROM log_entries 
WHERE uploaded_at < NOW() - INTERVAL '5 years';

-- Vacuum database
VACUUM ANALYZE;
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Check database
docker-compose logs db

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection error
```bash
# Wait for database to be ready
docker-compose restart app

# Check database health
docker exec logshackbaby-db pg_isready -U logshackbaby
```

### Upload fails
- Check file is valid ADIF format
- Verify API key is correct
- Check file size (max 16MB)
- Review application logs

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
│   └── js/
│       └── app.js      # JavaScript application
├── database/           # PostgreSQL configuration
├── nginx/              # NGINX configuration
│   ├── nginx.conf     # Reverse proxy config
│   └── ssl/           # SSL certificates
├── docker-compose.yml # Container orchestration
└── README.md         # This file
```

## License

This project is provided as-is for amateur radio use. 

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration files

## Contributing

Contributions welcome! Consider adding:
- Additional ADIF field support
- Log export functionality
- Contest log analysis
- DXCC tracking
- Award tracking (WAS, WAC, etc.)
- Logbook of the World (LoTW) integration
- QRZ/HamDB lookup integration

## Amateur Radio Resources

- [ADIF Specification](http://www.adif.org/)
- [ARRL](http://www.arrl.org/)
- [QRZ.com](https://www.qrz.com/)

---

**73 de LogShackBaby Team** 📻✨
