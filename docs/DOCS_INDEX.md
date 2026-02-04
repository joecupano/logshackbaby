# 📚 LogShackBaby Documentation Index

Welcome to the LogShackBaby documentation! This index will help you find what you need quickly.

## 🚀 Getting Started

**New to LogShackBaby? Start here:**

1. **[OVERVIEW.md](OVERVIEW.md)** - Project overview and statistics
2. **[README.md](../README.md)** - Complete setup guide and user documentation
3. Choose your deployment method:
   - **Docker**: Run `./install-docker.sh` then `./start-docker.sh`
   - **Local**: Run `./install-local.sh` then `./start-local.sh`

## 📖 Documentation Files

### Setup & Installation
- **[README.md](../README.md)** - Main documentation
  - Features overview
  - Installation instructions (Docker & Local)
  - Configuration guide
  - User guide
  - Maintenance procedures

- **Installation Scripts**
  - `install-docker.sh` - Automated Docker installation
  - `start-docker.sh` - Start Docker containers
  - `stop-docker.sh` - Stop Docker containers
  - `install-local.sh` - Automated local installation (no Docker)
  - `start-local.sh` - Start local application
  - `stop-local.sh` - Stop local application

- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Production deployment
  - Pre-deployment requirements (Docker & Local)
  - Security hardening
  - Step-by-step deployment
  - Monitoring setup
  - Rollback procedures

### Development & Testing
- **[TESTING.md](TESTING.md)** - Testing procedures
  - Manual testing steps
  - Automated test scripts
  - API testing examples
  - Performance testing
  - Security testing

- **[API_EXAMPLES.md](API_EXAMPLES.md)** - API usage examples
  - cURL examples
  - Python code samples
  - Bash scripts
  - Integration guides

### Reference
- **[OVERVIEW.md](OVERVIEW.md)** - Complete project overview
  - Architecture diagrams
  - Technology stack
  - File structure
  - Security features
  - API endpoint list

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project summary
  - What's included
  - Quick reference
  - Next steps

- **[ADIF_FIELDS_UPDATE.md](ADIF_FIELDS_UPDATE.md)** - ADIF field processing details
  - Comprehensive ADIF 3.1.6 support
  - Field storage strategy
  - Additional fields display
  - Testing procedures

## 📂 Component Documentation

### Backend
- **[backend/README.md](backend/)** - Backend code location
  - app.py - Main Flask application
  - models.py - Database models
  - auth.py - Authentication system
  - adif_parser.py - ADIF file parser

### Frontend
- **[frontend/](frontend/)** - Frontend code location
  - index.html - Main UI
  - css/style.css - Styling
  - js/app.js - JavaScript application

### Database
- **[database/README.md](database/README.md)** - Database documentation
  - Schema information
  - Backup/restore procedures
  - Direct access commands

### Infrastructure
- **[nginx/ssl/README.md](nginx/ssl/README.md)** - SSL setup
  - Certificate installation
  - Self-signed certificate generation

## 🎯 Quick Links by Task

### I want to...

**Deploy LogShackBaby**
→ Start with [README.md](README.md) → Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

**Test the application**
→ Read [TESTING.md](TESTING.md) → Run automated tests

**Use the API**
→ Check [API_EXAMPLES.md](API_EXAMPLES.md) → Adapt code samples

**Understand the project**
→ Read [OVERVIEW.md](OVERVIEW.md) → Review architecture

**Configure SSL**
→ Follow [nginx/ssl/README.md](nginx/ssl/README.md)

**Backup database**
→ See [database/README.md](database/README.md) → Use backup commands

**Integrate with logging software**
→ Read [API_EXAMPLES.md](API_EXAMPLES.md) → Use Python examples

**Troubleshoot issues**
→ Check [README.md](README.md) troubleshooting section → Review logs

## 📝 Documentation by Role

### For Club Members (Users)
1. [README.md](README.md) - User Guide section
2. Account registration process
3. MFA setup instructions
4. Log upload guide

### For System Administrators
1. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. [README.md](README.md) - Deployment & Maintenance sections
3. [database/README.md](database/README.md)
4. [nginx/ssl/README.md](nginx/ssl/README.md)

### For Developers
1. [OVERVIEW.md](OVERVIEW.md) - Architecture
2. [TESTING.md](TESTING.md) - Test procedures
3. [API_EXAMPLES.md](API_EXAMPLES.md) - Integration examples
4. Backend code files (app.py, models.py, etc.)

### For Power Users
1. [API_EXAMPLES.md](API_EXAMPLES.md)
2. [README.md](README.md) - API Documentation section
3. Automated upload scripts

## 🔍 Search by Topic

### Authentication
- User registration: [README.md](README.md)
- MFA setup: [README.md](README.md) + [backend/auth.py](backend/auth.py)
- API keys: [API_EXAMPLES.md](API_EXAMPLES.md)

