# Contest Templates Guide

## Overview

LogShackBaby includes three default contest templates designed to facilitate amateur radio competitions. These templates help ContestAdmin users create engaging contests from user log activity data.

## Available Contest Templates

### 1. Grid Square Globetrotter

**Contest Goal:** Work as many unique Maidenhead grid squares as possible in 30 days.

**Template Fields:**
- `user_callsign` - Participant's callsign
- `qso_date` - Date of contact (YYYYMMDD)
- `time_on` - Time contact started (HHMMSS)
- `call` - Station worked
- `gridsquare` - Maidenhead grid square of contacted station
- `band` - Frequency band used
- `mode` - Operating mode

**Usage Tips:**
- Set date filters for 30-day contest periods
- Export results and count unique `gridsquare` values per user
- Award points for each unique grid square worked
- Consider bonus points for rare grid squares

**Example Scoring:**
- 1 point per unique grid square
- Bonus: 5 points for 6-character grid squares (e.g., FN31pr)
- Winner: Most points in 30 days

**SQL Query to Count Unique Grids:**
```sql
SELECT user_callsign, COUNT(DISTINCT gridsquare) as unique_grids
FROM log_entries
WHERE qso_date >= '20260301' AND qso_date <= '20260331'
AND gridsquare IS NOT NULL
GROUP BY user_callsign
ORDER BY unique_grids DESC;
```

---

### 2. Band-Hopper

**Contest Goal:** Make at least one contact on as many different amateur bands as possible.

**Template Fields:**
- `user_callsign` - Participant's callsign
- `qso_date` - Date of contact
- `time_on` - Time contact started
- `call` - Station worked
- `band` - Frequency band (the key field!)
- `mode` - Operating mode
- `freq` - Specific frequency

**Usage Tips:**
- Award points for each unique band worked
- Typical amateur bands: 160m, 80m, 60m, 40m, 30m, 20m, 17m, 15m, 12m, 10m, 6m, 2m, 1.25m, 70cm, 33cm, 23cm
- Consider separate categories for HF (160m-10m) and VHF/UHF (6m and up)
- Bonus points for less common bands (WARC bands, microwave)

**Example Scoring:**
- 1 point per unique band worked
- Bonus: 3 points for WARC bands (60m, 30m, 17m, 12m)
- Bonus: 5 points for VHF/UHF bands
- Winner: Most total points

**SQL Query to Count Unique Bands:**
```sql
SELECT user_callsign, COUNT(DISTINCT band) as unique_bands,
       STRING_AGG(DISTINCT band, ', ' ORDER BY band) as bands_worked
FROM log_entries
WHERE band IS NOT NULL
GROUP BY user_callsign
ORDER BY unique_bands DESC;
```

---

### 3. Elmer's Choice (Mode Diversity)

**Contest Goal:** Rack up points across three categories: CW, Phone, and Digital modes (FT8/JS8/RTTY).

**Template Fields:**
- `user_callsign` - Participant's callsign
- `qso_date` - Date of contact
- `time_on` - Time contact started
- `call` - Station worked
- `mode` - Operating mode (the key field!)
- `band` - Frequency band
- `rst_sent` - Signal report sent
- `rst_rcvd` - Signal report received

**Usage Tips:**
- Group modes into three categories:
  - **CW Category:** CW, CWR
  - **Phone Category:** SSB, USB, LSB, FM, AM, DV (Digital Voice)
  - **Digital Category:** FT8, FT4, JS8, JS8CALL, RTTY, PSK31, PSK63, MFSK, JT65, WSPR

**Example Scoring System:**
- Basic: 1 point per QSO, must work at least one QSO in each category
- Balanced: Category scores multiplied together (CW × Phone × Digital)
- Example: 50 CW QSOs, 100 Phone QSOs, 75 Digital QSOs = 50 × 100 × 75 = 375,000 points
- This rewards balanced operation across all modes

**Alternative Scoring (Minimum Thresholds):**
- Each category must have at least 10 QSOs (threshold)
- Above threshold: 1 point per QSO in each category
- Total points = sum of all categories
- Encourages participation in all three modes

