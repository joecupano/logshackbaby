#!/usr/bin/env python3
"""
Initialize default report templates for LogShackBaby
Run this script to create the three global report templates
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, ReportTemplate

def init_default_templates():
    """Initialize default global report templates"""
    with app.app_context():
        # Create all database tables if they don't exist
        print('Ensuring database tables are created...')
        db.create_all()
        print('✅ Database tables ready\n')
        
        # Check if global templates already exist
        existing = ReportTemplate.query.filter_by(is_global=True).count()
        
        if existing > 0:
            print(f'✅ Found {existing} existing global template(s):')
            templates = ReportTemplate.query.filter_by(is_global=True).all()
            for t in templates:
                print(f'   - {t.name}')
            print('\nGlobal templates already initialized!')
            return
        
        print('Creating default global report templates...\n')
        
        default_templates = [
            {
                'name': 'Grid Square Globetrotter',
                'description': 'Track unique Maidenhead grid squares worked. Perfect for 30-day diversity contests.',
                'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'gridsquare', 'band', 'mode'],
                'filters': {},
                'is_global': True
            },
            {
                'name': 'Band-Hopper Challenge',
                'description': 'Make contacts on as many different amateur bands as possible. Explore new frequencies!',
                'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'band', 'mode', 'freq'],
                'filters': {},
                'is_global': True
            },
            {
                'name': 'Elmer\'s Choice (Mode Diversity)',
                'description': 'Work across CW, Phone (SSB/FM), and Digital modes. Become an all-arounder!',
                'fields': ['user_callsign', 'qso_date', 'time_on', 'call', 'mode', 'band', 'rst_sent', 'rst_rcvd'],
                'filters': {},
                'is_global': True
            }
        ]
        
        for template_data in default_templates:
            print(f'Creating: {template_data["name"]}')
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
        print('\n✅ Default templates initialized successfully!')
        print('\nCreated templates:')
        print('   1. Grid Square Globetrotter')
        print('   2. Band-Hopper Challenge')
        print('   3. Elmer\'s Choice (Mode Diversity)')

if __name__ == '__main__':
    try:
        init_default_templates()
    except Exception as e:
        print(f'❌ Error initializing templates: {e}')
        sys.exit(1)
