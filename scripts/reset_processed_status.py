from app import app, db, ImportedName

def reset_processed_status():
    with app.app_context():
        try:
            # Reset all imported names to unprocessed
            ImportedName.query.update({ImportedName.is_processed: False})
            db.session.commit()
            print("Successfully reset processed status for all imported names")
        except Exception as e:
            print(f"Error resetting processed status: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    reset_processed_status() 