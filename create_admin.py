from app import app, db, User

def create_admin():
    """Create an admin user."""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin = User(
            email='admin@example.com',
            name='Admin User',
            is_admin=True
        )
        admin.set_password('admin123')  # Change this password in production!
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("\nIMPORTANT: Please change this password immediately after logging in!")

if __name__ == '__main__':
    create_admin() 