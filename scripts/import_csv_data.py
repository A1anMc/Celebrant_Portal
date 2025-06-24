from app import app, db, ImportedName
import csv
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional

def clean_name(name: str) -> str:
    """Clean and standardize a name."""
    # Remove extra whitespace
    name = ' '.join(name.split())
    # Capitalize each word
    name = ' '.join(word.capitalize() for word in name.split())
    return name

def clean_phone(phone: str) -> Optional[str]:
    """Clean and standardize a phone number."""
    if not phone:
        return None
    # Remove all non-numeric characters
    numbers = re.sub(r'[^\d+]', '', phone)
    # Handle international format
    if numbers.startswith('+61'):
        numbers = '0' + numbers[3:]
    # Validate Australian mobile or landline
    if re.match(r'^(?:0[2378]|04)\d{8}$', numbers):
        return numbers
    return None

def clean_date(date_str: str) -> Optional[datetime]:
    """Clean and parse a date string."""
    if not date_str:
        return None
        
    date_formats = [
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def clean_fee(fee: str) -> Optional[str]:
    """Clean and standardize a fee string."""
    if not fee:
        return None
    # Remove any non-fee characters and standardize format
    fee = fee.strip().replace(' ', '')
    # Extract numbers and symbols
    matches = re.findall(r'(\$?\d+(?:,\d{3})*(?:\.\d{2})?(?:\+?(?:\$?\d+(?:,\d{3})*(?:\.\d{2})?)?)?)', fee)
    if matches:
        return ' + '.join(matches)
    return None

def validate_row(row: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validate a CSV row and return (is_valid, error_messages)."""
    errors = []
    
    # Required field validation
    if not row.get('Couple'):
        errors.append("Couple field is required")
        return False, errors
        
    # Couple name format validation
    if '&' not in row['Couple'] and 'and' not in row['Couple'].lower():
        errors.append("Couple field must contain '&' or 'and' between names")
    
    # Date validation if provided
    if row.get('Date'):
        if not clean_date(row['Date']):
            errors.append(f"Invalid date format: {row['Date']}")
    
    # Guest count validation if provided
    if row.get('Guest Count'):
        if not re.match(r'^(?:Approx\.)?\s*\d+(?:-\d+)?(?:\s*(?:people|guests))?\s*$', row['Guest Count'], re.IGNORECASE):
            errors.append(f"Invalid guest count format: {row['Guest Count']}")
    
    # Time validation if provided
    if row.get('Ceremony Time'):
        if not re.match(r'^(?:0?[1-9]|1[0-2]):[0-5][0-9]\s*(?:AM|PM)|(?:[01]?[0-9]|2[0-3]):[0-5][0-9]$', row['Ceremony Time'], re.IGNORECASE):
            errors.append(f"Invalid time format: {row['Ceremony Time']}")
    
    return len(errors) == 0, errors

def import_csv_data(filename: str) -> Tuple[int, List[str]]:
    """
    Import CSV data with validation and cleanup.
    Returns (number_of_records_imported, error_messages)
    """
    errors = []
    imported_count = 0
    
    with app.app_context():
        try:
            with open(filename, 'r') as file:
                csv_data = csv.DictReader(file)
                
                # Validate headers
                required_headers = ['Couple', 'Date', 'Location', 'Guest Count', 
                                 'Ceremony Time', 'Role', 'Package', 'Fee', 
                                 'Travel Fee', 'Vows', 'Confirmed', 'Notes']
                missing_headers = [h for h in required_headers if h not in csv_data.fieldnames]
                if missing_headers:
                    return 0, [f"Missing required headers: {', '.join(missing_headers)}"]
                
                for row_num, row in enumerate(csv_data, start=2):  # Start at 2 to account for header row
                    try:
                        # Validate row
                        is_valid, row_errors = validate_row(row)
                        if not is_valid:
                            errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
                            continue
                        
                        # Split and clean couple names
                        if '&' in row['Couple']:
                            names = row['Couple'].split('&')
                        else:
                            names = row['Couple'].split('and')
                        
                        partner1_name = clean_name(names[0])
                        partner2_name = clean_name(names[1]) if len(names) > 1 else ''
                        
                        # Parse and validate date
                        ceremony_date = None
                        if row.get('Date'):
                            ceremony_date = clean_date(row['Date'])
                        
                        # Clean up fee information
                        fee = clean_fee(row.get('Fee', ''))
                        travel_fee = clean_fee(row.get('Travel Fee', ''))
                        
                        # Create new ImportedName record
                        imported_name = ImportedName(
                            partner1_name=partner1_name,
                            partner2_name=partner2_name,
                            ceremony_date=ceremony_date,
                            location=row.get('Location', '').strip(),
                            guest_count=row.get('Guest Count', '').strip(),
                            ceremony_time=row.get('Ceremony Time', '').strip(),
                            role=row.get('Role', '').strip(),
                            package=row.get('Package', '').strip(),
                            fee=fee,
                            travel_fee=travel_fee,
                            vows=row.get('Vows', '').strip(),
                            confirmed=row.get('Confirmed', '').strip(),
                            notes=row.get('Notes', '').strip()
                        )
                        
                        # Check for duplicates
                        existing = ImportedName.query.filter_by(
                            partner1_name=partner1_name,
                            partner2_name=partner2_name
                        ).first()
                        
                        if existing:
                            errors.append(f"Row {row_num}: Duplicate couple - {partner1_name} & {partner2_name}")
                            continue
                        
                        db.session.add(imported_name)
                        imported_count += 1
                        print(f"Imported: {partner1_name} & {partner2_name}")
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error processing row - {str(e)}")
                        continue
                
                if imported_count > 0:
                    try:
                        db.session.commit()
                        print(f"\nSuccessfully imported {imported_count} couples")
                    except Exception as e:
                        db.session.rollback()
                        return 0, [f"Database error: {str(e)}"]
                
                return imported_count, errors
                
        except Exception as e:
            return 0, [f"Error reading CSV file: {str(e)}"]

if __name__ == '__main__':
    imported, errors = import_csv_data('Alan_McCarthy_Upcoming_Weddings.csv')
    print(f"\nImported {imported} couples")
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"- {error}") 