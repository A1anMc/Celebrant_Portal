from app import app, db, ImportedName, User
from services.gmail_service import GmailService
import sys

def scan_emails_for_couples(days_to_scan=90):
    with app.app_context():
        # Get the admin user
        admin_user = User.query.filter_by(email='admin@celebrant.local').first()
        if not admin_user:
            print("Admin user not found! Please run create_admin.py first.")
            return
            
        # Initialize Gmail service
        gmail_service = GmailService()
        
        # Check if we have any unprocessed names
        unprocessed_count = ImportedName.query.filter_by(is_processed=False).count()
        if unprocessed_count == 0:
            print("No unprocessed couples found. Have you imported the CSV data?")
            return
            
        print(f"Found {unprocessed_count} unprocessed couples")
        print(f"Scanning emails from the last {days_to_scan} days...")
        
        # Start the scanning process
        try:
            results = gmail_service.scan_and_process_emails(days_to_scan=days_to_scan, user_id=admin_user.id)
            
            # Print results
            print("\nScan Results:")
            for result in results:
                print(f"- {result}")
                
        except Exception as e:
            print(f"Error during email scan: {str(e)}")
            if "credentials" in str(e).lower():
                print("\nPlease make sure you're logged in to Gmail first!")
                print("Visit http://localhost:8086/scan_emails in your browser to authenticate.")
            sys.exit(1)

if __name__ == '__main__':
    # Default to scanning last 90 days, but allow command line override
    days = 90
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days value: {sys.argv[1]}. Using default of 90 days.")
    
    scan_emails_for_couples(days) 