### ADIF Logs
- Upload process: [README.md](README.md)
- ADIF format: [backend/adif_parser.py](backend/adif_parser.py)
- Deduplication: [backend/adif_parser.py](backend/adif_parser.py)

### Database
- Schema: [backend/models.py](backend/models.py)
- Backup: [database/README.md](database/README.md)
- Maintenance: [README.md](README.md)

### Docker
- Configuration: [docker-compose.yml](docker-compose.yml)
- Deployment: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Troubleshooting: [README.md](README.md)

### Security
- MFA: [backend/auth.py](backend/auth.py)
- SSL/TLS: [nginx/ssl/README.md](nginx/ssl/README.md)
- Hardening: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## 📊 Documentation Statistics

- **Total Documentation**: ~6,000+ lines
- **Number of Documents**: 8 markdown files
- **Code Comments**: Extensive inline documentation
- **Examples**: 20+ code examples
- **Procedures**: 15+ step-by-step guides

## 🆘 Need Help?

### Common Questions

**Q: How do I start LogShackBaby?**
A: Run `./start.sh` or see [README.md](README.md) Quick Start

**Q: How do I upload logs?**
A: See [API_EXAMPLES.md](API_EXAMPLES.md) or use the web UI

**Q: How do I enable SSL?**
A: Follow [nginx/ssl/README.md](nginx/ssl/README.md)

**Q: How do I backup the database?**
A: See [database/README.md](database/README.md) or [README.md](README.md) Maintenance section

**Q: Something isn't working!**
A: Check [README.md](README.md) Troubleshooting or [TESTING.md](TESTING.md)

### Troubleshooting Flow
1. Check [README.md](README.md) Troubleshooting section
2. Review container logs: `docker-compose logs`
3. Run tests from [TESTING.md](TESTING.md)
4. Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## 🎓 Learning Path

### Beginner
1. Read [OVERVIEW.md](OVERVIEW.md) - Understand the project
2. Follow [README.md](README.md) Quick Start - Get it running
3. Try [TESTING.md](TESTING.md) - Test basic functionality
4. Upload sample_log.adi - See it work!

### Intermediate
1. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Production setup
2. Configure SSL from [nginx/ssl/README.md](nginx/ssl/README.md)
3. Try [API_EXAMPLES.md](API_EXAMPLES.md) - API integration
4. Set up backups from [database/README.md](database/README.md)

### Advanced
1. Review all backend code (app.py, models.py, etc.)
2. Implement custom integrations using [API_EXAMPLES.md](API_EXAMPLES.md)
3. Optimize performance
4. Contribute enhancements

## 📅 Regular Reference

### Daily Operations
- Check health: `curl http://localhost/api/health`
- View logs: `docker-compose logs -f`
- Monitor uploads: Web UI → Upload tab

### Weekly Tasks
- Review error logs
- Check disk space
- Verify backups

### Monthly Tasks
- Update containers: `docker-compose pull && docker-compose up -d`
- Review security
- Test restore procedure

## 🔗 External Resources

### ADIF Format
- Official Specification: http://www.adif.org/
- Field reference

### Amateur Radio
- ARRL: http://www.arrl.org/
- QRZ: https://www.qrz.com/

### Technologies
- Docker: https://docs.docker.com/
- Flask: https://flask.palletsprojects.com/
- PostgreSQL: https://www.postgresql.org/docs/

## 📋 File Listing

```
Documentation Files:
├── README.md                    Main documentation
├── OVERVIEW.md                  Project overview
├── PROJECT_SUMMARY.md           Quick summary
├── API_EXAMPLES.md              API usage examples
├── TESTING.md                   Testing guide
├── DEPLOYMENT_CHECKLIST.md      Deployment guide
├── DOCS_INDEX.md                This file
├── sample_log.adi               Sample ADIF file
└── start.sh                     Quick start script

Component Documentation:
├── backend/
│   ├── app.py                   (with inline docs)
│   ├── models.py                (with inline docs)
│   ├── auth.py                  (with inline docs)
│   └── adif_parser.py          (with inline docs)
├── database/
│   └── README.md                Database guide
└── nginx/
    └── ssl/
        └── README.md            SSL setup guide
```

## ✅ Documentation Checklist

Before deployment, ensure you've read:
- [ ] README.md - Setup guide
- [ ] DEPLOYMENT_CHECKLIST.md - Production steps
- [ ] API_EXAMPLES.md - If using API
- [ ] TESTING.md - Test procedures

## 💡 Tips

- **Bookmark this file** for quick reference
- **Start with README.md** for initial setup
- **Use Ctrl+F** to search within documents
- **Follow links** to jump between related topics
- **Check examples** in API_EXAMPLES.md for code

## 🎉 You're Ready!

All documentation is complete and comprehensive. Pick your starting point above and dive in!

**73!** 📻✨

---

*Last Updated: January 4, 2026*
*LogShackBaby Version: 1.0.0*
