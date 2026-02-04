# SSL Certificate Directory

**Note:** This directory is only used for Docker deployments with NGINX reverse proxy.

Place your SSL certificates in this directory:

- `cert.pem` - Your SSL certificate
- `key.pem` - Your SSL private key

If using Let's Encrypt or another certificate provider, point to those certificates in the nginx.conf file.

For testing purposes, you can generate a self-signed certificate:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem
```

## Local Deployment

For local deployments (without Docker), you can use a separate NGINX installation or a reverse proxy like Caddy to handle SSL termination. The application runs on port 5000 by default.

**Important**: Never commit actual SSL certificates to version control!
