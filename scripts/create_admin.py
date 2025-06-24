import os
from app import app, db, User

def create_admin():
    """Create an admin user."""
    with app.app_context():
        # Get admin details from environment or use defaults
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@celebrant.local')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_name = os.environ.get('ADMIN_NAME', 'Admin User')
        
        # Check if admin already exists
        admin = User.query.filter_by(email=admin_email).first()
        if admin:
            print(f"Admin user already exists: {admin_email}")
            # Update password if provided
            if os.environ.get('ADMIN_PASSWORD'):
                admin.set_password(admin_password)
                db.session.commit()
                print("Admin password updated!")
            return
        
        # Create new admin user
        admin = User(
            username='admin',
            email=admin_email,
            name=admin_name,
            is_admin=True
        )
        admin.set_password(admin_password)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("\nTo customize login details, set environment variables:")
        print("export ADMIN_EMAIL='your-email@domain.com'")
        print("export ADMIN_PASSWORD='your-secure-password'")
        print("export ADMIN_NAME='Your Name'")
        print("\nIMPORTANT: Please change this password immediately after logging in!")

if __name__ == '__main__':
    create_admin() 