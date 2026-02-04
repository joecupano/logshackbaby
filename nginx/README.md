# Nginx Configuration

This directory contains the Nginx reverse proxy configuration for LogShackBaby.

## Files

### nginx.conf

The main Nginx configuration file that serves as the reverse proxy for the LogShackBaby application. This file:

- **Routes API requests** to the appropriate backend services
- **Handles load balancing** between microservices
- **Configures HTTP/HTTPS** servers
- **Manages proxy settings** and timeouts

#### Key Configuration Sections

**Upstream Services:**
- `logshackbaby_backend` - Main application backend (app:5000)
- `contest_service` - Contest microservice (contest:5001)

**HTTP Server (Port 80):**
- Currently configured for local testing
- Routes `/api/contests` to the contest service
- Routes all other requests to the main backend
- Extended timeouts (300s) for file uploads and processing
- Includes a commented redirect to HTTPS for production use

**HTTPS Server (Port 443):**
- Commented out by default for development
- Configured for production use with SSL/TLS
- Supports HTTP/2
- Uses TLS 1.2 and 1.3 protocols
- Requires SSL certificates in the `ssl/` directory

**Features:**
- Gzip compression for various content types
- Client max body size of 20M (for log file uploads)
- Custom timeout configurations for long-running operations
- Proper proxy headers for backend services

### ssl/

Directory for SSL certificates. See [ssl/README.md](ssl/README.md) for details on certificate setup.

## Usage

### Development

The default configuration serves HTTP on port 80 and proxies requests to the backend services. No SSL configuration is required for local development.

### Production Deployment

For production use:

1. **Enable HTTPS redirect** - Uncomment the redirect line in the HTTP server block:
   ```nginx
   return 301 https://$host$request_uri;
   ```

2. **Configure HTTPS** - Uncomment the HTTPS server block and update:
   - `server_name` with your domain
   - SSL certificate paths if not using the default locations

3. **Add SSL certificates** - Place your SSL certificates in the `ssl/` directory:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

4. **Restart Nginx** - Reload the configuration:
   ```bash
   docker-compose restart nginx
   ```

## Docker Integration

This configuration is used by the Nginx container defined in `docker-compose.yml`. The configuration file is mounted as a volume into the Nginx container at runtime.

## Troubleshooting

- **502 Bad Gateway**: Check that backend services (app, contest) are running
- **504 Gateway Timeout**: Consider increasing timeout values if processing large files
- **File upload failures**: Verify `client_max_body_size` is sufficient
- **SSL issues**: Ensure certificates are valid and paths are correct in the HTTPS block

## Related Documentation

- [Deployment Checklist](../docs/DEPLOYMENT_CHECKLIST.md)
- [Project Overview](../docs/OVERVIEW.md)
