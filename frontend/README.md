# LogShackBaby Frontend

The frontend directory contains the web-based user interface for the LogShackBaby amateur radio log server application. This is a pure client-side application built with vanilla HTML, CSS, and JavaScript.

## Directory Structure

```
frontend/
├── index.html           # Main application page with login, logs, and settings
├── contest.html         # Contest management interface (admin only)
├── leaderboard.html     # Contest leaderboards and scoring display
├── css/
│   └── style.css        # Main stylesheet with CSS variables and responsive design
└── js/
    ├── app.js           # Main application logic and API interactions
    ├── contest.js       # Contest creation, editing, and management
    └── leaderboard.js   # Leaderboard display and contest scoring
```

## Pages

### index.html
The main application interface that provides:
- **Authentication**: User login, registration, and two-factor authentication (MFA)
- **Log Management**: View, filter, search, and export QSO logs
- **File Upload**: Import ADIF format log files
- **API Keys**: Generate and manage API keys for programmatic access
- **Settings**: Profile management, MFA setup/disable
- **Admin Panel**: User management and log administration (for privileged users)

Key features:
- Tab-based navigation for different sections
- Role-based access control (user, logadmin, sysop)
- Session token-based authentication stored in localStorage
- Real-time log filtering and pagination
- ADIF file upload with drag-and-drop support

### contest.html
Contest management interface for administrators to:
- Create new amateur radio contests
- Edit existing contest details (name, dates, description, rules)
- Activate/deactivate contests
- Populate contest entries from user logs
- Delete contests

Access restricted to users with `contestadmin`, `logadmin`, or `sysop` roles.

### leaderboard.html
Public-facing contest leaderboards displaying:
- Contest selection dropdown
- Real-time scoring and rankings
- Medal indicators for top 3 positions (🥇🥈🥉)
- Participant statistics (total QSOs, unique callsigns, multipliers)
- Detailed QSO breakdown per participant
- Sortable columns

Accessible to all authenticated users.

## JavaScript Modules

### app.js (1408 lines)
Core application module handling:
- **Authentication Flow**: Login, registration, MFA verification, logout
- **Session Management**: Token storage and validation
- **Dashboard**: Main interface after login
- **Log Operations**: Fetch, filter, display, and export logs
- **File Upload**: ADIF file parsing and submission
- **API Key Management**: Creation and display of API keys
- **MFA Setup**: QR code generation and TOTP verification
- **Admin Functions**: User creation, role management, log reports
- **Tab Navigation**: Multi-tab interface management

API endpoints:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/mfa/verify` - MFA code verification
- `GET /api/logs` - Retrieve logs with filtering
- `POST /api/upload` - Upload ADIF files
- `POST /api/keys` - Generate API keys
- `GET /api/admin/users` - List all users (admin)
- `POST /api/admin/users` - Create user (admin)

### contest.js (288 lines)
Contest administration module providing:
- Contest CRUD operations (Create, Read, Update, Delete)
- Form validation for contest details
- Date/time formatting and validation
- Contest population from user logs
- Modal dialogs for editing
- Role-based UI rendering

Communicates with separate contest service API on port 5001.

### leaderboard.js (254 lines)
Leaderboard display module featuring:
- Contest selection and loading
- Real-time score calculation
- Participant ranking with visual medals
- QSO detail modal for each participant
- HTML escaping for security
- Empty state handling

Fetches data from contest service API and displays formatted results.

## Stylesheets

### style.css (780 lines)
Comprehensive stylesheet featuring:
- **CSS Variables**: Color scheme, spacing, shadows defined at `:root`
- **Responsive Design**: Mobile-first approach with flexbox/grid
- **Component Styles**: 
  - Navigation bar with user info
  - Authentication forms and cards
  - Tab navigation system
  - Data tables with pagination
  - Modal dialogs
  - Buttons (primary, secondary, success, danger)
  - Forms and input elements
  - Alert messages
  - Cards and containers
- **Theme**: Modern, clean design with blue primary color
- **Animations**: Smooth transitions and hover effects

Color scheme:
- Primary: `#2563eb` (blue)
- Success: `#10b981` (green)
- Danger: `#ef4444` (red)
- Background: `#f1f5f9` (light gray)

## API Integration

The frontend communicates with two backend services:

1. **Main API** (`http://localhost:5000/api` in production via nginx)
   - User authentication and management
   - Log storage and retrieval
   - File uploads
   - API key management

2. **Contest Service** (`http://localhost:5001/api`)
   - Contest management
   - Leaderboard generation
   - Scoring calculations

Authentication uses session tokens passed via `X-Session-Token` header.

## Security Features

- Session token storage in `localStorage`
- Two-factor authentication (TOTP) support
- Role-based access control
- HTML escaping to prevent XSS attacks
- Password confirmation on registration
- Session validation on page load
- HTTPS support (via nginx in production)

## User Roles

1. **user**: Standard user with log viewing and uploading
2. **logadmin**: Can view all user logs and generate reports
3. **contestadmin**: Can manage contests and leaderboards
4. **sysop**: Full system access including user management

## Development

The frontend is a static web application that can be served by any web server. In the LogShackBaby architecture, it's served through nginx which also proxies API requests to the backend services.

**No build process required** - all files are plain HTML, CSS, and JavaScript.

To develop locally:
1. Serve the frontend directory with any static file server
2. Ensure backend API is running on expected ports
3. Update API base URLs in JavaScript files if needed

## Dependencies

**None** - This is a pure vanilla JavaScript application with no external libraries or frameworks. All functionality is implemented using native browser APIs.