**SQL Query to Categorize Modes:**
```sql
SELECT user_callsign,
  COUNT(CASE WHEN mode IN ('CW', 'CWR') THEN 1 END) as cw_qsos,
  COUNT(CASE WHEN mode IN ('SSB', 'USB', 'LSB', 'FM', 'AM', 'DV') THEN 1 END) as phone_qsos,
  COUNT(CASE WHEN mode IN ('FT8', 'FT4', 'JS8', 'JS8CALL', 'RTTY', 'PSK31', 'PSK63', 'MFSK', 'JT65') THEN 1 END) as digital_qsos
FROM log_entries
WHERE mode IS NOT NULL
GROUP BY user_callsign
ORDER BY (
  COUNT(CASE WHEN mode IN ('CW', 'CWR') THEN 1 END) *
  COUNT(CASE WHEN mode IN ('SSB', 'USB', 'LSB', 'FM', 'AM', 'DV') THEN 1 END) *
  COUNT(CASE WHEN mode IN ('FT8', 'FT4', 'JS8', 'JS8CALL', 'RTTY', 'PSK31', 'PSK63', 'MFSK', 'JT65') THEN 1 END)
) DESC;
```

---

## Working with Templates

### Accessing Templates

As a ContestAdmin user, access templates through the API:

```bash
# List all available templates
curl -H "X-Session-Token: YOUR_TOKEN" \
  https://your-server/api/contestadmin/templates

# Get specific template details
curl -H "X-Session-Token: YOUR_TOKEN" \
  https://your-server/api/contestadmin/templates/1
```

### Creating a Contest from a Template

1. **Select a template** that matches your contest goals
2. **Customize filters** to define the contest period and scope
3. **Run the template** to generate the report
4. **Export the results** for scoring and analysis

**Example: Running Grid Square Globetrotter for March 2026:**

```bash
# Run template with date filter
curl -X POST -H "X-Session-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_from": "2026-03-01", "date_to": "2026-03-31"}' \
  https://your-server/api/contestadmin/templates/1/run
```

### Creating Custom Templates

You can create your own contest templates:

```bash
curl -X POST -H "X-Session-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekend Warrior",
    "description": "Work stations only on Saturday and Sunday",
    "fields": ["user_callsign", "qso_date", "call", "band", "mode"],
    "filters": {},
    "shared_with_role": "contestadmin"
  }' \
  https://your-server/api/contestadmin/templates
```

### Customizing Filters

Templates support the following filter options:

- `date_from` - Start date (YYYY-MM-DD format)
- `date_to` - End date (YYYY-MM-DD format)
- `bands` - Array of bands (e.g., `["20m", "15m", "10m"]`)
- `modes` - Array of modes (e.g., `["CW", "FT8"]`)
- `user_ids` - Array of user IDs to include

**Example: Band-Hopper for HF Bands Only:**

```sql
UPDATE report_templates 
SET filters = '{"bands": ["160m", "80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"]}'::jsonb
WHERE name = 'Band-Hopper';
```

---

## Contest Administration Best Practices

### 1. Pre-Contest Setup
- Announce contest rules and dates in advance
- Share the template name so participants know what data to log
- Set clear scoring rules and goals
- Test the template with your own logs first

### 2. During Contest
- Monitor participation through periodic reports
- Be available to answer questions about logging requirements
- Consider posting leaderboards to encourage participation

### 3. Post-Contest
- Run the final report as soon as the contest ends
- Verify results for accuracy
- Announce winners and top performers
- Share statistics (total QSOs, unique entities worked, etc.)

### 4. Data Quality
- Encourage participants to log complete information
- Grid squares should be 4 or 6 characters (e.g., FN31 or FN31pr)
- Band designations should be standardized (20m not 20)
- Mode names should follow ADIF standards

---

## Exporting Results

After running a template, you can export results to various formats:

### CSV Export (for spreadsheets)
```bash
curl -H "X-Session-Token: YOUR_TOKEN" \
  "https://your-server/api/contestadmin/templates/1/run" \
  | jq -r '.report[] | [.user_callsign, .qso_date, .call, .gridsquare] | @csv'
```

### JSON Export (for further processing)
```bash
curl -H "X-Session-Token: YOUR_TOKEN" \
  "https://your-server/api/contestadmin/templates/1/run" \
  > contest_results.json
```

---

## Installation

Contest templates are automatically included in new LogShackBaby installations. If you need to reinstall them:

**Method 1: SQL File**
```bash
docker exec -i logshackbaby-db psql -U logshackbaby logshackbaby < database/contest_templates.sql
```

**Method 2: Python Script**
```bash
python3 init_templates.py
```

Both methods are idempotent (safe to run multiple times without creating duplicates).

---

## Support

For questions or custom contest ideas:
- Review the API documentation at `/api/docs`
- Check the main README.md for application setup
- Review USERGUIDE.md for end-user features

Happy contesting! 73 de LogShackBaby
