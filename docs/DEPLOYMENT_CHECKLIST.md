# LogShackBaby Deployment Checklist

Use this checklist to ensure proper deployment of LogShackBaby.

LogShackBaby supports two deployment methods:
- **Docker Deployment** (containerized, recommended for production)
- **Local Deployment** (native installation, no Docker)

## Pre-Deployment

### Server Requirements (Docker Deployment)
- [ ] Docker 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Minimum 2GB RAM available
- [ ] Minimum 10GB disk space available
- [ ] Ports 80, 443, 5000 available (or alternative ports configured)
- [ ] Root/sudo access for Docker

### Server Requirements (Local Deployment)
- [ ] Python 3.8+ installed
- [ ] PostgreSQL 12+ installed
- [ ] Minimum 2GB RAM available
- [ ] Minimum 10GB disk space available
- [ ] Port 5000 available (or alternative port configured)
- [ ] Root/sudo access for PostgreSQL setup

### Network Requirements
- [ ] Static IP address or domain name configured
- [ ] DNS records pointing to server (if using domain)
- [ ] Firewall rules configured:
  - [ ] Port 80 (HTTP) open to internet
  - [ ] Port 443 (HTTPS) open to internet
  - [ ] Port 5000 only accessible locally or via Docker network
  - [ ] Port 5432 (PostgreSQL) blocked from internet

## Configuration

### Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Generate secure database password:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(16))"
  ```
- [ ] Generate secure Flask secret key:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Update `.env` with generated values
- [ ] Verify `.env` file permissions (should be 600):
  ```bash
  chmod 600 .env
  ```

### SSL/TLS Configuration (Production)
- [ ] Obtain SSL certificates (Let's Encrypt, commercial CA, etc.)
- [ ] Place certificates in `nginx/ssl/` directory:
  - [ ] cert.pem (certificate)
  - [ ] key.pem (private key)
- [ ] Update `nginx/nginx.conf` with SSL configuration
- [ ] Uncomment HTTPS server block in nginx.conf
- [ ] Update server_name with your domain
- [ ] Enable HTTP to HTTPS redirect

### Application Configuration
- [ ] Review `backend/app.py` configuration
- [ ] Verify `MAX_CONTENT_LENGTH` (default 16MB)
- [ ] Check `SQLALCHEMY_DATABASE_URI` in docker-compose.yml
- [ ] Confirm worker count in Dockerfile CMD (default: 4)

## Deployment Steps

### Docker Deployment

#### 1. Initial Deployment
- [ ] Clone/copy LogShackBaby to server:
  ```bash
  cd /opt
  git clone <repo> logshackbaby  # or copy files
  cd logshackbaby
  ```

#### 2. Run Installation Script
- [ ] Execute Docker installation:
  ```bash
  ./install-docker.sh
  ```
- [ ] Verify installation completed successfully

#### 3. Start Services
- [ ] Start containers:
  ```bash
  ./start-docker.sh
  ```
- [ ] Check container status:
  ```bash
  docker-compose ps
  ```
- [ ] Verify all containers are "Up" and healthy

### Local Deployment (No Docker)

#### 1. Initial Deployment
- [ ] Clone/copy LogShackBaby to server:
  ```bash
  cd /opt
  git clone <repo> logshackbaby  # or copy files
  cd logshackbaby
  ```

#### 2. Run Installation Script
- [ ] Execute local installation:
  ```bash
  ./install-local.sh
  ```
- [ ] Choose whether to create systemd service
- [ ] Verify installation completed successfully

#### 3. Start Application
- [ ] Start the application:
  ```bash
  ./start-local.sh
  ```
  OR if using systemd:
  ```bash
  sudo systemctl start logshackbaby
  ```
- [ ] Verify application is running:
  ```bash
  curl http://localhost:5000/api/health
  ```

### 4. Verify Deployment
- [ ] Check application logs:
  ```bash
  docker-compose logs app
  ```
- [ ] Check database logs:
  ```bash
  docker-compose logs db
  ```
- [ ] Test health endpoint:
  ```bash
  curl http://localhost/api/health
  ```
- [ ] Expected response: `{"status":"healthy"}`

### 5. Initialize Database
- [ ] Database tables are created automatically on first start
- [ ] Verify tables exist:
  ```bash
  docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby -c "\dt"
  ```
- [ ] Expected tables: users, api_keys, log_entries, upload_logs

### 6. Test Functionality
- [ ] Open web interface in browser
- [ ] Create test account
- [ ] Enable MFA on test account
- [ ] Create test API key
- [ ] Upload sample_log.adi
- [ ] Verify logs appear in dashboard

## Security Hardening

### Application Security
- [ ] Change default passwords in `.env`
- [ ] Verify SECRET_KEY is random and secure
- [ ] Enable HTTPS only (disable HTTP redirect in production)
- [ ] Review CORS settings in `backend/app.py`
- [ ] Disable debug mode (FLASK_ENV=production)

### Database Security
- [ ] Database only accessible via Docker network
- [ ] Strong database password set
- [ ] Regular backup schedule established
- [ ] Database logs reviewed for suspicious activity

### Network Security
- [ ] Firewall configured (ufw, iptables, etc.):
  ```bash
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw deny 5000/tcp
  ufw deny 5432/tcp
  ufw enable
  ```
- [ ] Fail2ban configured for brute-force protection
- [ ] Rate limiting configured in NGINX
- [ ] Consider adding Cloudflare or similar DDoS protection

### SSL/TLS Security
- [ ] Use TLS 1.2 or higher only
- [ ] Strong cipher suites configured
- [ ] HSTS header enabled
- [ ] SSL certificate auto-renewal configured (if using Let's Encrypt)

## Monitoring & Maintenance

### Logging
- [ ] Configure log rotation:
  ```bash
  # Add to /etc/logrotate.d/logshackbaby
  /var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
  }
  ```
- [ ] Set up centralized logging (optional)
- [ ] Monitor disk space usage

### Backups
- [ ] Automated database backup script:
  ```bash
  #!/bin/bash
  docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > \
    /backup/logshackbaby-$(date +%Y%m%d).sql
  ```
- [ ] Add to crontab:
  ```bash
  0 2 * * * /opt/logshackbaby/backup.sh
  ```
- [ ] Test backup restoration procedure
- [ ] Verify backups stored off-site

### Updates
- [ ] Subscribe to security advisories
- [ ] Regular update schedule (monthly recommended)
- [ ] Update procedure documented
- [ ] Rollback procedure documented

### Health Checks
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Monitor endpoint: `http://your-domain/api/health`
- [ ] Alert on downtime
- [ ] Monitor disk space
- [ ] Monitor database size
- [ ] Monitor CPU/RAM usage

