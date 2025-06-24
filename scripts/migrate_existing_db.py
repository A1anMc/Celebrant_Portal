#!/usr/bin/env python3
"""
Migration script to update existing database with new legal forms schema
"""
import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate existing database to new schema."""
    print("🔄 Migrating Existing Database to Legal Forms Schema")
    print("=" * 55)
    
    db_files = ['celebrant.db', 'celebrant_dev.db']
    
    for db_file in db_files:
        if not os.path.exists(db_file):
            print(f"⏭️  Skipping {db_file} - doesn't exist")
            continue
            
        print(f"\n📄 Processing {db_file}...")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print(f"  ⏭️  No users table found in {db_file}")
                conn.close()
                continue
            
            # Check current users schema
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"  📋 Current columns: {', '.join(columns)}")
            
            # Add missing columns
            new_columns = [
                ('role', 'VARCHAR(50)', 'admin'),
                ('is_active', 'BOOLEAN', '1'),
                ('organization_id', 'INTEGER', 'NULL'),
                ('last_login', 'DATETIME', 'NULL')
            ]
            
            for col_name, col_type, default_value in new_columns:
                if col_name not in columns:
                    try:
                        if default_value == 'NULL':
                            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                        else:
                            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type} DEFAULT {default_value}")
                        print(f"  ✅ Added column: {col_name}")
                    except sqlite3.Error as e:
                        print(f"  ⚠️  Could not add {col_name}: {e}")
                else:
                    print(f"  ✅ Column {col_name} already exists")
            
            # Create organizations table if it doesn't exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'")
            if not cursor.fetchone():
                print("  📋 Creating organizations table...")
                cursor.execute("""
                    CREATE TABLE organizations (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        contact_email VARCHAR(255),
                        contact_phone VARCHAR(50),
                        address TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("  ✅ Organizations table created")
            
            # Create legal forms tables
            legal_tables = [
                ('legal_form_submissions', """
                    CREATE TABLE legal_form_submissions (
                        id INTEGER PRIMARY KEY,
                        organization_id INTEGER NOT NULL,
                        couple_id INTEGER NOT NULL,
                        form_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'not_started',
                        legal_deadline DATE,
                        submission_date DATETIME,
                        file_path VARCHAR(500),
                        file_name VARCHAR(255),
                        file_size INTEGER,
                        validation_status VARCHAR(50),
                        validation_notes TEXT,
                        reminder_schedule TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id),
                        FOREIGN KEY (couple_id) REFERENCES couples(id)
                    )
                """),
                ('compliance_alerts', """
                    CREATE TABLE compliance_alerts (
                        id INTEGER PRIMARY KEY,
                        organization_id INTEGER NOT NULL,
                        couple_id INTEGER,
                        form_submission_id INTEGER,
                        alert_type VARCHAR(50) NOT NULL,
                        severity VARCHAR(20) DEFAULT 'medium',
                        title VARCHAR(255) NOT NULL,
                        message TEXT,
                        is_resolved BOOLEAN DEFAULT 0,
                        resolved_at DATETIME,
                        resolved_by INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id),
                        FOREIGN KEY (couple_id) REFERENCES couples(id),
                        FOREIGN KEY (form_submission_id) REFERENCES legal_form_submissions(id)
                    )
                """),
                ('reminder_logs', """
                    CREATE TABLE reminder_logs (
                        id INTEGER PRIMARY KEY,
                        organization_id INTEGER NOT NULL,
                        couple_id INTEGER NOT NULL,
                        form_submission_id INTEGER,
                        reminder_type VARCHAR(50) NOT NULL,
                        recipient VARCHAR(255) NOT NULL,
                        subject VARCHAR(500),
                        content TEXT,
                        days_before_deadline INTEGER,
                        template_used VARCHAR(100),
                        delivery_status VARCHAR(50) DEFAULT 'pending',
                        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id),
                        FOREIGN KEY (couple_id) REFERENCES couples(id),
                        FOREIGN KEY (form_submission_id) REFERENCES legal_form_submissions(id)
                    )
                """)
            ]
            
            for table_name, create_sql in legal_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    print(f"  📋 Creating {table_name} table...")
                    cursor.execute(create_sql)
                    print(f"  ✅ {table_name} table created")
                else:
                    print(f"  ✅ {table_name} table already exists")
            
            # Add organization_id to couples table if missing
            cursor.execute("PRAGMA table_info(couples)")
            couple_columns = [row[1] for row in cursor.fetchall()]
            if 'organization_id' not in couple_columns:
                try:
                    cursor.execute("ALTER TABLE couples ADD COLUMN organization_id INTEGER")
                    print("  ✅ Added organization_id to couples table")
                except sqlite3.Error as e:
                    print(f"  ⚠️  Could not add organization_id to couples: {e}")
            
            # Create a default organization if none exists
            cursor.execute("SELECT COUNT(*) FROM organizations")
            if cursor.fetchone()[0] == 0:
                print("  🏢 Creating default organization...")
                cursor.execute("""
                    INSERT INTO organizations (name, description, contact_email, is_active)
                    VALUES ('Default Organization', 'Default celebrant organization', 'admin@celebrant.com', 1)
                """)
                
                # Get the organization ID
                cursor.execute("SELECT id FROM organizations WHERE name='Default Organization'")
                org_id = cursor.fetchone()[0]
                
                # Update existing users to belong to this organization
                cursor.execute("UPDATE users SET organization_id = ? WHERE organization_id IS NULL", (org_id,))
                cursor.execute("UPDATE couples SET organization_id = ? WHERE organization_id IS NULL", (org_id,))
                
                print(f"  ✅ Default organization created (ID: {org_id})")
                print("  ✅ Existing users and couples assigned to default organization")
            
            conn.commit()
            conn.close()
            
            print(f"  🎉 {db_file} migration completed successfully!")
            
        except Exception as e:
            print(f"  ❌ Migration failed for {db_file}: {e}")
            if 'conn' in locals():
                conn.close()
            return False
    
    return True

def main():
    """Main migration function."""
    print("🚀 Legal Forms Database Migration")
    print("=" * 40)
    
    if migrate_database():
        print("\n✅ All database migrations completed successfully!")
        print("\nNext steps:")
        print("1. python run_celery.py (in separate terminal)")
        print("2. python app.py")
        print("3. Visit: http://localhost:8085/legal-forms/dashboard")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1) 