# LogShackBaby User Guide

**Version 1.0.0** | Last Updated: February 5, 2026

A comprehensive guide for amateur radio operators using LogShackBaby to manage their QSO logs.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Your Account](#creating-your-account)
- [Logging In](#logging-in)
- [Dashboard Overview](#dashboard-overview)
- [Uploading Logs](#uploading-logs)
- [Viewing and Searching Logs](#viewing-and-searching-logs)
- [Understanding ADIF Fields](#understanding-adif-fields)
- [Exporting Logs](#exporting-logs)
- [Managing API Keys](#managing-api-keys)
- [Enabling Two-Factor Authentication](#enabling-two-factor-authentication)
- [User Roles](#user-roles)
- [Contest Administration](#contest-administration)
- [Integrating with Logging Software](#integrating-with-logging-software)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

LogShackBaby is a web-based Amateur Radio log server that allows you to:
- Upload and store your QSO logs in ADIF format
- Search and filter your contacts
- View statistics about your operating activity
- Export logs in ADIF format
- Access your logs from anywhere with an internet connection
- Securely manage your data with optional two-factor authentication

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection to access the server
- ADIF-formatted log files from your logging software

### Accessing LogShackBaby

Open your web browser and navigate to:
- If running locally: `http://localhost:5000`
- If using Docker with NGINX: `http://localhost`
- If deployed on a server: `http://your-server-address` (ask your administrator)

---

## Creating Your Account

1. **Navigate to the Registration Page**
   - Click the "Register" link on the login page

2. **Fill in Your Information**
   - **Callsign**: Your amateur radio callsign (e.g., W1ABC, K2DEF)
   - **Email**: Your email address
   - **Password**: A strong password (minimum 8 characters recommended)
   - **Confirm Password**: Re-enter your password

3. **Submit Registration**
   - Click "Register"
   - You'll be redirected to the login page upon successful registration

4. **First User Benefits**
   - The first person to register automatically becomes a **sysop** (system administrator)
   - Subsequent users register as regular **users** by default
   - Sysops can promote other users to different roles

---

## Logging In

1. **Enter Your Credentials**
   - **Callsign**: Your registered callsign
   - **Password**: Your password

2. **Two-Factor Authentication** (if enabled)
   - Enter the 6-digit code from your authenticator app
   - Codes refresh every 30 seconds

3. **Access Granted**
   - You'll be taken to your dashboard upon successful login

---

## Dashboard Overview

The dashboard has several tabs depending on your user role:

### My Logs Tab
- View all your QSO records
- Search and filter contacts
- See quick statistics (total QSOs, bands, modes)

### Upload Tab
- Upload new ADIF log files
- View upload history
- See statistics for each upload (new contacts, duplicates, errors)

### API Keys Tab
- Create API keys for programmatic log uploads
- View existing keys
- Delete keys you no longer need

### Settings Tab
- Enable or disable two-factor authentication
- View your account information
- Manage security settings

### Admin Tabs (Role-Dependent)
- **Contest Admin**: Generate reports from all user logs
- **Log Admin**: View and manage logs for all users
- **System Admin**: Manage user accounts (sysop only)

---

## Uploading Logs

### Method 1: Web Upload (Recommended for Beginners)

1. **Navigate to Upload Tab**
   - Click on the "Upload" tab in the dashboard

2. **Choose Your ADIF File**
   - Click "Choose File"
   - Select your .adi or .adif file
   - Maximum file size: 16MB

3. **Enter API Key**
   - When prompted, enter one of your API keys
   - If you don't have one, create it in the API Keys tab first

4. **Upload**
   - Click "Upload ADIF File"
   - Wait for the upload to complete

5. **Review Results**
   - **Total**: Total QSOs in the file
   - **New**: New contacts added to your log
   - **Duplicates**: Contacts already in your log (skipped)
   - **Errors**: Records that couldn't be processed

### Method 2: Programmatic Upload

See the [Integrating with Logging Software](#integrating-with-logging-software) section for scripts and automation.

### Supported ADIF Versions

LogShackBaby supports **ADIF 3.1.6** and is backward compatible with earlier ADIF 3.x versions.

### Automatic Deduplication

LogShackBaby automatically detects duplicate QSOs based on:
- Callsign
- Date
- Time
- Band
- Mode

Duplicates are not added, preventing duplicate entries in your log.

---

## Viewing and Searching Logs

### Viewing Your Logs

1. **Navigate to My Logs Tab**
   - All your QSO records are displayed in a table

2. **Table Columns**
   - **Date**: QSO date
   - **Time**: Start time (UTC)
   - **Call**: Contacted station
   - **Band**: Operating band (e.g., 20m, 40m)
   - **Mode**: Operating mode (e.g., SSB, CW, FT8)
   - **Frequency**: Operating frequency (MHz)
   - **RST S**: Signal report sent
   - **RST R**: Signal report received
   - **Additional**: Number of extra ADIF fields (hover to view)

3. **Pagination**
   - Use the page numbers at the bottom to navigate through logs
   - Default: 50 QSOs per page

### Searching and Filtering

Use the filter controls at the top of the logs table:

1. **Callsign Filter**
   - Enter full or partial callsign
   - Example: "W1" will find W1ABC, W1XYZ, etc.

2. **Band Filter**
   - Select a specific band from the dropdown
   - Shows only QSOs on that band

3. **Mode Filter**
   - Select a specific mode from the dropdown
   - Shows only QSOs using that mode

4. **Date Range** (if available)
   - Filter by date range

5. **Apply Filters**
   - Click "Apply" to search
   - Click "Clear" to reset filters

### Statistics

At the top of your logs, you'll see quick statistics:
- **Total QSOs**: Total number of contacts in your log
- **Unique Callsigns**: Number of different stations worked
- **Bands**: Breakdown of QSOs by band
- **Modes**: Breakdown of QSOs by mode

---

## Understanding ADIF Fields

### Core Fields

These are the essential fields for every QSO:
- **QSO_DATE**: Date of contact (required)
- **TIME_ON**: Start time of contact (required)
- **CALL**: Contacted station's callsign (required)
- **BAND**: Operating band
- **MODE**: Operating mode
- **FREQ**: Frequency in MHz
- **RST_SENT** / **RST_RCVD**: Signal reports
- **STATION_CALLSIGN**: Your callsign
- **MY_GRIDSQUARE**: Your grid square
- **GRIDSQUARE**: Their grid square
- **NAME**: Operator name
- **QTH**: Location
- **COMMENT**: Notes about the QSO

### Additional Fields

LogShackBaby captures **all ADIF 3.1.6 fields** (100+ fields), including:

- **Contest Information**: CONTEST_ID, SRX, STX, CLASS, PRECEDENCE
- **Station Details**: OPERATOR, OWNER_CALLSIGN, MY_CITY, MY_COUNTRY
- **QSL Tracking**: QSL_SENT, QSL_RCVD, LOTW_QSL_SENT, EQSL_QSL_RCVD
- **Power & Propagation**: TX_PWR, PROP_MODE, SAT_NAME, ANT_AZ
- **Awards**: DXCC, IOTA, SOTA, POTA, WWFF references
- **Location**: LAT, LON, CNTY, STATE, COUNTRY
- And many more...

### Viewing Additional Fields

In the web interface:
1. Look for the "Additional" column in your logs table
2. You'll see a badge showing the count (e.g., "5 fields")
3. Hover your mouse over the badge
4. A tooltip will display all additional field names and values

This makes it easy to see which QSOs have extra metadata like contest information, power levels, or operator notes.

---

## Exporting Logs

### Export All Logs

1. **Navigate to My Logs Tab**
2. **Click Export Button** (usually near filters)
3. **Download**: Your browser will download a .adi file with all your logs

### Export Filtered Logs

1. **Apply Filters** first (callsign, band, mode)
2. **Click Export Button**
3. Only the filtered logs will be exported

### Using Exported Logs

The exported ADIF file can be:
- Imported into other logging software
- Used for contest log submissions
- Shared with other operators
- Used as a backup

---

## Managing API Keys

API keys allow programmatic access to upload logs (useful for automation and logging software integration).

### Creating an API Key

1. **Navigate to API Keys Tab**
2. **Click "Create New API Key"**
3. **Enter Description**
   - Give it a meaningful name (e.g., "N1MM Logger", "Python Upload Script")
4. **Copy the Key Immediately**
   - The full key is shown only once
   - Copy it to a safe place
   - You cannot retrieve it later
5. **Key Prefix Saved**
   - After creation, you'll only see the key prefix (first few characters)
   - This helps you identify the key later

### Using an API Key

Include the API key in your upload requests:
- **Header**: `X-API-Key: your_api_key_here`
- See [Integrating with Logging Software](#integrating-with-logging-software) for examples

### Deleting an API Key

1. Find the key in your API Keys list
2. Click the "Delete" button next to it
3. Confirm deletion
4. The key is immediately revoked

### Best Practices

- Create separate keys for different purposes
- Use descriptive names
- Delete keys you no longer use
- Keep keys secure (don't share them publicly)
- Rotate keys periodically for security

---

## Enabling Two-Factor Authentication

Two-factor authentication (2FA) adds an extra layer of security to your account.

### Setting Up 2FA

1. **Navigate to Settings Tab**
2. **Click "Enable 2FA"**
3. **Scan QR Code**
   - Use an authenticator app on your phone:
     - Google Authenticator (iOS/Android)
     - Microsoft Authenticator (iOS/Android)
     - Authy (iOS/Android)
     - Any TOTP-compatible app
4. **Or Enter Secret Manually**
   - If you can't scan, copy the text secret and enter it manually
5. **Enter Verification Code**
   - Enter the 6-digit code shown in your app
   - Click "Verify & Enable"
6. **2FA Enabled**
   - You'll need your authenticator code every time you log in

### Logging In with 2FA

1. Enter your callsign and password
2. Click "Login"
3. Enter the 6-digit code from your authenticator app
4. Click "Verify"
5. Access granted

### Disabling 2FA

1. Navigate to Settings Tab
2. Click "Disable 2FA"
3. Enter your current authenticator code to confirm
4. 2FA is disabled

### Troubleshooting 2FA

- **Code doesn't work**: Ensure your phone's time is synchronized
- **Lost phone**: Contact your system administrator (sysop) for help
- **Time sync issues**: TOTP codes are time-based with a 30-second window

---

## User Roles

LogShackBaby has four user roles with different permissions:

### User (Default)
**What you can do:**
- Upload and manage your own logs
- Create and manage API keys
- Enable/disable 2FA on your account
- Export your logs
- View your statistics
- Search and filter your logs

**What you cannot do:**
- View other users' logs
- Modify other users' accounts
- Access administrative functions

### Contest Admin
**Additional capabilities:**
- Read-only access to all users' logs
- Generate custom reports from all logs
- Select which ADIF fields to include in reports
- Filter reports by date, band, mode
- Export reports to CSV
- View which ADIF fields contain data

**Use case:** Contest organizers who need to compile and analyze logs from all club members.

### Log Admin
**Additional capabilities:**
- View all users' logs (full access)
- Reset (delete all logs) for any user
- View log counts for all users

**Use case:** Log administrators who help manage member logs and troubleshoot issues.

### Sysop (System Operator)
**Full administrative access:**
- All user, contestadmin, and logadmin permissions
- Create new user accounts with any role
- Modify user details (email, role, active status)
- Delete user accounts and all their data
- Assign roles to users
- Promote/demote users between roles

**Use case:** System administrators who manage the entire LogShackBaby installation.

**Note:** The first user to register automatically becomes a sysop.

---

## Contest Administration

*This section is for users with the **contestadmin** role.*

### Accessing Contest Admin Features

1. Log in with a contestadmin account
2. Click on the "Contest Admin" tab
3. You'll see two subtabs:
   - **User Logs**: View individual user logs
   - **Report Generator**: Create custom reports

### Viewing User Logs

1. **Navigate to User Logs subtab**
2. **See all users** with their log counts
3. **Click on a user** to view their logs
4. **Read-only access**: You cannot modify or delete logs

### Using the Report Generator

#### Step 1: Select Fields

- **All 100+ ADIF 3.1.6 fields** are displayed as checkboxes
- **Green ● indicator**: Field contains data in the logs
- **No indicator**: Field is available but currently empty
- Select the fields you want in your report

**Common field selections:**
- Basic QSO: `user_callsign`, `qso_date`, `time_on`, `call`, `band`, `mode`
- Contest: Add `contest_id`, `srx`, `stx`, `precedence`, `class`
- Grid tracking: Add `gridsquare`, `my_gridsquare`
- Power/Equipment: Add `tx_pwr`, `operator`

#### Step 2: Apply Filters (Optional)

- **Date Range**: From/To dates (YYYY-MM-DD)
- **Bands**: Comma-separated list (e.g., `20m, 40m, 80m`)
- **Modes**: Comma-separated list (e.g., `FT8, SSB, CW`)
- **User**: Filter by specific user (leave blank for all users)

#### Step 3: Generate Report

1. Click "Generate Report"
2. Wait for processing (up to 10,000 records)
3. View results in an interactive table
4. OR click "Export to CSV" for analysis in Excel/LibreOffice

#### Example Use Cases

**Contest Log Compilation:**
- Select: `user_callsign`, `qso_date`, `time_on`, `call`, `band`, `mode`, `contest_id`, `srx`, `stx`
- Filter: Date range of contest weekend
- Export to CSV for submission

**Grid Tracking:**
- Select: `call`, `gridsquare`, `band`, `mode`
- Filter: Specific band (e.g., 6m)
- See which grids have been worked

**Power Analysis:**
- Select: `user_callsign`, `tx_pwr`, `band`, `mode`
- See power levels used by operators

---

## Integrating with Logging Software

### General Process

1. Export your log from your logging software in ADIF format
2. Upload it to LogShackBaby via web or API
3. Repeat periodically to keep logs synchronized

### Supported Logging Software

LogShackBaby works with any software that exports ADIF format:
- N1MM Logger+
- Logger32
- Ham Radio Deluxe
- WSJT-X / JTDX
- DXLab Suite
- Log4OM
- And any other ADIF-compatible software

### Using cURL for Upload

```bash
#!/bin/bash
# Save as upload.sh

API_KEY="your_api_key_here"
LOG_FILE="path/to/your/log.adi"

curl -X POST http://localhost:5000/api/logs/upload \
  -H "X-API-Key: $API_KEY" \
  -F "file=@$LOG_FILE"
```

Make executable: `chmod +x upload.sh`

### Using Python for Upload

```python
import requests

def upload_log(api_key, file_path):
    url = "http://localhost:5000/api/logs/upload"
    headers = {"X-API-Key": api_key}
    
    with open(file_path, 'rb') as f:
        response = requests.post(url, headers=headers, files={'file': f})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Uploaded: {data['new']} new, {data['duplicates']} duplicates")
    else:
        print(f"❌ Error: {response.json().get('error')}")

# Usage
upload_log("your_api_key", "my_log.adi")
```

### Automated Daily Upload

Add to your crontab (`crontab -e`):
```bash
# Upload logs daily at 2 AM
0 2 * * * /path/to/upload.sh >> /var/log/logshack_upload.log 2>&1
```

### N1MM Logger+ Integration

1. **Export from N1MM:**
   - File → ADIF/Cabrillo → Export ADIF
   - Save to a known location

2. **Upload:**
   - Use the web interface, or
   - Use a script to automatically upload

### WSJT-X Integration

1. **Find your log file:**
   - Usually in: `C:\Users\YourName\AppData\Local\WSJT-X\` (Windows)
   - Or: `~/.local/share/WSJT-X/` (Linux)
   - File: `wsjtx_log.adi`

2. **Upload periodically:**
   - Use a scheduled script to upload the file regularly

---

## Troubleshooting

### Cannot Login

**Check:**
- Is your callsign spelled correctly? (case-insensitive)
- Is your password correct?
- If you have 2FA enabled, is the code current?
- Is the server running?

**Solutions:**
- Reset password (contact administrator if no reset feature)
- Disable 2FA (contact administrator)
- Verify server is accessible

### Upload Fails

**Common causes:**
- Invalid ADIF format
- File too large (max 16MB)
- Wrong API key
- Network issues

**Solutions:**
- Verify your file is valid ADIF format
- Check file size
- Verify you're using the correct API key
- Try a smaller file first
- Check server logs (ask administrator)

### Logs Not Appearing

**Check:**
- Did the upload succeed?
- Are you looking at the right user account?
- Try refreshing the page

**Solutions:**
- Re-upload the file
- Check upload history tab
- Verify no errors occurred during upload

### 2FA Code Not Working

**Common causes:**
- Time synchronization issue
- Wrong app
- Code expired (they change every 30 seconds)

**Solutions:**
- Ensure phone time is synchronized
- Try the code before or after the current one
- Verify you're using the right authenticator entry
- Contact administrator to disable 2FA if locked out

### Cannot Export Logs

**Check:**
- Do you have logs to export?
- Is your browser blocking downloads?
- Is the server responding?

**Solutions:**
- Check that you have QSOs in your log
- Allow downloads in browser settings
- Try a different browser
- Contact administrator

### Getting Help

1. Check this user guide
2. Contact your club's LogShackBaby administrator
3. Ask your sysop for assistance
4. Check server status with your administrator

---

## Tips and Best Practices

### Regular Backups
- Export your logs regularly as a backup
- Keep ADIF files from your logging software

### API Key Security
- Don't share your API keys
- Use different keys for different purposes
- Delete unused keys

### Enable 2FA
- Adds significant security to your account
- Protects against password compromise
- Quick and easy to set up

### Upload Regularly
- Upload logs after each operating session
- Use automated scripts for convenience
- Keeps your online log up to date

### Use Filters Effectively
- Filter before exporting to get specific data
- Save time finding specific QSOs
- Use partial callsign matching

### Check Upload Results
- Review the upload summary
- Investigate any errors
- Verify new contacts were added

---

**73 and Happy Logging!** 📻✨

*For setup and administration, see ADMINISTRATION.md*  
*For development and API details, see DEVELOPMENT.md*
