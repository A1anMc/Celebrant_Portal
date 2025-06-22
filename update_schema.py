from app import app, db

def update_schema():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        print("Database schema updated successfully")

if __name__ == '__main__':
    update_schema() 