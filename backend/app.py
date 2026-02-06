"""
LogShackBaby - Amateur Radio Log Server
Main Flask application
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime

from models import db, User, APIKey, LogEntry, UploadLog, Session, ReportTemplate
from auth import AuthManager
from adif_parser import ADIFParser

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://logshackbaby:logshackbaby@db:5432/logshackbaby'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)


def require_auth(f):
    """Decorator to require session authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('X-Session-Token')
        
        if not session_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Look up session in database
        session = Session.query.filter_by(session_token=session_token).first()
        if not session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if MFA is required but not completed
        if session.mfa_required and not session.mfa_verified:
            return jsonify({'error': 'MFA verification required'}), 403
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        db.session.commit()
        
        request.current_user = User.query.get(session.user_id)
        if not request.current_user:
            return jsonify({'error': 'User not found'}), 401
        
        # Check if password change is required (allow only change-password endpoint)
        if request.current_user.must_change_password and request.endpoint != 'change_password':
            return jsonify({'error': 'Password change required', 'must_change_password': True}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        user = AuthManager.verify_api_key(api_key)
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def require_role(role):
    """Decorator to require a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not request.current_user.has_role(role):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes - Serve Frontend
@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)


# Routes - Authentication
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    callsign = data.get('callsign', '').strip().upper()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not callsign or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user, error = AuthManager.create_user(callsign, email, password)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Registration successful',
        'callsign': user.callsign
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    callsign = data.get('callsign', '').strip().upper()
    password = data.get('password', '')
    
    user = AuthManager.authenticate_user(callsign, password)
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create session in database
    import secrets
    session_token = secrets.token_urlsafe(32)
    
    new_session = Session(
        session_token=session_token,
        user_id=user.id,
        mfa_required=user.mfa_enabled,
        mfa_verified=not user.mfa_enabled
    )
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({
        'session_token': session_token,
        'callsign': user.callsign,
        'role': user.role,
        'mfa_required': user.mfa_enabled,
        'must_change_password': user.must_change_password
    }), 200


@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    session_token = request.headers.get('X-Session-Token')
    if session_token:
        session = Session.query.filter_by(session_token=session_token).first()
        if session:
            db.session.delete(session)
            db.session.commit()
    
    return jsonify({'message': 'Logged out successfully'}), 200


# Routes - MFA
@app.route('/api/mfa/setup', methods=['POST'])
@require_auth
def mfa_setup():
    """Setup MFA for user"""
    user = request.current_user
    
    if user.mfa_enabled:
        return jsonify({'error': 'MFA already enabled'}), 400
    
    # Generate secret
    secret = AuthManager.generate_mfa_secret()
    
    # Store secret (not enabled yet)
    user.mfa_secret = secret
    db.session.commit()
    
    # Generate QR code
    qr_code = AuthManager.generate_qr_code(user.callsign, secret)
    
    return jsonify({
        'secret': secret,
        'qr_code': qr_code
    }), 200


@app.route('/api/mfa/enable', methods=['POST'])
@require_auth
def mfa_enable():
    """Enable MFA after verifying token"""
    data = request.get_json()
    token = data.get('token', '')
    
    user = request.current_user
    
    if not user.mfa_secret:
        return jsonify({'error': 'MFA not set up'}), 400
    
    if not AuthManager.verify_mfa_token(user.mfa_secret, token):
        return jsonify({'error': 'Invalid token'}), 400
    
    user.mfa_enabled = True
    db.session.commit()
    
    return jsonify({'message': 'MFA enabled successfully'}), 200


@app.route('/api/mfa/verify', methods=['POST'])
def mfa_verify():
    """Verify MFA token during login"""
    data = request.get_json()
    session_token = data.get('session_token', '')
    token = data.get('token', '')
    
    # Look up session in database
    session = Session.query.filter_by(session_token=session_token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 401
    
    user = User.query.get(session.user_id)
    
    if not user or not user.mfa_enabled:
        return jsonify({'error': 'MFA not enabled'}), 400
    
    if not AuthManager.verify_mfa_token(user.mfa_secret, token):
        return jsonify({'error': 'Invalid token'}), 400
    
    # Mark MFA as verified in session
    session.mfa_verified = True
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'MFA verified successfully',
        'must_change_password': user.must_change_password
    }), 200


@app.route('/api/mfa/disable', methods=['POST'])
@require_auth
def mfa_disable():
    """Disable MFA"""
    data = request.get_json()
    password = data.get('password', '')
    
    user = request.current_user
    
    if not AuthManager.verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid password'}), 401
    
    user.mfa_enabled = False
    user.mfa_secret = None
    db.session.commit()
    
    return jsonify({'message': 'MFA disabled successfully'}), 200


@app.route('/api/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password (also handles forced password changes)"""
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    user = request.current_user
    
    if not current_password or not new_password:
        return jsonify({'error': 'Both current and new passwords are required'}), 400
    
    # Verify current password
    if not AuthManager.verify_password(current_password, user.password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password (minimum length)
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    # Update password
    user.password_hash = AuthManager.hash_password(new_password)
    user.must_change_password = False
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


# Routes - API Keys
@app.route('/api/keys', methods=['GET'])
@require_auth
def list_api_keys():
    """List user's API keys"""
    user = request.current_user
    
    keys = APIKey.query.filter_by(user_id=user.id).all()
    
    return jsonify({
        'keys': [{
            'id': key.id,
            'prefix': key.key_prefix,
            'description': key.description,
            'created_at': key.created_at.isoformat(),
            'last_used': key.last_used.isoformat() if key.last_used else None,
            'is_active': key.is_active
        } for key in keys]
    }), 200


@app.route('/api/keys', methods=['POST'])
@require_auth
def create_api_key():
    """Create a new API key"""
    data = request.get_json()
    description = data.get('description', '').strip()
    
    user = request.current_user
    
    # Generate key
    full_key, key_hash, key_prefix = AuthManager.generate_api_key()
    
    # Store in database
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        description=description
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    return jsonify({
        'api_key': full_key,
        'prefix': key_prefix,
        'message': 'Store this key safely - it will not be shown again'
    }), 201


@app.route('/api/keys/<int:key_id>', methods=['DELETE'])
@require_auth
def delete_api_key(key_id):
    """Delete an API key"""
    user = request.current_user
    
    api_key = APIKey.query.filter_by(id=key_id, user_id=user.id).first()
    
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    db.session.delete(api_key)
    db.session.commit()
    
    return jsonify({'message': 'API key deleted'}), 200


# Routes - Log Upload and Management
@app.route('/api/logs/upload', methods=['POST'])
@require_api_key
def upload_log():
    """Upload ADIF log file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user = request.current_user
    
    # Create upload log entry
    upload_log = UploadLog(
        user_id=user.id,
        filename=file.filename,
        status='processing'
    )
    db.session.add(upload_log)
    db.session.commit()
    
    try:
        # Parse ADIF file
        parser = ADIFParser()
        file_content = file.read()
        records = parser.parse_file(file_content)
        
        upload_log.total_records = len(records)
        
        # Process records
        new_count = 0
        duplicate_count = 0
        error_count = 0
        
        for record in records:
            try:
                # Check for duplicate
                existing = LogEntry.query.filter_by(
                    user_id=user.id,
                    qso_hash=record['qso_hash']
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Create new log entry
                log_entry = LogEntry(
                    user_id=user.id,
                    qso_date=record.get('qso_date'),
                    time_on=record.get('time_on'),
                    call=record.get('call'),
                    band=record.get('band'),
                    mode=record.get('mode'),
                    freq=record.get('freq'),
                    rst_sent=record.get('rst_sent'),
                    rst_rcvd=record.get('rst_rcvd'),
                    qso_date_off=record.get('qso_date_off'),
                    time_off=record.get('time_off'),
                    station_callsign=record.get('station_callsign'),
                    my_gridsquare=record.get('my_gridsquare'),
                    gridsquare=record.get('gridsquare'),
                    name=record.get('name'),
                    qth=record.get('qth'),
                    comment=record.get('comment'),
                    additional_fields=record.get('additional_fields'),
                    qso_hash=record['qso_hash']
                )
                
                db.session.add(log_entry)
                new_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error processing record: {e}")
        
        # Commit all new entries
        db.session.commit()
        
        # Update upload log
        upload_log.new_records = new_count
        upload_log.duplicate_records = duplicate_count
        upload_log.error_records = error_count
        upload_log.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'message': 'Upload successful',
            'total': len(records),
            'new': new_count,
            'duplicates': duplicate_count,
            'errors': error_count
        }), 200
        
    except Exception as e:
        upload_log.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    """Get user's log entries"""
    user = request.current_user
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Filters
    callsign = request.args.get('callsign', '').upper()
    band = request.args.get('band', '')
    mode = request.args.get('mode', '')
    
    # Build query
    query = LogEntry.query.filter_by(user_id=user.id)
    
    if callsign:
        query = query.filter(LogEntry.call.ilike(f'%{callsign}%'))
    if band:
        query = query.filter_by(band=band)
    if mode:
        query = query.filter_by(mode=mode)
    
    # Order by date/time descending
    query = query.order_by(LogEntry.qso_date.desc(), LogEntry.time_on.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'qso_date': log.qso_date,
            'time_on': log.time_on,
            'call': log.call,
            'band': log.band,
            'mode': log.mode,
            'freq': log.freq,
            'rst_sent': log.rst_sent,
            'rst_rcvd': log.rst_rcvd,
            'station_callsign': log.station_callsign,
            'gridsquare': log.gridsquare,
            'name': log.name,
            'comment': log.comment
        } for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route('/api/logs/stats', methods=['GET'])
@require_auth
def get_log_stats():
    """Get statistics about user's logs"""
    user = request.current_user
    
    total_qsos = LogEntry.query.filter_by(user_id=user.id).count()
    
    # Get unique callsigns worked
    unique_calls = db.session.query(LogEntry.call).filter_by(
        user_id=user.id
    ).distinct().count()
    
    # Get band breakdown
    band_stats = db.session.query(
        LogEntry.band,
        db.func.count(LogEntry.id)
    ).filter_by(user_id=user.id).group_by(LogEntry.band).all()
    
    # Get mode breakdown
    mode_stats = db.session.query(
        LogEntry.mode,
        db.func.count(LogEntry.id)
    ).filter_by(user_id=user.id).group_by(LogEntry.mode).all()
    
    return jsonify({
        'total_qsos': total_qsos,
        'unique_callsigns': unique_calls,
        'bands': {band: count for band, count in band_stats if band},
        'modes': {mode: count for mode, count in mode_stats if mode}
    }), 200


@app.route('/api/uploads', methods=['GET'])
@require_auth
def get_uploads():
    """Get upload history"""
    user = request.current_user
    
    uploads = UploadLog.query.filter_by(user_id=user.id).order_by(
        UploadLog.uploaded_at.desc()
    ).limit(50).all()
    
    return jsonify({
        'uploads': [{
            'id': upload.id,
            'filename': upload.filename,
            'uploaded_at': upload.uploaded_at.isoformat(),
            'total_records': upload.total_records,
            'new_records': upload.new_records,
            'duplicate_records': upload.duplicate_records,
            'error_records': upload.error_records,
            'status': upload.status
        } for upload in uploads]
    }), 200


@app.route('/api/logs/export', methods=['GET'])
@require_auth
def export_logs():
    """Export logs in ADIF format"""
    user = request.current_user
    
    # Get filters
    callsign = request.args.get('callsign', '').upper()
    band = request.args.get('band', '')
    mode = request.args.get('mode', '')
    
    # Build query
    query = LogEntry.query.filter_by(user_id=user.id)
    
    if callsign:
        query = query.filter(LogEntry.call.ilike(f'%{callsign}%'))
    if band:
        query = query.filter_by(band=band)
    if mode:
        query = query.filter_by(mode=mode)
    
    # Order by date/time
    logs = query.order_by(LogEntry.qso_date, LogEntry.time_on).all()
    
    # Build ADIF file
    adif_content = generate_adif_export(logs, user.callsign)
    
    # Create response with proper headers
    from flask import make_response
    response = make_response(adif_content)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename="{user.callsign}_logbook.adi"'
    
    return response


def generate_adif_export(logs, callsign):
    """Generate ADIF file content from log entries"""
    from datetime import datetime
    
    # ADIF header
    header = f"""ADIF export from LogShackBaby
<ADIF_VER:5>3.1.4
<PROGRAMID:12>LogShackBaby
<PROGRAMVERSION:5>1.0.0
<CREATED_TIMESTAMP:15>{datetime.utcnow().strftime('%Y%m%d %H%M%S')}
<EOH>

"""
    
    records = []
    
    for log in logs:
        fields = []
        
        # Add core fields in standard order
        if log.station_callsign:
            fields.append(f"<STATION_CALLSIGN:{len(log.station_callsign)}>{log.station_callsign}")
        
        fields.append(f"<CALL:{len(log.call)}>{log.call}")
        fields.append(f"<QSO_DATE:{len(log.qso_date)}>{log.qso_date}")
        fields.append(f"<TIME_ON:{len(log.time_on)}>{log.time_on}")
        
        if log.qso_date_off:
            fields.append(f"<QSO_DATE_OFF:{len(log.qso_date_off)}>{log.qso_date_off}")
        if log.time_off:
            fields.append(f"<TIME_OFF:{len(log.time_off)}>{log.time_off}")
        
        if log.band:
            fields.append(f"<BAND:{len(log.band)}>{log.band}")
        if log.freq:
            fields.append(f"<FREQ:{len(log.freq)}>{log.freq}")
        if log.mode:
            fields.append(f"<MODE:{len(log.mode)}>{log.mode}")
        
        if log.rst_sent:
            fields.append(f"<RST_SENT:{len(log.rst_sent)}>{log.rst_sent}")
        if log.rst_rcvd:
            fields.append(f"<RST_RCVD:{len(log.rst_rcvd)}>{log.rst_rcvd}")
        
        if log.my_gridsquare:
            fields.append(f"<MY_GRIDSQUARE:{len(log.my_gridsquare)}>{log.my_gridsquare}")
        if log.gridsquare:
            fields.append(f"<GRIDSQUARE:{len(log.gridsquare)}>{log.gridsquare}")
        
        if log.name:
            fields.append(f"<NAME:{len(log.name)}>{log.name}")
        if log.qth:
            fields.append(f"<QTH:{len(log.qth)}>{log.qth}")
        if log.comment:
            fields.append(f"<COMMENT:{len(log.comment)}>{log.comment}")
        
        # Add additional fields from JSON
        if log.additional_fields:
            for field_name, field_value in log.additional_fields.items():
                field_value_str = str(field_value)
                fields.append(f"<{field_name.upper()}:{len(field_value_str)}>{field_value_str}")
        
        # Join fields with space and add EOR
        record = ' '.join(fields) + ' <EOR>\n'
        records.append(record)
    
    return header + ''.join(records)


# Routes - Admin (Sysop)
@app.route('/api/admin/users', methods=['GET'])
@require_auth
@require_role('sysop')
def admin_list_users():
    """List all users (sysop only)"""
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': u.id,
            'callsign': u.callsign,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'mfa_enabled': u.mfa_enabled,
            'created_at': u.created_at.isoformat(),
            'last_login': u.last_login.isoformat() if u.last_login else None,
            'log_count': len(u.log_entries)
        } for u in users]
    }), 200


