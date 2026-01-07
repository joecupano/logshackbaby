# Quick Start Guide: Contest & Gamification System

## For Club Administrators

### 1. Grant Contest Admin Rights
First, promote a user to contestadmin role using the database or admin tools:

```sql
-- Connect to database
docker exec -it logshackbaby-db psql -U logshackbaby -d logshackbaby

-- Promote user to contestadmin
UPDATE users SET role = 'contestadmin' WHERE callsign = 'W1ABC';
```

### 2. Start the Services
```bash
# Development mode (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production mode
docker-compose up -d --build
```

### 3. Create Your First Contest
1. Log in as a contestadmin user
2. Navigate to **Contest Management** page
3. Click **"Create New Contest"**
4. Fill in the details:
   - **Name**: e.g., "2026 Winter Sprint"
   - **Start/End dates**: Contest period
   - **Base QSO Points**: Default 1
   - **Status**: Active
5. Click **"Save Contest"**

### 4. Populate the Contest
1. On the contest card, click **"Populate"**
2. System will scan all logs and add eligible QSOs
3. View results: "Added X new entries"

### 5. View Leaderboard
1. Click **"Leaderboard"** button on contest card
2. See rankings with medals for top 3
3. Click any callsign to see their detailed QSO log

## For Regular Users

### Viewing Leaderboards
1. Log in to LogShackBaby
2. Navigate to **"Leaderboards"** in the navigation
3. Select a contest from the dropdown
4. View your ranking and others
5. Click on callsigns to see detailed contest entries

## API Base URLs

When running locally:
- Main App: `http://localhost:5000`
- Contest Service: `http://localhost:5001`
- NGINX (if using): `http://localhost:80`

When using NGINX, all requests go through port 80:
- Contest APIs: `http://localhost/api/contests/*`
- Main APIs: `http://localhost/api/*`

## Example Contest Configuration

### Simple Contest
```json
{
  "name": "Weekend Sprint",
  "description": "48-hour weekend activity",
  "start_date": "2026-01-10T00:00:00Z",
  "end_date": "2026-01-12T23:59:59Z",
  "scoring": {
    "qso_points": 1
  },
  "is_active": true
}
```

### Advanced Contest with Rules
```json
{
  "name": "HF Challenge",
  "description": "HF bands only, extra points for CW",
  "start_date": "2026-02-01T00:00:00Z",
  "end_date": "2026-02-28T23:59:59Z",
  "rules": {
    "bands": ["20M", "40M", "80M", "160M"],
    "modes": ["SSB", "CW", "FT8", "RTTY"]
  },
  "scoring": {
    "qso_points": 1,
    "band_multiplier": {
      "20M": 1.5,
      "40M": 1.5,
      "80M": 2,
      "160M": 3
    },
    "mode_bonus": {
      "CW": 3,
      "RTTY": 2,
      "FT8": 1
    }
  },
  "is_active": true
}
```

## Troubleshooting

### Service Not Starting
```bash
# Check contest service logs
docker logs logshackbaby-contest

# Restart services
docker-compose restart contest
```

### Database Not Updated
```bash
# Run migrations
docker exec -it logshackbaby-app flask --app app init-db
```

### Port Conflicts
If port 5001 is already in use:
1. Stop conflicting service
2. Or edit docker-compose.yml to use different port

### Permission Issues
If you see "Insufficient permissions":
- Verify user role is 'contestadmin' or higher
- Check session token is valid
- Try logging out and back in

## Tips for Contest Success

1. **Set Clear Date Ranges**: Make sure contest dates align with club activities
2. **Test Populate**: Run populate after creating contest to verify rules work
3. **Monitor Regularly**: Check leaderboards during contest period
4. **Communicate**: Announce contests to club members via email/newsletter
5. **Archive Old Contests**: Set inactive=false for concluded contests

## Next Steps

- Read full documentation: [GAMIFICATION.md](GAMIFICATION.md)
- Configure SSL for production use
- Set up automated backups of contest data
- Create contest templates for recurring events
- Export leaderboards for club newsletters

## API Testing with curl

### List Contests
```bash
curl -H "X-Session-Token: YOUR_TOKEN" \
  http://localhost:5001/api/contests
```

### Get Leaderboard
```bash
curl -H "X-Session-Token: YOUR_TOKEN" \
  http://localhost:5001/api/contests/1/leaderboard
```

### Create Contest (contestadmin only)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: YOUR_TOKEN" \
  -d '{"name":"Test Contest","start_date":"2026-01-01T00:00:00Z","end_date":"2026-01-31T23:59:59Z"}' \
  http://localhost:5001/api/contests
```

## Support
For questions or issues, see [GAMIFICATION.md](GAMIFICATION.md) or contact your system administrator.
