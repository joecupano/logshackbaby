#!/usr/bin/env python3
"""
Database migration: Add shared_with_role column to report_templates table
Run this script to update existing databases with the new column
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from sqlalchemy import text

def migrate_add_shared_role():
    """Add shared_with_role column to report_templates table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='report_templates' 
                AND column_name='shared_with_role'
            """))
            
            if result.fetchone():
                print('✅ Column shared_with_role already exists in report_templates table')
                return
            
            print('Adding shared_with_role column to report_templates table...')
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE report_templates 
                ADD COLUMN shared_with_role VARCHAR(20) NULL
            """))
            
            db.session.commit()
            print('✅ Successfully added shared_with_role column!')
            print('\nContestAdmins can now create templates shared with all Contest Admins.')
            
        except Exception as e:
            print(f'❌ Error during migration: {e}')
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    try:
        migrate_add_shared_role()
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        sys.exit(1)
