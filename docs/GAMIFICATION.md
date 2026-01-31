# Gamification & Contest Management

## Overview
The LogShackBaby Amateur Radio Log Server now includes a comprehensive gamification system for creating contests and competitions based on log entries. This feature allows clubs to engage members through friendly competition and leaderboards.

## Architecture

### New Contest Service Container
A dedicated microservice (`contest`) runs separately from the main application:
- **Port**: 5001
- **Service**: `backend/contest_service.py`
- **Dockerfile**: `backend/Dockerfile.contest`
- **Database**: Shares the same PostgreSQL database as the main app

### Database Models
Three new models added to `backend/models.py`:

1. **Contest** - Stores contest definitions
   - Name, description, date range
   - Rules (bands, modes, filters)
   - Scoring configuration
   - Active/inactive status

2. **ContestEntry** - Links log entries to contests
   - References Contest and LogEntry
   - Stores calculated points
   - Validation status

## Authorization & Roles

### Contest Admin Role
Users with `contestadmin` role (or higher: `logadmin`, `sysop`) can:
- Create new contests
- Edit/delete contests
- Populate contests with eligible QSOs
- View all contest management features

### Regular Users
Users with `user` role can:
- View all active contests
- View leaderboards
- See detailed contest entries for all participants
- Cannot create or modify contests

### Role Hierarchy
The system uses a role hierarchy (already implemented in `User.has_role()`):
- `user` (0) - Basic access
- `contestadmin` (1) - Contest management
- `logadmin` (2) - Full log management
- `sysop` (3) - System administration

## API Endpoints

All contest endpoints are prefixed with `/api/contests` and routed through the contest service.

### Contest Management (contestadmin only)

#### Create Contest
```http
POST /api/contests
Content-Type: application/json
X-Session-Token: <session-token>

{
  "name": "2026 Winter Sprint",
  "description": "Club winter activity contest",
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "rules": {
    "bands": ["20M", "40M", "80M"],
    "modes": ["SSB", "CW", "FT8"]
  },
  "scoring": {
    "qso_points": 1,
    "band_multiplier": {"20M": 2, "40M": 1.5},
    "mode_bonus": {"CW": 2, "FT8": 1}
  },
  "is_active": true
}
```

#### Update Contest
```http
PUT /api/contests/{contest_id}
```

#### Delete Contest
```http
DELETE /api/contests/{contest_id}
```

#### Populate Contest
```http
POST /api/contests/{contest_id}/populate
```
Scans all user logs and automatically creates contest entries for QSOs that match the contest rules.

### Leaderboards (all authenticated users)

#### List Contests
```http
GET /api/contests
```

#### Get Contest Details
```http
GET /api/contests/{contest_id}
```

#### Get Leaderboard
```http
GET /api/contests/{contest_id}/leaderboard
```
Returns ranked list of participants with QSO counts and points.

#### Get User Contest Details
```http
GET /api/contests/{contest_id}/leaderboard/{user_id}
```
Returns detailed QSO list for a specific user in a contest.

## Frontend Pages

### Contest Management (`contest.html`)
- **Access**: contestadmin role required
- **Features**:
  - Create/edit/delete contests
  - Configure scoring rules
  - Populate contests with eligible QSOs
  - Visual contest cards with status badges
  - Direct links to leaderboards

### Leaderboard View (`leaderboard.html`)
- **Access**: All authenticated users
- **Features**:
  - Contest selector dropdown
  - Ranked leaderboard with medals (🥇🥈🥉)
  - Click-through to detailed QSO lists
  - Total QSOs and points per participant
  - Highlighted top 3 positions

## Contest Scoring System

### Base Scoring
- Each QSO has a base point value (configured per contest)

### Multipliers
- **Band Multiplier**: Different bands can award different multipliers
- **Mode Bonus**: Additional points for specific modes (e.g., CW bonus)

### Example Scoring
```json
{
  "qso_points": 1,
  "band_multiplier": {
    "20M": 2,
    "40M": 1.5,
    "80M": 1
  },
  "mode_bonus": {
    "CW": 2,
    "FT8": 1
  }
}
```

A CW QSO on 20M would score: `1 * 2 (band) + 2 (mode) = 4 points`

## Deployment

### Development Mode
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production Mode
```bash
docker-compose up -d
```

### Container Health Check
```bash
curl http://localhost:5001/health
```

### Database Migrations
The Contest service shares the database with the main app. Run migrations on the main app container:
```bash
docker exec -it logshackbaby-app flask --app app init-db
```

## Configuration

### Environment Variables
The contest service uses the same environment variables as the main app:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key for sessions
- `FLASK_ENV` - development/production

### NGINX Routing
The nginx configuration routes contest API calls to the contest service:
- `/api/contests/*` → contest service (port 5001)
- All other routes → main app (port 5000)

## Usage Workflow

### For Contest Admins

1. **Create a Contest**
   - Navigate to Contest Management page
   - Click "Create New Contest"
   - Fill in name, dates, rules, and scoring
   - Save

2. **Populate Contest**
   - Click "Populate" button on contest card
   - System scans all logs and creates entries for eligible QSOs
   - Automatically calculates points based on scoring rules

3. **Monitor Leaderboard**
   - Click "Leaderboard" button on contest card
   - View real-time rankings
   - Click on callsigns to see detailed QSO lists

### For Regular Users

1. **View Active Contests**
   - Navigate to Leaderboards page
   - Select a contest from dropdown

2. **Check Rankings**
   - See your position relative to others
   - View total QSOs and points

3. **Review Details**
   - Click on any callsign to see their contest QSOs
   - Compare bands, modes, and points

## Future Enhancements

Potential additions to the gamification system:
- Real-time updates via WebSocket
- Export leaderboards to PDF/CSV
- Contest templates for common contest types
- Achievements and badges
- Team competitions
- Multi-operator scoring
- Automated contest announcements
- Email notifications for rankings
- Historical contest archive
- Advanced filtering and search

## Security Considerations

- All endpoints require authentication via session token
- Role-based access control enforced at API level
- Contest admins cannot modify other users' logs
- Contest deletion cascades to entries (be careful!)
- SQL injection protection via SQLAlchemy ORM
- XSS protection via HTML escaping in frontend

## Troubleshooting

### Contest service not starting
```bash
# Check logs
docker logs logshackbaby-contest

# Verify database connection
docker exec -it logshackbaby-contest python -c "from models import db; print('DB OK')"
```

### Leaderboard not loading
- Check browser console for API errors
- Verify session token is valid
- Ensure contest service is running on port 5001

### Populate not working
- Verify log entries exist in database
- Check contest date range includes log entries
- Review contest rules (bands/modes filters)

## Support

For issues, feature requests, or questions about the gamification system, contact your club administrator or check the project documentation.
