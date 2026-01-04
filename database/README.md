# PostgreSQL Database Configuration

This directory is reserved for PostgreSQL-specific configuration and initialization scripts.

## Database Schema

The database schema is automatically created by the Flask application on first startup using SQLAlchemy models.

## Tables

- **users** - User accounts with MFA support
- **api_keys** - API keys for programmatic log uploads
- **log_entries** - Individual QSO records from ADIF files
- **upload_logs** - History of file uploads

## Backup and Restore

### Backup
```bash
docker exec logshackbaby-db pg_dump -U logshackbaby logshackbaby > backup.sql
```

### Restore
```bash
docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < backup.sql
```

## Direct Database Access

```bash
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby
```

## Volume

Database data is stored in the Docker volume `postgres_data` for persistence.