@app.route('/api/admin/users', methods=['POST'])
@require_auth
@require_role('sysop')
def admin_create_user():
    """Create a new user (sysop only)"""
    data = request.get_json()
    
    callsign = data.get('callsign', '').strip().upper()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'user')
    
    if not callsign or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if role not in ['user', 'contestadmin', 'logadmin', 'sysop']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if user exists
    if User.query.filter_by(callsign=callsign).first():
        return jsonify({'error': 'Callsign already registered'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(
        callsign=callsign,
        email=email,
        password_hash=AuthManager.hash_password(password),
        role=role
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'callsign': user.callsign,
            'email': user.email,
            'role': user.role
        }
    }), 201


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@require_auth
@require_role('sysop')
def admin_update_user(user_id):
    """Update a user (sysop only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'email' in data:
        email = data['email'].strip()
        if email != user.email and User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = email
    
    if 'role' in data:
        role = data['role']
        if role not in ['user', 'contestadmin', 'logadmin', 'sysop']:
            return jsonify({'error': 'Invalid role'}), 400
        user.role = role
    
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    
    if 'password' in data and data['password']:
        user.password_hash = AuthManager.hash_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'callsign': user.callsign,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
    }), 200


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('sysop')
def admin_delete_user(user_id):
    """Delete a user and all their logs (sysop only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deleting yourself
    if user.id == request.current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    callsign = user.callsign
    log_count = len(user.log_entries)
    
    # Delete user's sessions first (to avoid foreign key constraint)
    Session.query.filter_by(user_id=user_id).delete()
    
    # Delete user (cascade will handle log entries, API keys, etc.)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': f'User {callsign} and {log_count} log entries deleted successfully'
    }), 200


