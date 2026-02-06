# LogShackBaby Administration Guide

**Version 1.0.0** | Last Updated: February 5, 2026

Complete setup, deployment, and administration guide for LogShackBaby servers.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Docker Deployment](#docker-deployment)
- [Local Deployment](#local-deployment)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [SSL/TLS Setup](#ssltls-setup)
- [User Management](#user-management)
- [Database Administration](#database-administration)
- [Backup and Restore](#backup-and-restore)
- [Monitoring](#monitoring)
- [Security Hardening](#security-hardening)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)
- [Deployment Checklist](#deployment-checklist)

---

## System Requirements

### Docker Deployment

**Minimum Requirements:**
- Linux, macOS, or Windows with WSL2
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM
- 10GB disk space
- Ports 80, 443, 5000 available

**Recommended:**
- 4GB RAM
- 20GB disk space
- SSD storage for database

### Local Deployment

**Minimum Requirements:**
- Linux (Ubuntu 20.04+, Debian 11+, or similar)
- Python 3.8+
- PostgreSQL 12+
- 2GB RAM
- 10GB disk space
- Port 5000 available

**Recommended:**
- Python 3.11+
- PostgreSQL 16
- 4GB RAM
- 20GB disk space

### Network Requirements

- Outbound internet access (for package downloads)
- Inbound HTTP/HTTPS access (ports 80/443)
- Static IP or domain name (recommended for production)
- DNS properly configured

---

## Installation Methods

LogShackBaby supports three installation methods:

1. **Docker Deployment** - Recommended for production (containerized, isolated)
2. **Local Deployment** - Native installation without Docker
3. **Manual Installation** - Complete control over every step

---

## Docker Deployment

### Quick Start

```bash
cd /home/pi/source/LogShackBaby
./install-docker.sh
./start-docker.sh
```

Access at: `http://localhost`

### Step-by-Step Docker Installation

#### 1. Install Docker (if not already installed)

The `install-docker.sh` script will check and install Docker automatically.

**Manual Docker Installation:**

**For Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**For other systems**, see: https://docs.docker.com/engine/install/

#### 2. Run Installation Script

```bash
cd /home/pi/source/LogShackBaby
./install-docker.sh
```

**What it does:**
- Checks for Docker and Docker Compose
- Installs Docker if needed
- Adds user to docker group
- Creates `.env` file with secure random passwords
- Generates SECRET_KEY and DB_PASSWORD
- Builds Docker images
- Creates persistent volumes

#### 3. Review Configuration

Check the generated `.env` file:
```bash
cat .env
```

Expected contents:
```bash
DB_PASSWORD=<random-secure-password>
SECRET_KEY=<random-secret-key>
```

**Optional:** Customize these values before starting.

#### 4. Start Services

```bash
./start-docker.sh
```

**What it does:**
- Starts three Docker containers:
  - `logshackbaby-db` - PostgreSQL 16 database
  - `logshackbaby-app` - Flask application with Gunicorn
  - `logshackbaby-nginx` - NGINX reverse proxy
- Creates network: `logshackbaby-network`
- Mounts persistent volume: `postgres_data`

#### 5. Verify Services Are Running

```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  STATUS              PORTS
logshackbaby-app    "gunicorn..."            Up                  0.0.0.0:5000->5000/tcp
logshackbaby-db     "docker-entrypoint..."   Up (healthy)        5432/tcp
logshackbaby-nginx  "/docker-entrypoint..."  Up                  0.0.0.0:80->80/tcp
```

#### 6. Test Health Endpoint

```bash
curl http://localhost/api/health
```

Expected: `{"status":"healthy"}`

### Docker Management Commands

```bash
# Start containers
./start-docker.sh

# Stop containers
./stop-docker.sh

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f nginx

# Restart a service
docker-compose restart app

# Check status
docker-compose ps

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including volumes (DELETES ALL DATA)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Docker Access URLs

- **Via NGINX (recommended)**: `http://localhost` or `https://localhost` (with SSL)
- **Direct to app**: `http://localhost:5000`
- **Database**: Internal only (not exposed to host)

---

## Local Deployment

### Quick Start

```bash
cd /home/pi/source/LogShackBaby
./install-local.sh
./start-local.sh
```

Access at: `http://localhost:5000`

### Step-by-Step Local Installation

#### 1. Run Installation Script

```bash
cd /home/pi/source/LogShackBaby
./install-local.sh
```

**What it does:**
- Checks for Python 3, PostgreSQL, and required packages
- Installs missing dependencies (Ubuntu/Debian)
- Creates PostgreSQL database and user
- Generates secure random password
- Creates Python virtual environment
- Installs Python packages from requirements.txt
- Creates `.env` file
- Initializes database schema
- Optionally creates systemd service

#### 2. Review Configuration

Check the generated `.env` file:
```bash
cat .env
```

#### 3. Start Application

**Manual start:**
```bash
./start-local.sh
```

**Or with systemd:**
```bash
sudo systemctl start logshackbaby
sudo systemctl status logshackbaby
```

#### 4. Verify Service is Running

```bash
curl http://localhost:5000/api/health
```

Expected: `{"status":"healthy"}`

### Local Management Commands

```bash
# Start application
./start-local.sh

# Stop application
./stop-local.sh

# With systemd service
sudo systemctl start logshackbaby
sudo systemctl stop logshackbaby
sudo systemctl restart logshackbaby
sudo systemctl status logshackbaby

# Enable auto-start on boot
sudo systemctl enable logshackbaby

# View logs
sudo journalctl -u logshackbaby -f

# Without systemd (view process)
ps aux | grep gunicorn
```

---

## Manual Installation

For complete control over the installation process.

### Docker Manual Setup

```bash
# 1. Create .env file
cp .env.example .env
nano .env  # Edit with your secure passwords

# 2. Build images
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

### Local Manual Setup

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y postgresql python3 python3-pip python3-venv

# 2. Create PostgreSQL database
sudo -u postgres psql <<EOF
CREATE DATABASE logshackbaby;
CREATE USER logshackbaby WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE logshackbaby TO logshackbaby;
\q
EOF

# 3. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r backend/requirements.txt

# 5. Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://logshackbaby:your_secure_password@localhost:5432/logshackbaby
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF

# 6. Initialize database (done automatically on first run)

# 7. Run application
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Configuration

### Environment Variables

The `.env` file contains critical configuration:

```bash
# Database connection string
DATABASE_URL=postgresql://logshackbaby:password@db:5432/logshackbaby

# Flask secret key (for session security)
SECRET_KEY=your-random-secret-key-here

# Optional: Override database password separately (Docker)
DB_PASSWORD=your-database-password
```

**Generating Secure Values:**

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate DB_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

**Change ports:**
```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Change from 80 to 8080
      - "8443:443"
```

**Adjust worker count:**
```yaml
services:
  app:
    command: gunicorn -w 8 -b 0.0.0.0:5000 app:app  # Change from 4 to 8 workers
```

**Change max upload size:**

Edit `backend/app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # Change to 32MB
```

Also update `nginx/nginx.conf`:
```nginx
client_max_body_size 32M;
```

### Application Configuration

Key settings in `backend/app.py`:

```python
# Maximum file upload size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

---

## SSL/TLS Setup

### Using Let's Encrypt (Recommended)

#### 1. Install Certbot

```bash
sudo apt-get install certbot
```

#### 2. Obtain Certificate

```bash
sudo certbot certonly --standalone -d your-domain.com
```

#### 3. Copy Certificates

```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

#### 4. Update NGINX Configuration

Edit `nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }
}
```

#### 5. Restart NGINX

```bash
docker-compose restart nginx
```

#### 6. Set Up Auto-Renewal

```bash
sudo crontab -e
```

Add:
```bash
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/LogShackBaby/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/LogShackBaby/nginx/ssl/key.pem && docker-compose -f /path/to/LogShackBaby/docker-compose.yml restart nginx
```

### Using Self-Signed Certificate (Testing Only)

```bash
cd nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

---

## User Management

*For sysop administrators only.*

### First User Setup

The first registered user automatically becomes a **sysop** (system administrator).

### Creating Users via Web Interface

1. Log in as sysop
2. Go to "System Admin" tab
3. Click "Create New User"
4. Fill in:
   - Callsign
   - Email
   - Password
   - Role (user, contestadmin, logadmin, sysop)
5. Click "Create"

### User Roles

| Role | Permissions |
|------|-------------|
| **user** | Manage own logs, API keys, settings |
| **contestadmin** | Read-only access to all logs, generate reports |
| **logadmin** | View and reset logs for all users |
| **sysop** | Full admin: create/modify/delete users, assign roles |

### Modifying User Roles

1. Log in as sysop
2. Go to "System Admin" tab
3. Find the user
4. Click "Edit"
5. Change role
6. Click "Save"

### Resetting User Passwords

#### Automatic Password Reset (Recommended)

As sysop, you can reset any user's password with an automatically generated temporary password that forces the user to create a new password on next login.

**Step-by-Step Process:**

1. **Navigate to System Admin**
   - Log in as sysop
   - Click the "System Admin" tab

2. **Find the User**
   - Locate the user in the user list
   - Users are listed with callsign, email, role, and status

3. **Initiate Password Reset**
   - Click the yellow "Reset Password" button next to the user's name
   - A confirmation dialog will appear

4. **Confirm the Action**
   - Click "OK" to confirm
   - System generates a secure 12-character temporary password

5. **Copy the Temporary Password**
   - A modal dialog displays the temporary password
   - **⚠️ IMPORTANT**: This password is shown only once!
   - Click the "Copy" button to copy to clipboard
   - Or manually note down the password before closing

6. **Communicate to User**
   - Securely send the temporary password to the user
   - Do not send via unencrypted email if possible
   - Consider phone call, encrypted message, or in-person

7. **Close the Modal**
   - Click "Close" to dismiss the modal

**What Happens Behind the Scenes:**
- User's password is immediately changed to the temporary password
- `must_change_password` flag is set to `TRUE` in database
- All user's existing sessions are invalidated (forced logout)
- User must log in with temporary password and change it before accessing any features

**User Experience:**

When the user logs in:
1. They enter their callsign and the temporary password
2. If MFA is enabled, they complete MFA verification
3. They are automatically redirected to password change screen
4. They must enter the temporary password and choose a new password
5. After successful password change, they're granted full access
6. The `must_change_password` flag is cleared

**Security Features:**
- Temporary passwords are cryptographically secure (12 characters, alphanumeric)
- All existing sessions terminated immediately
- User cannot access any API endpoints except `/api/change-password` until password is changed
- Password requirements enforced (minimum 8 characters)
- Current password verification required for change

**Best Practices:**
- Always copy the temporary password before closing the modal
- Verify user identity before performing password reset
- Use secure communication channels for sharing temporary passwords
- Instruct users to change password immediately
- Consider keeping a log of password reset actions for security audits

#### Manual Password Reset (Alternative)

You can also manually set a password through the edit interface, but this does NOT force the user to change it:

1. Go to "System Admin" tab
2. Find user
3. Click "Edit"
4. Enter new password in the password field
5. Click "Save"

**Note**: With this method, the user will NOT be forced to change the password and can continue using this password indefinitely.

#### Troubleshooting Password Resets

**Admin Issues:**

- **Modal closed before copying password**
  - Solution: Reset the password again - system generates a new temporary password

- **User says temporary password doesn't work**
  - Verify they're entering it exactly as shown (case-sensitive)
  - Ensure they're using the most recent temporary password if reset multiple times
  - Check that user account is active (`is_active = true`)

- **Need to track who reset passwords**
  - Currently no audit log - consider implementing for security
  - Check database `updated_at` field on users table

**User Issues:**

- **User lost temporary password**
  - Solution: Reset password again for the user

- **User stuck on password change screen**
  - Verify they're entering the temporary password correctly
  - Check that new password meets requirements (8+ characters)
  - Ensure new password and confirmation match

- **User cannot access after password change**
  - Should not happen - contact development team
  - Verify `must_change_password` flag is FALSE in database
  - Check for JavaScript errors in browser console

### Deleting Users

**Warning:** This deletes the user and ALL their logs permanently.

1. Log in as sysop
2. Go to "System Admin" tab
3. Find user
4. Click "Delete"
5. Confirm deletion

### Disabling 2FA for Users

If a user loses access to their authenticator:

1. Access database directly
2. Run SQL command:

```sql
UPDATE users SET mfa_enabled = false, mfa_secret = NULL 
WHERE callsign = 'W1ABC';
```

---

## Database Administration

### Accessing the Database

**Docker:**
```bash
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby
```

**Local:**
```bash
psql -U logshackbaby -d logshackbaby
```

### Database Schema

**Tables:**
- `users` - User accounts with authentication
- `api_keys` - API key management
- `log_entries` - QSO records
- `upload_logs` - Upload history
- `sessions` - User sessions

### Useful SQL Queries

**View all users:**
```sql
SELECT id, callsign, email, role, mfa_enabled, created_at FROM users;
```

**Count logs per user:**
```sql
SELECT u.callsign, COUNT(l.id) as log_count 
FROM users u 
LEFT JOIN log_entries l ON u.id = l.user_id 
GROUP BY u.callsign 
ORDER BY log_count DESC;
```

**Recent uploads:**
```sql
SELECT u.callsign, ul.filename, ul.total_records, ul.uploaded_at 
FROM upload_logs ul 
JOIN users u ON ul.user_id = u.id 
ORDER BY ul.uploaded_at DESC 
LIMIT 10;
```

**Database size:**
```sql
SELECT pg_size_pretty(pg_database_size('logshackbaby'));
```

**Table sizes:**
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Database Maintenance

**Vacuum database:**
```sql
VACUUM ANALYZE;
```

**Reindex:**
```sql
REINDEX DATABASE logshackbaby;
```

**Check for bloat:**
```sql
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname='public';
```

---

## Backup and Restore

### Automated Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/logshackbaby"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Docker backup
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > \
  $BACKUP_DIR/logshackbaby_$DATE.sql

# Compress
gzip $BACKUP_DIR/logshackbaby_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: logshackbaby_$DATE.sql.gz"
```

Make executable:
```bash
chmod +x backup.sh
```

### Schedule Daily Backups

```bash
sudo crontab -e
```

Add:
```bash
0 2 * * * /path/to/backup.sh >> /var/log/logshackbaby_backup.log 2>&1
```

### Manual Backup

**Docker:**
```bash
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql
```

**Local:**
```bash
pg_dump -U logshackbaby logshackbaby > backup.sql
```

### Restore from Backup

**Docker:**
```bash
# Stop application
docker-compose stop app

# Restore
cat backup.sql | docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby

# Start application
docker-compose start app
```

**Local:**
```bash
# Stop application
./stop-local.sh

# Restore
psql -U logshackbaby logshackbaby < backup.sql

# Start application
./start-local.sh
```

### Backup Best Practices

- Automate daily backups
- Store backups off-site
- Test restore procedure regularly
- Keep multiple backup versions (7-30 days)
- Backup before major updates
- Include configuration files in backups

---

## Monitoring

### Health Checks

**Application health:**
```bash
curl http://localhost/api/health
```

**Database health (Docker):**
```bash
docker exec logshackbaby-db pg_isready -U logshackbaby
```

### Log Monitoring

**View real-time logs:**
```bash
# All services
docker-compose logs -f

# Application only
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

**Search logs:**
```bash
docker-compose logs app | grep ERROR
docker-compose logs app | grep "Upload successful"
```

### System Monitoring

**Container stats:**
```bash
docker stats
```

**Disk usage:**
```bash
# Docker volumes
docker system df -v

# Local disk
df -h
du -sh /var/lib/docker/volumes/
```

**Database connections:**
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'logshackbaby';
```

### Setting Up External Monitoring

**UptimeRobot, Pingdom, or similar:**
- Monitor URL: `http://your-domain/api/health`
- Check interval: 5 minutes
- Alert on: Non-200 response

**Prometheus/Grafana:**
- Add Flask metrics exporter
- Monitor response times, request counts, errors

---

## Security Hardening

### Firewall Configuration

**UFW (Ubuntu):**
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 5000/tcp  # Block direct app access
sudo ufw deny 5432/tcp  # Block database access
sudo ufw enable
```

**iptables:**
```bash
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
iptables -A INPUT -p tcp --dport 5432 -j DROP
```

### Fail2ban Setup

Protect against brute force attacks:

```bash
sudo apt-get install fail2ban
```

Create `/etc/fail2ban/jail.local`:
```ini
[logshackbaby]
enabled = true
port = http,https
filter = logshackbaby
logpath = /var/log/logshackbaby/*.log
maxretry = 5
bantime = 3600
```

### Rate Limiting

Add to NGINX configuration:
```nginx
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /api/login {
    limit_req zone=login burst=10 nodelay;
    proxy_pass http://app:5000;
}
```

### Security Checklist

- [ ] Strong passwords in `.env`
- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Database not exposed to internet
- [ ] Regular backups enabled
- [ ] Fail2ban installed
- [ ] Rate limiting configured
- [ ] Users encouraged to enable 2FA
- [ ] Regular security updates applied

---

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Verify backups completed
- Monitor disk space

**Weekly:**
- Review user activity
- Check failed login attempts
- Update statistics

**Monthly:**
- Update Docker images
- Review and delete old logs
- Test backup restore
- Vacuum database
- Review security logs

### Update Procedure

**Docker:**
```bash
# Pull latest images
docker-compose pull

# Stop services
docker-compose down

# Start with new images
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost/api/health
```

**Local:**
```bash
# Stop application
./stop-local.sh

# Update code
git pull  # or download new version

# Update dependencies
source venv/bin/activate
pip install -r backend/requirements.txt

# Start application
./start-local.sh
```

### Clean Up Old Data

**Delete logs older than X years:**
```sql
DELETE FROM log_entries 
WHERE uploaded_at < NOW() - INTERVAL '5 years';
```

**Vacuum after deletion:**
```sql
VACUUM ANALYZE log_entries;
```

### Rotate Logs

For local installations, rotate application logs:

```bash
# /etc/logrotate.d/logshackbaby
/var/log/logshackbaby/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 logshackbaby logshackbaby
}
```

---

## Troubleshooting

### Containers Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
- Port already in use
- .env file missing or invalid
- Docker daemon not running
- Permission issues

**Solutions:**
```bash
# Check what's using port 80
sudo lsof -i :80

# Restart Docker daemon
sudo systemctl restart docker

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Errors

**Check database health:**
```bash
docker exec logshackbaby-db pg_isready -U logshackbaby
```

**Check credentials:**
```bash
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby
```

**Restart database:**
```bash
docker-compose restart db
# Wait 10 seconds
docker-compose restart app
```

### Application Won't Start

**Check logs:**
```bash
docker-compose logs app
```

**Common issues:**
- Missing dependencies
- Database not ready
- Invalid configuration
- Port conflict

**Solutions:**
```bash
# Wait for database
docker-compose restart app

# Check environment variables
docker-compose config

# Rebuild
docker-compose build app --no-cache
docker-compose up -d app
```

### Upload Failures

**Check:**
- File format (must be valid ADIF)
- File size (max 16MB)
- Disk space
- Application logs

**Debug:**
```bash
# Check disk space
df -h

# View upload errors
docker-compose logs app | grep -i upload

# Test with sample file
curl -X POST http://localhost/api/logs/upload \
  -H "X-API-Key: test_key" \
  -F "file=@sample_log.adi"
```

### Performance Issues

**Check resource usage:**
```bash
docker stats
```

**Optimize:**
- Increase Gunicorn workers
- Add database indexes
- Vacuum database
- Increase RAM allocation

**Database optimization:**
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM log_entries WHERE user_id = 1;

-- Add indexes if needed
CREATE INDEX idx_log_entries_call ON log_entries(call);
CREATE INDEX idx_log_entries_band ON log_entries(band);
```

---

## Performance Tuning

### Gunicorn Workers

Edit `docker-compose.yml`:
```yaml
command: gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

**Formula:** workers = (2 x CPU cores) + 1

### PostgreSQL Tuning

Edit `docker-compose.yml`:
```yaml
services:
  db:
    environment:
      - POSTGRES_INITDB_ARGS="-E UTF8 --locale=C"
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
```

### NGINX Tuning

Edit `nginx/nginx.conf`:
```nginx
worker_processes auto;
worker_connections 1024;

gzip on;
gzip_types text/plain text/css application/json application/javascript;

client_body_buffer_size 10M;
client_max_body_size 20M;
```

---

## Deployment Checklist

Use this checklist when deploying to production:

### Pre-Deployment

- [ ] Server meets minimum requirements
- [ ] DNS configured (if using domain)
- [ ] Firewall rules planned
- [ ] SSL certificates obtained
- [ ] Backup strategy planned

### Installation

- [ ] Docker or PostgreSQL installed
- [ ] LogShackBaby installed
- [ ] .env file created with secure passwords
- [ ] Services started successfully
- [ ] Health endpoint responds

### Configuration

- [ ] SSL/TLS configured
- [ ] NGINX configured properly
- [ ] Firewall rules applied
- [ ] Backup script created and scheduled
- [ ] Log rotation configured

### Testing

- [ ] Health check passes
- [ ] User registration works
- [ ] Login works
- [ ] Upload test file works
- [ ] Export works
- [ ] 2FA setup works

### Security

- [ ] Strong passwords used
- [ ] Database not exposed to internet
- [ ] SSL certificate valid
- [ ] Firewall configured
- [ ] Fail2ban configured (optional)
- [ ] Rate limiting enabled

### Monitoring

- [ ] External monitoring configured
- [ ] Log monitoring set up
- [ ] Backup verification scheduled
- [ ] Alert system configured

### Documentation

- [ ] Admin contacts documented
- [ ] Credentials stored securely
- [ ] User instructions prepared
- [ ] Rollback plan documented

### Go-Live

- [ ] Announce to users
- [ ] Monitor for first 24 hours
- [ ] Be available for support
- [ ] Document any issues

---

**Congratulations! Your LogShackBaby server is ready for production use.**

*For user instructions, see USERGUIDE.md*  
*For development and API details, see DEVELOPMENT.md*

**73!** 📻✨