## Production Checklist

### Before Go-Live
- [ ] All tests pass (see TESTING.md)
- [ ] SSL certificate valid and installed
- [ ] DNS configured correctly
- [ ] Backups tested and working
- [ ] Monitoring configured
- [ ] Documentation reviewed
- [ ] Admin accounts created
- [ ] MFA enabled on admin accounts

### Go-Live
- [ ] Announce to club members
- [ ] Provide registration instructions
- [ ] Share API documentation
- [ ] Monitor logs for first 24 hours
- [ ] Be available for support questions

### Post-Deployment
- [ ] Verify user registrations working
- [ ] Check upload functionality
- [ ] Monitor error logs
- [ ] Review performance metrics
- [ ] Collect user feedback

## Integration with Existing Infrastructure

### Existing NGINX Proxy
If using existing NGINX:
- [ ] Comment out nginx service in docker-compose.yml
- [ ] Add proxy configuration to existing NGINX
- [ ] Test proxy to localhost:5000
- [ ] Verify headers forwarded correctly

### Existing Docker Network
If integrating with existing Docker network:
- [ ] Update docker-compose.yml network configuration
- [ ] Connect to existing network:
  ```yaml
  networks:
    logshackbaby-network:
      external: true
      name: your-existing-network
  ```

### Existing PostgreSQL
If using existing PostgreSQL (not recommended):
- [ ] Remove db service from docker-compose.yml
- [ ] Update DATABASE_URL in .env
- [ ] Ensure network connectivity
- [ ] Create database and user manually
- [ ] Run migrations manually

## Troubleshooting

### Container Issues
- [ ] Check Docker daemon status: `systemctl status docker`
- [ ] Check Docker logs: `journalctl -u docker`
- [ ] Verify disk space: `df -h`
- [ ] Check Docker network: `docker network ls`

### Application Issues
- [ ] Review application logs: `docker-compose logs -f app`
- [ ] Check database connection
- [ ] Verify environment variables
- [ ] Test health endpoint

### Database Issues
- [ ] Check PostgreSQL logs: `docker-compose logs -f db`
- [ ] Verify database is healthy: `docker exec logshackbaby-db pg_isready`
- [ ] Check database connections: `docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby -c "SELECT * FROM pg_stat_activity;"`

### Network Issues
- [ ] Verify ports are listening: `netstat -tlnp | grep -E "80|443|5000"`
- [ ] Check firewall rules: `ufw status` or `iptables -L`
- [ ] Test connectivity: `curl -v http://localhost/api/health`
- [ ] Check DNS resolution

## Rollback Procedure

If deployment fails:
1. [ ] Stop containers: `docker-compose down`
2. [ ] Restore previous version
3. [ ] Restore database backup:
   ```bash
   docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < backup.sql
   ```
4. [ ] Restart containers: `docker-compose up -d`
5. [ ] Verify functionality
6. [ ] Document issues for review

## Support Contacts

Document your support contacts:
- [ ] Server administrator: __________________
- [ ] Database administrator: __________________
- [ ] Network administrator: __________________
- [ ] Club technical contact: __________________
- [ ] Emergency contact: __________________

## Sign-Off

Deployment completed by: __________________ Date: __________

Verified by: __________________ Date: __________

Production approved by: __________________ Date: __________

---

**Notes:**
- Keep this checklist for future reference
- Update as your deployment evolves
- Review quarterly for improvements
- Document any deviations from standard procedure

**Good luck with your deployment!** 🚀📻