@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@require_auth
@require_role('sysop')
def admin_reset_password(user_id):
    """Reset user password with temporary password (sysop only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate a temporary password
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Set the temporary password and require password change
    user.password_hash = AuthManager.hash_password(temp_password)
    user.must_change_password = True
    
    # Invalidate all existing sessions to force re-login
    Session.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Password reset successfully',
        'temporary_password': temp_password,
        'callsign': user.callsign
    }), 200


# Routes - Contest Admin
@app.route('/api/contestadmin/users', methods=['GET'])
@require_auth
@require_role('contestadmin')
def contestadmin_list_users():
    """List all users with log info (contestadmin only)"""
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': u.id,
            'callsign': u.callsign,
            'log_count': len(u.log_entries),
            'created_at': u.created_at.isoformat()
        } for u in users]
    }), 200


@app.route('/api/contestadmin/users/<int:user_id>/logs', methods=['GET'])
@require_auth
@require_role('contestadmin')
def contestadmin_get_user_logs(user_id):
    """Get logs for a specific user (contestadmin only - read only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Get logs
    pagination = LogEntry.query.filter_by(user_id=user_id).order_by(
        LogEntry.qso_date.desc(), 
        LogEntry.time_on.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    logs = [{
        'id': log.id,
        'qso_date': log.qso_date,
        'time_on': log.time_on,
        'call': log.call,
        'band': log.band,
        'mode': log.mode,
        'freq': log.freq,
        'rst_sent': log.rst_sent,
        'rst_rcvd': log.rst_rcvd,
        'station_callsign': log.station_callsign,
        'comment': log.comment
    } for log in pagination.items]
    
    return jsonify({
        'user': {
            'id': user.id,
            'callsign': user.callsign
        },
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200


@app.route('/api/contestadmin/available-fields', methods=['GET'])
@require_auth
@require_role('contestadmin')
def contestadmin_available_fields():
    """Get all ADIF 3.1.6 fields and indicate which have data"""
    from adif_parser import ADIFParser
    
    # Get all possible ADIF fields from parser (excluding core fields)
    parser = ADIFParser()
    all_possible_fields = sorted(list(parser.ALL_ADIF_FIELDS - parser.CORE_FIELDS))
    
    # Get fields that actually have data in logs
    logs = LogEntry.query.limit(1000).all()
    fields_with_data = set()
    
    for log in logs:
        if log.additional_fields:
            fields_with_data.update(log.additional_fields.keys())
    
    return jsonify({
        'all_fields': all_possible_fields,
        'fields_with_data': sorted(list(fields_with_data)),
        'additional_fields': sorted(list(fields_with_data))  # Keep for backwards compatibility
    }), 200


@app.route('/api/contestadmin/report', methods=['POST'])
@require_auth
@require_role('contestadmin')
def contestadmin_generate_report():
    """Generate a custom report from all user logs"""
    data = request.get_json()
    
    # Get selected fields
    fields = data.get('fields', [])
    if not fields:
        return jsonify({'error': 'No fields selected'}), 400
    
    # Validate fields
    valid_fields = [
        'qso_date', 'time_on', 'call', 'band', 'mode', 'freq',
        'rst_sent', 'rst_rcvd', 'station_callsign', 'my_gridsquare',
        'gridsquare', 'name', 'qth', 'comment', 'qso_date_off', 'time_off'
    ]
    
    for field in fields:
        # Allow fields from JSON (prefixed with 'json:')
        if field.startswith('json:'):
            continue
        if field not in valid_fields and field != 'user_callsign':
            return jsonify({'error': f'Invalid field: {field}'}), 400
    
    # Get filters
    filters = data.get('filters', {})
    date_from = filters.get('date_from')
    date_to = filters.get('date_to')
    bands = filters.get('bands', [])
    modes = filters.get('modes', [])
    user_ids = filters.get('user_ids', [])
    
    # Build query
    query = LogEntry.query.join(User)
    
    if date_from:
        query = query.filter(LogEntry.qso_date >= date_from.replace('-', ''))
    if date_to:
        query = query.filter(LogEntry.qso_date <= date_to.replace('-', ''))
    if bands:
        query = query.filter(LogEntry.band.in_(bands))
    if modes:
        query = query.filter(LogEntry.mode.in_(modes))
    if user_ids:
        query = query.filter(LogEntry.user_id.in_(user_ids))
    
    # Get results
    results = query.order_by(LogEntry.qso_date.desc(), LogEntry.time_on.desc()).limit(10000).all()
    
    # Build report data
    report_data = []
    for log in results:
        row = {}
        for field in fields:
            if field == 'user_callsign':
                row[field] = log.user.callsign
            elif field.startswith('json:'):
                # Extract from additional_fields JSON
                json_key = field[5:]  # Remove 'json:' prefix
                row[field] = log.additional_fields.get(json_key) if log.additional_fields else None
            else:
                row[field] = getattr(log, field, None)
        report_data.append(row)
    
    return jsonify({
        'report': report_data,
        'total': len(report_data),
        'fields': fields
    }), 200


@app.route('/api/contestadmin/templates', methods=['POST'])
@require_auth
@require_role('contestadmin')
def contestadmin_create_template():
    """Create a new report template"""
    data = request.get_json()
    
    name = data.get('name')
    if not name or not name.strip():
        return jsonify({'error': 'Template name is required'}), 400
    
    fields = data.get('fields', [])
    if not fields:
        return jsonify({'error': 'At least one field is required'}), 400
    
    description = data.get('description', '')
    filters = data.get('filters', {})
    shared_with_role = data.get('shared_with_role')  # Optional: 'contestadmin', 'logadmin', etc.
    
    # Validate shared_with_role if provided
    if shared_with_role and shared_with_role not in ['contestadmin', 'logadmin', 'sysop']:
        return jsonify({'error': 'Invalid role for sharing'}), 400
    
    # Create template
    template = ReportTemplate(
        user_id=request.current_user.id,
        name=name.strip(),
        description=description.strip() if description else None,
        fields=fields,
        filters=filters,
        shared_with_role=shared_with_role
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'message': 'Template created successfully',
        'template': {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'fields': template.fields,
            'filters': template.filters,
            'shared_with_role': template.shared_with_role,
            'created_at': template.created_at.isoformat()
        }
    }), 201


@app.route('/api/contestadmin/templates', methods=['GET'])
@require_auth
@require_role('contestadmin')
def contestadmin_list_templates():
    """List all report templates (user's own + global templates + role-shared templates)"""
    # Get user's own templates
    user_templates = ReportTemplate.query.filter_by(user_id=request.current_user.id).order_by(
        ReportTemplate.created_at.desc()
    ).all()
    
    # Get global templates
    global_templates = ReportTemplate.query.filter_by(is_global=True).order_by(
        ReportTemplate.name
    ).all()
    
    # Get templates shared with user's role
    role_shared_templates = ReportTemplate.query.filter(
        ReportTemplate.shared_with_role == request.current_user.role,
        ReportTemplate.user_id != request.current_user.id  # Exclude own templates (already in user_templates)
    ).order_by(
        ReportTemplate.created_at.desc()
    ).all()
    
    # Combine them (global first, then role-shared, then user's)
    all_templates = global_templates + role_shared_templates + user_templates
    
    return jsonify({
        'templates': [{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'fields': t.fields,
            'filters': t.filters,
            'is_global': t.is_global,
            'shared_with_role': t.shared_with_role,
            'is_owner': t.user_id == request.current_user.id,
            'created_at': t.created_at.isoformat(),
            'updated_at': t.updated_at.isoformat()
        } for t in all_templates]
    }), 200


@app.route('/api/contestadmin/templates/<int:template_id>', methods=['GET'])
@require_auth
@require_role('contestadmin')
def contestadmin_get_template(template_id):
    """Get a specific report template"""
    # Allow access to user's own templates, global templates, or role-shared templates
    template = ReportTemplate.query.filter(
        ReportTemplate.id == template_id,
        db.or_(
            ReportTemplate.user_id == request.current_user.id,
            ReportTemplate.is_global == True,
            ReportTemplate.shared_with_role == request.current_user.role
        )
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({
        'template': {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'fields': template.fields,
            'filters': template.filters,
            'is_global': template.is_global,
            'shared_with_role': template.shared_with_role,
            'is_owner': template.user_id == request.current_user.id,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat()
        }
    }), 200


@app.route('/api/contestadmin/templates/<int:template_id>', methods=['DELETE'])
@require_auth
@require_role('contestadmin')
def contestadmin_delete_template(template_id):
    """Delete a report template"""
    template = ReportTemplate.query.filter_by(
        id=template_id,
        user_id=request.current_user.id
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found or you do not have permission to delete it'}), 404
    
    # Prevent deletion of global templates
    if template.is_global:
        return jsonify({'error': 'Cannot delete global templates'}), 403
    
    # Prevent deletion of role-shared templates (only owner can delete)
    # This is already handled by the query filter above (user_id=request.current_user.id)
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'message': 'Template deleted successfully'}), 200


@app.route('/api/contestadmin/templates/<int:template_id>/run', methods=['POST'])
@require_auth
@require_role('contestadmin')
def contestadmin_run_template(template_id):
    """Run a report template (generate report from template)"""
    # Allow running user's own templates, global templates, or role-shared templates
    template = ReportTemplate.query.filter(
        ReportTemplate.id == template_id,
        db.or_(
            ReportTemplate.user_id == request.current_user.id,
            ReportTemplate.is_global == True,
            ReportTemplate.shared_with_role == request.current_user.role
        )
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Use the template's fields and filters to generate report
    fields = template.fields
    filters = template.filters or {}
    
    # Validate fields (same validation as in contestadmin_generate_report)
    valid_fields = [
        'qso_date', 'time_on', 'call', 'band', 'mode', 'freq',
        'rst_sent', 'rst_rcvd', 'station_callsign', 'my_gridsquare',
        'gridsquare', 'name', 'qth', 'comment', 'qso_date_off', 'time_off'
    ]
    
    for field in fields:
        if field.startswith('json:'):
            continue
        if field not in valid_fields and field != 'user_callsign':
            return jsonify({'error': f'Invalid field: {field}'}), 400
    
    # Build query
    date_from = filters.get('date_from')
    date_to = filters.get('date_to')
    bands = filters.get('bands', [])
    modes = filters.get('modes', [])
    user_ids = filters.get('user_ids', [])
    
    query = LogEntry.query.join(User)
    
    if date_from:
        query = query.filter(LogEntry.qso_date >= date_from.replace('-', ''))
    if date_to:
        query = query.filter(LogEntry.qso_date <= date_to.replace('-', ''))
    if bands:
        query = query.filter(LogEntry.band.in_(bands))
    if modes:
        query = query.filter(LogEntry.mode.in_(modes))
    if user_ids:
        query = query.filter(LogEntry.user_id.in_(user_ids))
    
    # Get results
    results = query.order_by(LogEntry.qso_date.desc(), LogEntry.time_on.desc()).limit(10000).all()
    
    # Build report data
    report_data = []
    for log in results:
        row = {}
        for field in fields:
            if field == 'user_callsign':
                row[field] = log.user.callsign
            elif field.startswith('json:'):
                json_key = field[5:]
                row[field] = log.additional_fields.get(json_key) if log.additional_fields else None
            else:
                row[field] = getattr(log, field, None)
        report_data.append(row)
    
    return jsonify({
        'report': report_data,
        'total': len(report_data),
        'fields': fields,
        'template_name': template.name
    }), 200


# Routes - Log Admin
@app.route('/api/logadmin/users', methods=['GET'])
@require_auth
@require_role('logadmin')
def logadmin_list_users():
    """List all users with log info (logadmin only)"""
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': u.id,
            'callsign': u.callsign,
            'log_count': len(u.log_entries),
            'created_at': u.created_at.isoformat()
        } for u in users]
    }), 200


