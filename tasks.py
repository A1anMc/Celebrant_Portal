from celery import Celery
import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from app import app, db, ImportSession, ImportedName
from import_csv_data import clean_name, clean_date, clean_fee

# Configure Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.update(app.config)

class FlaskTask(celery.Task):
    """Celery task that ensures tasks have application context."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = FlaskTask

@celery.task(bind=True)
def import_task(self, session_id: int) -> Dict[str, Any]:
    """Process CSV import in chunks."""
    try:
        session = ImportSession.query.get(session_id)
        if not session:
            return {'success': False, 'error': 'Import session not found'}
            
        # Get file path
        file_path = os.path.join(app.instance_path, session.filename)
        if not os.path.exists(file_path):
            session.status = 'failed'
            session.errors = json.dumps(['Import file not found'])
            db.session.commit()
            return {'success': False, 'error': 'Import file not found'}
            
        # Get column mappings
        mappings = json.loads(session.column_mapping)
        
        with open(file_path, 'r') as f:
            # Skip to current chunk
            csv_reader = csv.DictReader(f)
            start_row = session.current_chunk * session.chunk_size
            for _ in range(start_row):
                next(csv_reader, None)
            
            # Process chunk
            chunk_errors = []
            row_num = start_row + 1  # 1-based row numbers
            processed_in_chunk = 0
            
            while processed_in_chunk < session.chunk_size:
                try:
                    # Check if import was paused or cancelled
                    session = ImportSession.query.get(session_id)
                    if session.status != 'processing':
                        return {'success': True, 'status': session.status}
                    
                    # Get next row
                    try:
                        row = next(csv_reader)
                    except StopIteration:
                        break
                    
                    # Map and clean data
                    try:
                        # Get couple names
                        couple_field = row[mappings['Couple']] if mappings.get('Couple') else None
                        if not couple_field:
                            chunk_errors.append(f"Row {row_num}: Missing couple names")
                            continue
                            
                        if '&' in couple_field:
                            names = couple_field.split('&')
                        else:
                            names = couple_field.split('and')
                            
                        partner1_name = clean_name(names[0])
                        partner2_name = clean_name(names[1]) if len(names) > 1 else ''
                        
                        # Parse date
                        ceremony_date = None
                        date_field = row[mappings['Date']] if mappings.get('Date') else None
                        if date_field:
                            ceremony_date = clean_date(date_field)
                            if not ceremony_date:
                                chunk_errors.append(f"Row {row_num}: Invalid date format - {date_field}")
                        
                        # Create ImportedName record
                        imported_name = ImportedName(
                            partner1_name=partner1_name,
                            partner2_name=partner2_name,
                            ceremony_date=ceremony_date,
                            location=row[mappings['Location']].strip() if mappings.get('Location') else '',
                            guest_count=row[mappings['Guest Count']].strip() if mappings.get('Guest Count') else '',
                            ceremony_time=row[mappings['Ceremony Time']].strip() if mappings.get('Ceremony Time') else '',
                            role=row[mappings['Role']].strip() if mappings.get('Role') else '',
                            package=row[mappings['Package']].strip() if mappings.get('Package') else '',
                            fee=clean_fee(row[mappings['Fee']]) if mappings.get('Fee') else None,
                            travel_fee=clean_fee(row[mappings['Travel Fee']]) if mappings.get('Travel Fee') else None,
                            vows=row[mappings['Vows']].strip() if mappings.get('Vows') else '',
                            confirmed=row[mappings['Confirmed']].strip() if mappings.get('Confirmed') else '',
                            notes=row[mappings['Notes']].strip() if mappings.get('Notes') else ''
                        )
                        
                        # Check for duplicates
                        existing = ImportedName.query.filter_by(
                            partner1_name=partner1_name,
                            partner2_name=partner2_name
                        ).first()
                        
                        if existing:
                            chunk_errors.append(f"Row {row_num}: Duplicate couple - {partner1_name} & {partner2_name}")
                            continue
                        
                        db.session.add(imported_name)
                        processed_in_chunk += 1
                        
                    except Exception as e:
                        chunk_errors.append(f"Row {row_num}: Error processing row - {str(e)}")
                        continue
                        
                    row_num += 1
                    
                except Exception as e:
                    chunk_errors.append(f"Error processing chunk: {str(e)}")
                    break
            
            try:
                # Update session
                session = ImportSession.query.get(session_id)
                session.processed_rows += processed_in_chunk
                session.current_chunk += 1
                session.error_count += len(chunk_errors)
                
                # Update errors
                current_errors = json.loads(session.errors) if session.errors else []
                current_errors.extend(chunk_errors)
                session.errors = json.dumps(current_errors)
                
                # Check if complete
                if session.processed_rows >= session.total_rows:
                    session.status = 'completed'
                    # Clean up temp file
                    os.remove(file_path)
                
                db.session.commit()
                
                # If not complete and still processing, queue next chunk
                if session.status == 'processing' and session.processed_rows < session.total_rows:
                    import_task.delay(session_id)
                
                return {
                    'success': True,
                    'processed': processed_in_chunk,
                    'errors': chunk_errors
                }
                
            except Exception as e:
                return {'success': False, 'error': f"Error updating session: {str(e)}"}
            
    except Exception as e:
        try:
            session = ImportSession.query.get(session_id)
            session.status = 'failed'
            session.errors = json.dumps([f"Fatal error: {str(e)}"])
            db.session.commit()
        except:
            pass
        return {'success': False, 'error': str(e)} 