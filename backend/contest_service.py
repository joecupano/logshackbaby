"""
Contest Management Service for LogShackBaby
Handles contest creation, scoring, and leaderboard generation
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
from sqlalchemy import func, and_

from models import db, User, Session, Contest, ContestEntry, LogEntry

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://logshackbaby:logshackbaby@db:5432/logshackbaby'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')

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


# Contest Management Endpoints (contestadmin only)

@app.route('/api/contests', methods=['POST'])
@require_auth
@require_role('contestadmin')
def create_contest():
    """Create a new contest"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        if end_date <= start_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        contest = Contest(
            name=data['name'],
            description=data.get('description', ''),
            created_by=request.current_user.id,
            start_date=start_date,
            end_date=end_date,
            rules=data.get('rules', {}),
            scoring=data.get('scoring', {'qso_points': 1}),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(contest)
        db.session.commit()
        
        return jsonify({
            'id': contest.id,
            'name': contest.name,
            'description': contest.description,
            'start_date': contest.start_date.isoformat(),
            'end_date': contest.end_date.isoformat(),
            'rules': contest.rules,
            'scoring': contest.scoring,
            'is_active': contest.is_active,
            'created_at': contest.created_at.isoformat()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create contest: {str(e)}'}), 500


@app.route('/api/contests', methods=['GET'])
@require_auth
def list_contests():
    """List all contests (visible to all authenticated users)"""
    contests = Contest.query.order_by(Contest.start_date.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'start_date': c.start_date.isoformat(),
        'end_date': c.end_date.isoformat(),
        'rules': c.rules,
        'scoring': c.scoring,
        'is_active': c.is_active,
        'created_at': c.created_at.isoformat()
    } for c in contests]), 200


@app.route('/api/contests/<int:contest_id>', methods=['GET'])
@require_auth
def get_contest(contest_id):
    """Get contest details"""
    contest = Contest.query.get_or_404(contest_id)
    
    return jsonify({
        'id': contest.id,
        'name': contest.name,
        'description': contest.description,
        'start_date': contest.start_date.isoformat(),
        'end_date': contest.end_date.isoformat(),
        'rules': contest.rules,
        'scoring': contest.scoring,
        'is_active': contest.is_active,
        'created_at': contest.created_at.isoformat(),
        'entry_count': len(contest.entries)
    }), 200


