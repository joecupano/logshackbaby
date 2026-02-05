# LogShackBaby 📻

**Amateur Radio Log Server** - A web-based ADIF log management system for amateur radio operators.

LogShackBaby provides a secure, containerized solution for uploading, storing, and managing amateur radio QSO logs in ADIF 3.1.6 format with multi-factor authentication and API support.

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

### Prerequisites
- Docker and Docker Compose
- 2GB RAM minimum
- 10GB disk space for logs

### Installation

LogShackBaby supports two deployment methods: **Docker** (containerized) and **Local** (native installation).

#### Option 1: Docker Deployment (Recommended for Production)

Easiest setup with full isolation and portability:

1. **Clone or extract the project**
   ```bash
   cd /home/pi/source/LogShackBaby
   ```

2. **Run the Docker installation script**
   ```bash
   ./install-docker.sh
   ```

The script will:
- Check for and install Docker if needed
- Set up user permissions for Docker
- Create `.env` file with secure random passwords
- Build all Docker images
- Create persistent volumes

3. **Start the application**
   ```bash
   ./start-docker.sh
   ```

4. **Access the application**
   - Open your browser to: `http://localhost` (NGINX)
   - Or: `http://localhost:5000` (direct app access)
   - For SSL: Configure NGINX with your certificates (see NGINX Configuration)

**Docker Management:**
```bash
# Start containers
./start-docker.sh

# Stop containers
./stop-docker.sh

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check status
docker-compose ps
```

#### Option 2: Local Installation (Native - No Docker)

Install and run directly on your system:

1. **Clone or extract the project**
   ```bash
   cd /home/pi/source/LogShackBaby
   ```

2. **Run the local installation script**
   ```bash
   ./install-local.sh
   ```

The script will:
- Check for and install Python 3, PostgreSQL, and dependencies
- Create PostgreSQL database with secure random password
- Set up Python virtual environment
- Install all Python dependencies
- Initialize database schema
- Optionally create systemd service

3. **Start the application**
   ```bash
   ./start-local.sh
   ```

4. **Access the application**
   - Open your browser to: `http://localhost:5000`

**Local Management:**
```bash
# Start application
./start-local.sh

# Stop application (Ctrl+C or in another terminal)
./stop-local.sh

# If using systemd service
sudo systemctl start logshackbaby
sudo systemctl stop logshackbaby
sudo systemctl status logshackbaby
sudo journalctl -u logshackbaby -f
```

#### Option 3: Manual Installation

If you prefer complete manual control:

**Docker:**
```bash
cp .env.example .env
nano .env  # Edit with your secure passwords
docker-compose build
docker-compose up -d
```

**Local:**
```bash
# Install dependencies
sudo apt-get install postgresql python3 python3-pip python3-venv

# Create database
sudo -u postgres createdb logshackbaby
sudo -u postgres createuser logshackbaby

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configure and run
cd backend
python3 app.py
```

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

LogShackBaby fully supports ADIF 3.1.6 format files and processes **all ADIF fields**.

### How ADIF Fields Are Processed

**Core Fields** (stored in dedicated database columns for fast searching/filtering):
- `QSO_DATE` - Date of QSO (YYYYMMDD) **[Required]**
- `TIME_ON` - Start time (HHMMSS) **[Required]**
- `CALL` - Contacted station's callsign **[Required]**
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
- `QSO_DATE_OFF` / `TIME_OFF` - End date/time

**All Other ADIF Fields** (automatically stored in `additional_fields` JSON column):

The parser captures ALL fields from the ADIF 3.1.6 specification, including:
- Station details: `OPERATOR`, `OWNER_CALLSIGN`, `MY_CITY`, `MY_COUNTRY`, etc.
- Contest fields: `CONTEST_ID`, `SRX`, `STX`, `PRECEDENCE`, `CLASS`, etc.
- QSL tracking: `QSL_SENT`, `QSL_RCVD`, `LOTW_QSL_SENT`, `EQSL_QSL_RCVD`, etc.
- Power/Propagation: `TX_PWR`, `PROP_MODE`, `SAT_NAME`, `ANT_AZ`, etc.
- Award tracking: `AWARD_SUBMITTED`, `AWARD_GRANTED`, `CREDIT_SUBMITTED`, etc.
- Digital modes: `SUBMODE`, application-specific fields (N1MM, LOTW, eQSL, etc.)
- Location data: `LAT`, `LON`, `CNTY`, `STATE`, `COUNTRY`, `DXCC`, etc.
- And 100+ more fields...

### Viewing Additional Fields

In the web interface, the "Logs" tab shows a column called "Additional" which displays:
- A badge showing the count of additional ADIF fields captured for each QSO
- Hover over the badge to see a tooltip with all additional field names and values
- This makes it easy to see which QSOs have extra metadata

### Example ADIF File

```adif
<ADIF_VER:5>3.1.6
<PROGRAMID:12>LogShackBaby
<EOH>

<CALL:5>W1ABC <QSO_DATE:8>20240101 <TIME_ON:6>143000 
<BAND:3>20m <MODE:3>SSB <FREQ:8>14.250000 
<RST_SENT:2>59 <RST_RCVD:2>59 
<TX_PWR:3>100 <OPERATOR:5>K1XYZ <CONTEST_ID:7>CQ-WPX
<EOR>
```

All fields are captured and stored, preserving the complete QSO record.

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
