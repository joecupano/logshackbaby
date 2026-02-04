# PostgreSQL Database Configuration

This directory is reserved for PostgreSQL-specific configuration and initialization scripts.

## Database Schema

The database schema is automatically created by the Flask application on first startup using SQLAlchemy models.

## Tables

- **users** - User accounts with MFA support and role-based access control
  - Columns: id, callsign, email, password_hash, mfa_secret, mfa_enabled, role, created_at, last_login, is_active
  - Roles: user (default), logadmin, sysop
- **sessions** - Database-backed user sessions for multi-worker support
  - Columns: id, session_token, user_id, mfa_required, mfa_verified, created_at, last_activity
- **api_keys** - API keys for programmatic log uploads
- **log_entries** - Individual QSO records from ADIF files
- **upload_logs** - History of file uploads

## Backup and Restore

### Docker Deployment

**Backup:**
```bash
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql
```

**Restore:**
```bash
docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < backup.sql
```

**Direct Database Access:**
```bash
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby
```

### Local Deployment

**Backup:**
```bash
sudo -u postgres pg_dump logshackbaby > backup.sql
```

**Restore:**
```bash
sudo -u postgres psql logshackbaby < backup.sql
```

**Direct Database Access:**
```bash
sudo -u postgres psql -d logshackbaby
```

## Storage

- **Docker**: Database data is stored in the Docker volume `postgres_data` for persistence
- **Local**: Database data is stored in PostgreSQL's default data directory (typically `/var/lib/postgresql/`)