@app.route('/api/contests/<int:contest_id>', methods=['PUT'])
@require_auth
@require_role('contestadmin')
def update_contest(contest_id):
    """Update a contest"""
    contest = Contest.query.get_or_404(contest_id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            contest.name = data['name']
        if 'description' in data:
            contest.description = data['description']
        if 'start_date' in data:
            contest.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            contest.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        if 'rules' in data:
            contest.rules = data['rules']
        if 'scoring' in data:
            contest.scoring = data['scoring']
        if 'is_active' in data:
            contest.is_active = data['is_active']
        
        contest.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Contest updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update contest: {str(e)}'}), 500


@app.route('/api/contests/<int:contest_id>', methods=['DELETE'])
@require_auth
@require_role('contestadmin')
def delete_contest(contest_id):
    """Delete a contest"""
    contest = Contest.query.get_or_404(contest_id)
    
    try:
        db.session.delete(contest)
        db.session.commit()
        return jsonify({'message': 'Contest deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete contest: {str(e)}'}), 500


@app.route('/api/contests/<int:contest_id>/populate', methods=['POST'])
@require_auth
@require_role('contestadmin')
def populate_contest(contest_id):
    """
    Populate contest entries by finding all eligible QSOs from all users
    based on contest rules (date range, bands, modes)
    """
    contest = Contest.query.get_or_404(contest_id)
    
    try:
        # Build query for eligible log entries
        query = LogEntry.query.filter(
            and_(
                LogEntry.qso_date >= contest.start_date.strftime('%Y%m%d'),
                LogEntry.qso_date <= contest.end_date.strftime('%Y%m%d')
            )
        )
        
        # Apply rules filters if specified
        rules = contest.rules or {}
        if 'bands' in rules and rules['bands']:
            query = query.filter(LogEntry.band.in_(rules['bands']))
        if 'modes' in rules and rules['modes']:
            query = query.filter(LogEntry.mode.in_(rules['modes']))
        
        eligible_logs = query.all()
        
        # Calculate scoring
        scoring = contest.scoring or {'qso_points': 1}
        base_points = scoring.get('qso_points', 1)
        band_multiplier = scoring.get('band_multiplier', {})
        mode_bonus = scoring.get('mode_bonus', {})
        
        new_entries = 0
        for log in eligible_logs:
            # Check if entry already exists
            existing = ContestEntry.query.filter_by(
                contest_id=contest.id,
                log_entry_id=log.id
            ).first()
            
            if not existing:
                # Calculate points
                points = base_points
                if log.band in band_multiplier:
                    points *= band_multiplier[log.band]
                if log.mode in mode_bonus:
                    points += mode_bonus[log.mode]
                
                entry = ContestEntry(
                    contest_id=contest.id,
                    user_id=log.user_id,
                    log_entry_id=log.id,
                    points=points,
                    is_valid=True
                )
                db.session.add(entry)
                new_entries += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contest populated successfully',
            'new_entries': new_entries,
            'total_entries': len(contest.entries)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to populate contest: {str(e)}'}), 500


# Leaderboard Endpoints (read-only for all users)

@app.route('/api/contests/<int:contest_id>/leaderboard', methods=['GET'])
@require_auth
def get_leaderboard(contest_id):
    """Get contest leaderboard"""
    contest = Contest.query.get_or_404(contest_id)
    
    # Aggregate scores per user
    leaderboard = db.session.query(
        User.callsign,
        User.id,
        func.count(ContestEntry.id).label('qso_count'),
        func.sum(ContestEntry.points).label('total_points')
    ).join(
        ContestEntry, User.id == ContestEntry.user_id
    ).filter(
        and_(
            ContestEntry.contest_id == contest_id,
            ContestEntry.is_valid == True
        )
    ).group_by(
        User.id, User.callsign
    ).order_by(
        func.sum(ContestEntry.points).desc()
    ).all()
    
    # Format results with ranking
    results = []
    rank = 1
    for entry in leaderboard:
        results.append({
            'rank': rank,
            'callsign': entry.callsign,
            'user_id': entry.id,
            'qso_count': entry.qso_count,
            'total_points': float(entry.total_points or 0)
        })
        rank += 1
    
    return jsonify({
        'contest_id': contest.id,
        'contest_name': contest.name,
        'leaderboard': results
    }), 200


@app.route('/api/contests/<int:contest_id>/leaderboard/<int:user_id>', methods=['GET'])
@require_auth
def get_user_contest_details(contest_id, user_id):
    """Get detailed contest entries for a specific user"""
    contest = Contest.query.get_or_404(contest_id)
    user = User.query.get_or_404(user_id)
    
    entries = ContestEntry.query.filter_by(
        contest_id=contest_id,
        user_id=user_id,
        is_valid=True
    ).join(LogEntry).order_by(LogEntry.qso_date, LogEntry.time_on).all()
    
    results = []
    for entry in entries:
        log = entry.log_entry
        results.append({
            'id': entry.id,
            'qso_date': log.qso_date,
            'time_on': log.time_on,
            'call': log.call,
            'band': log.band,
            'mode': log.mode,
            'points': float(entry.points)
        })
    
    total_points = sum(e.points for e in entries)
    
    return jsonify({
        'contest_id': contest.id,
        'contest_name': contest.name,
        'callsign': user.callsign,
        'qso_count': len(entries),
        'total_points': float(total_points),
        'entries': results
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Contest service information and available endpoints"""
    return jsonify({
        'service': 'LogShackBaby Contest Management Service',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'health': {
                'path': '/health',
                'method': 'GET',
                'auth': False,
                'description': 'Health check endpoint'
            },
            'contests': {
                'list': {'path': '/api/contests', 'method': 'GET', 'auth': True, 'role': 'user'},
                'create': {'path': '/api/contests', 'method': 'POST', 'auth': True, 'role': 'contestadmin'},
                'get': {'path': '/api/contests/{id}', 'method': 'GET', 'auth': True, 'role': 'user'},
                'update': {'path': '/api/contests/{id}', 'method': 'PUT', 'auth': True, 'role': 'contestadmin'},
                'delete': {'path': '/api/contests/{id}', 'method': 'DELETE', 'auth': True, 'role': 'contestadmin'},
                'populate': {'path': '/api/contests/{id}/populate', 'method': 'POST', 'auth': True, 'role': 'contestadmin'},
                'leaderboard': {'path': '/api/contests/{id}/leaderboard', 'method': 'GET', 'auth': True, 'role': 'user'},
                'user_details': {'path': '/api/contests/{id}/leaderboard/{user_id}', 'method': 'GET', 'auth': True, 'role': 'user'}
            }
        },
        'authentication': 'Required: X-Session-Token header for all authenticated endpoints',
        'documentation': 'See GAMIFICATION.md for full API documentation'
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'contest'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=os.getenv('FLASK_ENV') == 'development')
