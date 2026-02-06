# PostgreSQL Database Configuration

This directory is reserved for PostgreSQL-specific configuration and initialization scripts.

## Database Schema

The database schema is automatically created by the Flask application on first startup using SQLAlchemy models.

## Tables

- **users** - User accounts with MFA support and role-based access control
  - Columns: id, callsign, email, password_hash, mfa_secret, mfa_enabled, role, created_at, last_login, is_active
  - Roles: user (default), contestadmin, logadmin, sysop
- **sessions** - Database-backed user sessions for multi-worker support
  - Columns: id, session_token, user_id, mfa_required, mfa_verified, created_at, last_activity
- **api_keys** - API keys for programmatic log uploads
- **log_entries** - Individual QSO records from ADIF files
- **upload_logs** - History of file uploads
- **report_templates** - Report templates for ContestAdmin users
  - Columns: id, user_id, name, description, fields, filters, is_global, shared_with_role, created_at, updated_at

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

## Contest Templates

The `contest_templates.sql` file contains default global report templates for ContestAdmin users:

1. **Grid Square Globetrotter** - Track unique Maidenhead grid squares (30-day contests)
2. **Band-Hopper** - Make contacts on as many different amateur bands as possible
3. **Elmer's Choice (Mode Diversity)** - Work across CW, Phone, and Digital modes

### Installing Contest Templates

**Docker Deployment:**
```bash
docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < database/contest_templates.sql
```

**Local Deployment:**
```bash
sudo -u postgres psql logshackbaby < database/contest_templates.sql
```

**Python Script (Alternative):**
```bash
python3 init_templates.py
```

The templates are designed to be included by default in new installations and can be re-imported at any time without creating duplicates (uses `ON CONFLICT DO NOTHING`).