@app.route('/api/logadmin/users/<int:user_id>/logs', methods=['GET'])
@require_auth
@require_role('logadmin')
def logadmin_get_user_logs(user_id):
    """Get logs for a specific user (logadmin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Get logs
    pagination = LogEntry.query.filter_by(user_id=user_id).order_by(
        LogEntry.qso_date.desc(), 
        LogEntry.time_on.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    logs = [{
        'id': log.id,
        'qso_date': log.qso_date,
        'time_on': log.time_on,
        'call': log.call,
        'band': log.band,
        'mode': log.mode,
        'freq': log.freq,
        'rst_sent': log.rst_sent,
        'rst_rcvd': log.rst_rcvd,
        'station_callsign': log.station_callsign,
        'comment': log.comment
    } for log in pagination.items]
    
    return jsonify({
        'user': {
            'id': user.id,
            'callsign': user.callsign
        },
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200


@app.route('/api/logadmin/users/<int:user_id>/logs', methods=['DELETE'])
@require_auth
@require_role('logadmin')
def logadmin_reset_user_logs(user_id):
    """Reset (delete all) logs for a specific user (logadmin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    log_count = len(user.log_entries)
    
    # Delete all logs for this user
    LogEntry.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({
        'message': f'Reset complete: {log_count} log entries deleted for {user.callsign}'
    }), 200


# Health check
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


# Database initialization
@app.cli.command('init-db')
def init_db():
    """Initialize the database"""
    db.create_all()
    init_default_templates()
    print('Database initialized!')


def init_default_templates():
    """Initialize default global report templates"""
    # Check if global templates already exist
    existing = ReportTemplate.query.filter_by(is_global=True).count()
    if existing > 0:
        return  # Already initialized
    
    default_templates = [
        {
            'name': 'Grid Square Globetrotter',
            'description': 'Contest Goal: Work as many unique Maidenhead grid squares as possible in 30 days.',
            'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'gridsquare', 'band', 'mode'],
            'filters': {},
            'is_global': True
        },
        {
            'name': 'Band-Hopper',
            'description': 'Contest Goal: Make at least one contact on as many different amateur bands as possible.',
            'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'band', 'mode', 'freq'],
            'filters': {},
            'is_global': True
        },
        {
            'name': 'Elmer\'s Choice (Mode Diversity)',
            'description': 'Contest Goal: Rack up points across three categories: CW, Phone, and Digital modes (FT8/JS8/RTTY).',
            'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'mode', 'band', 'rst_sent', 'rst_rcvd'],
            'filters': {},
            'is_global': True
        }
    ]
    
    for template_data in default_templates:
        template = ReportTemplate(
            user_id=None,  # Global templates have no owner
            name=template_data['name'],
            description=template_data['description'],
            fields=template_data['fields'],
            filters=template_data['filters'],
            is_global=True
        )
        db.session.add(template)
    
    db.session.commit()
    print('Default templates initialized!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_templates()
    app.run(host='0.0.0.0', port=5000, debug=False)
