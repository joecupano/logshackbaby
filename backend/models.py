"""
Database models for LogShackBaby Amateur Radio Log Server
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')  # user, contestadmin, logadmin, sysop
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    log_entries = db.relationship('LogEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.callsign}>'
    
    def has_role(self, role):
        """Check if user has a specific role or higher"""
        role_hierarchy = {'user': 0, 'contestadmin': 1, 'logadmin': 2, 'sysop': 3}
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(role, 0)


class APIKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    key_prefix = db.Column(db.String(8), nullable=False)  # First 8 chars for identification
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<APIKey {self.key_prefix}...>'


class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # ADIF core fields
    qso_date = db.Column(db.String(8), nullable=False)  # YYYYMMDD
    time_on = db.Column(db.String(6), nullable=False)   # HHMMSS
    call = db.Column(db.String(20), nullable=False, index=True)
    band = db.Column(db.String(10), nullable=True)
    mode = db.Column(db.String(20), nullable=True)
    freq = db.Column(db.String(20), nullable=True)
    rst_sent = db.Column(db.String(10), nullable=True)
    rst_rcvd = db.Column(db.String(10), nullable=True)
    
    # Optional fields
    qso_date_off = db.Column(db.String(8), nullable=True)
    time_off = db.Column(db.String(6), nullable=True)
    station_callsign = db.Column(db.String(20), nullable=True, index=True)
    my_gridsquare = db.Column(db.String(10), nullable=True)
    gridsquare = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    qth = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    
    # Additional ADIF fields stored as JSON
    additional_fields = db.Column(db.JSON, nullable=True)
    
    # Metadata
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    qso_hash = db.Column(db.String(64), nullable=False, index=True)  # For deduplication
    
    # Unique constraint for deduplication
    __table_args__ = (
        db.UniqueConstraint('user_id', 'qso_hash', name='unique_qso_per_user'),
    )
    
    def __repr__(self):
        return f'<LogEntry {self.station_callsign or "?"} -> {self.call} on {self.qso_date}>'


class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mfa_required = db.Column(db.Boolean, default=False)
    mfa_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Session {self.session_token[:8]}... for user {self.user_id}>'


class UploadLog(db.Model):
    __tablename__ = 'upload_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_records = db.Column(db.Integer, default=0)
    new_records = db.Column(db.Integer, default=0)
    duplicate_records = db.Column(db.Integer, default=0)
    error_records = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='processing')  # processing, completed, failed
    
    def __repr__(self):
        return f'<UploadLog {self.filename} - {self.status}>'


class Contest(db.Model):
    __tablename__ = 'contests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Contest rules (stored as JSON)
    rules = db.Column(db.JSON, nullable=True)
    # Example rules: {"bands": ["20M", "40M"], "modes": ["SSB", "CW"], "min_qsos": 10}
    
    # Scoring configuration (stored as JSON)
    scoring = db.Column(db.JSON, nullable=True)
    # Example scoring: {"qso_points": 1, "band_multiplier": {"20M": 2, "40M": 1}, "mode_bonus": {"CW": 2}}
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = db.relationship('ContestEntry', backref='contest', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contest {self.name}>'


class ContestEntry(db.Model):
    __tablename__ = 'contest_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    log_entry_id = db.Column(db.Integer, db.ForeignKey('log_entries.id'), nullable=False)
    
    # Scoring
    points = db.Column(db.Float, default=0.0)
    is_valid = db.Column(db.Boolean, default=True)
    validation_notes = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    log_entry = db.relationship('LogEntry', backref='contest_entries')
    
    # Unique constraint: each log entry can only be in a contest once
    __table_args__ = (
        db.UniqueConstraint('contest_id', 'log_entry_id', name='unique_log_per_contest'),
    )
    
    def __repr__(self):
        return f'<ContestEntry contest:{self.contest_id} user:{self.user_id}>'
