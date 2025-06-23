import os
import pickle
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Union, Mapping
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email
from email.utils import parsedate_to_datetime
import re
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Configure logging
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.readonly'  # Added for Drive template import
]

class GmailService:
    def __init__(self):
        self.service = None  # type: Any
        self.creds = None    # type: Optional[Credentials]
        self.flow = None     # type: Optional[InstalledAppFlow]
        self.SCOPES = SCOPES  # Use the same scopes defined at module level
        self.email_templates = self._load_email_templates()
        self.thread_cache = {}

    def authenticate(self) -> Optional[str]:
        """Authenticate with Gmail API using OAuth 2.0.
        Returns the authorization URL if authorization is needed, None otherwise."""
        if not os.path.exists('credentials.json'):
            raise FileNotFoundError(
                "credentials.json not found. Please download it from Google Cloud Console "
                "and place it in the application root directory."
            )

        try:
            # Configure for non-local server
            self.flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Use manual auth flow
            )
            # Get the authorization URL
            auth_url, _ = self.flow.authorization_url()
            return auth_url
        except Exception as e:
            raise Exception(
                f"Failed to authenticate with Google: {str(e)}. "
                "Make sure you have valid credentials.json and "
                "proper permissions."
            )

    def complete_authentication(self, code: str) -> None:
        """Complete the authentication process with the provided code."""
        try:
            if not self.flow:
                self.flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
            
            # Exchange the authorization code for credentials
            token = self.flow.fetch_token(code=code)
            
            # Convert OAuth2Token to Credentials
            if token and not isinstance(token, Credentials):
                scope = token.get('scope')
                # Handle scope whether it's a string, list, or None
                if isinstance(scope, str):
                    scopes = scope.split(' ')
                elif isinstance(scope, list):
                    scopes = scope
                else:
                    scopes = SCOPES

                self.creds = Credentials(
                    token=token.get('access_token'),
                    refresh_token=token.get('refresh_token'),
                    token_uri=token.get('token_uri'),
                    client_id=token.get('client_id'),
                    client_secret=token.get('client_secret'),
                    scopes=scopes
                )
            else:
                self.creds = token
            
            # Save the credentials
            with open('token.pickle', 'wb') as token_file:
                pickle.dump(self.creds, token_file)
                
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            raise Exception(f"Failed to complete authentication: {str(e)}")

    def ensure_authenticated(self) -> None:
        """Ensure we have valid credentials and a service instance."""
        print("Checking for credentials.json...")
        if not os.path.exists('credentials.json'):
            raise Exception(
                "Gmail API credentials not found. Please follow these steps:\n"
                "1. Go to Google Cloud Console (https://console.cloud.google.com)\n"
                "2. Create a project or select an existing one\n"
                "3. Enable the Gmail API\n"
                "4. Go to Credentials\n"
                "5. Create OAuth 2.0 Client ID (Application type: Desktop)\n"
                "6. Download the credentials and save as 'credentials.json'\n"
                "7. Place the file in the application root directory"
            )
                
        print("Checking for token.pickle...")
        if os.path.exists('token.pickle'):
            print("Found token.pickle, loading credentials...")
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                
                # Check if credentials are expired and refresh if possible
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Credentials expired, attempting to refresh...")
                    try:
                        self.creds.refresh(Request())
                        print("Successfully refreshed credentials")
                        # Save the refreshed credentials
                        with open('token.pickle', 'wb') as token_file:
                            pickle.dump(self.creds, token_file)
                    except Exception as e:
                        print(f"Failed to refresh credentials: {str(e)}")
                        os.remove('token.pickle')  # Remove invalid token
                        raise Exception(
                            f"Failed to refresh credentials: {str(e)}\n"
                            "Please re-authenticate by visiting the scan emails page."
                        )
                
                if self.creds and not self.creds.expired:
                    print("Building Gmail service with valid credentials...")
                    self.service = build('gmail', 'v1', credentials=self.creds)
                else:
                    print("Credentials expired and couldn't be refreshed")
                    os.remove('token.pickle')  # Remove invalid token
                    raise Exception(
                        "Gmail API credentials have expired. "
                        "Please re-authenticate by visiting the scan emails page."
                    )
        else:
            print("No token.pickle found, starting OAuth flow...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                print("Successfully obtained new credentials")
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
                print("Saved credentials to token.pickle")
                
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                print(f"Error during OAuth flow: {str(e)}")
                raise Exception(
                    f"Failed to authenticate with Gmail: {str(e)}. "
                    "Please ensure you have valid credentials.json and "
                    "proper permissions."
                )

    def search_emails(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for emails matching the query."""
        try:
            results = []
            page_token = None
            
            while True:
                response = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=min(max_results - len(results), 100)
                ).execute()
                
                messages = response.get('messages', [])
                
                for message in messages:
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Get thread messages
                    thread_messages = self._get_thread_messages(msg['threadId'])
                    msg['thread_messages'] = thread_messages
                    
                    results.append(msg)
                    
                    if len(results) >= max_results:
                        return results
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
            return results
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    def get_email_data(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Get the full email data for a message ID."""
        try:
            print(f"Fetching email data for message {msg_id}")
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            print(f"Successfully fetched email data for message {msg_id}")
            return message
        except Exception as e:
            print(f"Error getting email data: {str(e)}")
            return None

    def get_body_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        """Extract email body from message parts."""
        body = ""
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode()
            elif 'parts' in part:
                body += self.get_body_from_parts(part['parts'])
        return body

    def scan_for_couples(self, days: int = 30) -> List[Dict[str, Any]]:
        """Scan emails with labels indicating waiting for response."""
        self.ensure_authenticated()
        
        # Look for emails labeled as waiting for response
        query = (
            'label:"waiting for alan to respond" OR '
            'label:"waiting for alan" OR '
            'label:"alan to respond" OR '
            'label:"needs alan response" OR '
            'label:"pending alan" OR '
            'label:"alan action required"'
        )
        
        # Get emails
        emails = self.search_emails(query)
        
        couples_data = []
        for email_data in emails:
            # Extract information from emails needing response
            couple_info = self.extract_couple_info(email_data)
            if couple_info:
                couples_data.append(couple_info)
        
        return couples_data

    def get_labels(self) -> List[Dict[str, str]]:
        """Get all available Gmail labels."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except Exception as e:
            print(f"Error getting labels: {e}")
            return []

    def create_label(self, label_name: str) -> Optional[Dict[str, Any]]:
        """Create a new Gmail label if it doesn't exist."""
        try:
            # Ensure we're authenticated
            self.ensure_authenticated()
            
            # First check if label already exists
            existing_labels = self.get_labels()
            for label in existing_labels:
                if label['name'].lower() == label_name.lower():
                    print(f"Label '{label_name}' already exists")
                    return label

            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            try:
                created_label = self.service.users().labels().create(
                    userId='me',
                    body=label_object
                ).execute()
                print(f"Created new label '{label_name}'")
                return created_label
            except Exception as e:
                if 'Label name exists or conflicts' in str(e):
                    # If creation failed due to conflict, try to find the existing label again
                    existing_labels = self.get_labels()
                    for label in existing_labels:
                        if label['name'].lower() == label_name.lower():
                            print(f"Found existing label '{label_name}' after creation attempt")
                            return label
                raise  # Re-raise if it's not a conflict error or we couldn't find the label
                
        except Exception as e:
            print(f"Error creating label '{label_name}': {str(e)}")
            return None

    def ensure_required_labels_exist(self) -> None:
        """Ensure that the required labels exist in Gmail."""
        try:
            # Ensure we're authenticated first
            self.ensure_authenticated()
            
            required_labels = [
                'Waiting for Alan to Respond',
                'Needs Alan Response',
                'Alan Action Required',
                'Wedding 2026'  # Add this since we're also scanning for 2026 weddings
            ]
            
            created_labels = []
            failed_labels = []
            
            for label_name in required_labels:
                try:
                    result = self.create_label(label_name)
                    if result:
                        created_labels.append(label_name)
                    else:
                        failed_labels.append(label_name)
                except Exception as e:
                    print(f"Error creating label '{label_name}': {str(e)}")
                    failed_labels.append(label_name)
            
            if failed_labels:
                raise Exception(
                    "Failed to create/verify labels: " + 
                    ", ".join(failed_labels) +
                    "\nPlease ensure you are properly authenticated with Gmail " +
                    "and have the necessary permissions."
                )
        except Exception as e:
            if "Gmail API credentials not found" in str(e):
                raise  # Re-raise credential missing error with instructions
            raise Exception(
                f"Error ensuring required labels exist: {str(e)}\n"
                "Please ensure you are properly authenticated with Gmail."
            )

    def is_confirmation_email(self, email_data: Dict[str, Any]) -> bool:
        """Check if the email has waiting-for-response labels."""
        # Get the labels for this email
        labels = email_data.get('labelIds', [])
        
        # Convert label IDs to names using the Gmail API
        try:
            label_objects = self.get_labels()
            label_map = {label['id']: label['name'].lower() for label in label_objects}
            
            # Check if any of the email's labels indicate waiting for response
            email_label_names = [label_map.get(label_id, '').lower() for label_id in labels]
            
            waiting_keywords = [
                'waiting for alan',
                'alan to respond',
                'needs alan response',
                'pending alan',
                'alan action required'
            ]
            
            return any(any(keyword in label_name for keyword in waiting_keywords)
                      for label_name in email_label_names)
        except Exception as e:
            print(f"Error checking labels: {e}")
            return False

    def extract_couple_info(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract couple information from email content."""
        body = email_data['body'].lower()
        subject = email_data['subject'].lower()
        sender_email = email_data['from'].lower()
        
        # Extract sender's actual email from the "From" field (which might be in "Name <email>" format)
        sender_match = re.search(r'<(.+?)>', sender_email)
        if sender_match:
            sender_email = sender_match.group(1)
        
        # Common patterns for names and contact info
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        # Extract potential partner information
        emails = [
            email.lower() for email in re.findall(email_pattern, body)
            if email.lower() != sender_email  # Exclude sender's email
            and not any(domain in email.lower() for domain in [
                '@example.com', '@test.com', '@gmail.com', '@yahoo.com', '@hotmail.com'
            ])  # Exclude common example/test domains
        ]
        
        phones = re.findall(phone_pattern, body)
        
        # If we found any valid emails, use the first one as partner1_email
        if emails:
            couple_info = {
                'partner1_email': emails[0],
                'partner1_name': '[Name Pending]',
                'partner2_name': '[Name Pending]',
                'status': 'Needs Response',
                'notes': f"Email waiting for response:\nFrom: {email_data['from']}\n"
                        f"Subject: {email_data['subject']}\n"
                        f"Received: {email_data['date'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"Email content:\n{email_data['body'][:500]}..."
            }
            
            # If we found a second email, use it as partner2_email
            if len(emails) > 1:
                couple_info['partner2_email'] = emails[1]
            else:
                # If sender's email looks valid, use it as partner2_email
                if (
                    sender_email
                    and '@' in sender_email
                    and not any(domain in sender_email for domain in ['@example.com', '@test.com'])
                ):
                    couple_info['partner2_email'] = sender_email
                else:
                    couple_info['partner2_email'] = '[Email Pending]'
            
            # If we found any phone numbers
            if phones:
                couple_info['partner1_phone'] = phones[0]
                if len(phones) > 1:
                    couple_info['partner2_phone'] = phones[1]
            
            return couple_info
        
        return None

    def scan_and_process_emails(self, days_to_scan: int = 30, user_id: Optional[int] = None) -> List[str]:
        """
        Scan sent emails, process them, and populate the database with extracted information.
        """
        try:
            logger.info("Starting email scan process...")
            # Ensure we're authenticated
            self.ensure_authenticated()
            logger.info("Authentication successful")
            
            # Get database session and models
            from app import db, Couple, ImportedName
            logger.info("Database session initialized")
            
            # Get unprocessed imported names
            imported_names = ImportedName.query.filter_by(is_processed=False).all()
            if not imported_names:
                logger.info("No unprocessed imported names found")
                return ["No names to scan for. Please import names first."]
            
            logger.info(f"Found {len(imported_names)} unprocessed names to scan for")
            results = []
            processed_count = 0
            new_couples = 0
            updated_couples = 0
            
            for imported_name in imported_names:
                try:
                    print(f"\nScanning for couple: {imported_name.partner1_name} and {imported_name.partner2_name}")
                    
                    # Create search query for this couple
                    # Search for exact phrases of each name
                    name_queries = []
                    for name in [imported_name.partner1_name, imported_name.partner2_name]:
                        if name:  # Only add if name is not empty
                            # Add exact phrase match
                            name_queries.append(f'"{name}"')
                            # Add individual word matches as backup
                            name_parts = name.split()
                            if len(name_parts) > 1:  # Only add individual words for multi-word names
                                name_queries.extend(name_parts)
                    
                    # Search for emails containing the names
                    query = f'in:sent newer_than:{days_to_scan}d ({" OR ".join(name_queries)})'
                    print(f"Search query: {query}")
                    
                    emails = self.search_emails(query)
                    if not emails:
                        print(f"No emails found for {imported_name.partner1_name} and {imported_name.partner2_name}")
                        continue
                    
                    print(f"Found {len(emails)} potential emails")
                    
                    for email in emails:
                        try:
                            # Extract email content and metadata
                            email_info = self.extract_email_info(email)
                            if not email_info:
                                continue
                            
                            # Verify this email actually contains the names we're looking for
                            content = email_info['content'].lower()
                            
                            # Check for name variations
                            name_variations = []
                            # Original names
                            if imported_name.partner1_name and imported_name.partner2_name:
                                name_variations.extend([
                                    f"{imported_name.partner1_name.lower()} and {imported_name.partner2_name.lower()}",
                                    f"{imported_name.partner1_name.lower()} & {imported_name.partner2_name.lower()}",
                                    f"{imported_name.partner2_name.lower()} and {imported_name.partner1_name.lower()}",
                                    f"{imported_name.partner2_name.lower()} & {imported_name.partner1_name.lower()}"
                                ])
                            
                            # Individual names
                            if imported_name.partner1_name:
                                name_variations.append(imported_name.partner1_name.lower())
                            if imported_name.partner2_name:
                                name_variations.append(imported_name.partner2_name.lower())
                            
                            # Check if any variation is found in the content
                            name_found = any(variation in content for variation in name_variations)
                            if not name_found:
                                print("Names not found in email content, skipping...")
                                continue
                            
                            print("Found matching email!")
                            print(f"Subject: {email_info['subject']}")
                            
                            # Check if this couple already exists
                            existing_couple = Couple.query.filter(
                                (Couple.partner1_name == imported_name.partner1_name) & 
                                (Couple.partner2_name == imported_name.partner2_name)
                            ).first()
                            
                            if existing_couple:
                                print(f"Found existing couple: {imported_name.partner1_name} and {imported_name.partner2_name}")
                                # Update existing couple with new information
                                updated = self.update_couple_info(existing_couple, email_info, db)
                                if updated:
                                    updated_couples += 1
                                    results.append(f"Updated information for {imported_name.partner1_name} and {imported_name.partner2_name}")
                            else:
                                print("Creating new couple entry...")
                                new_couple = Couple(
                                    celebrant_id=user_id,
                                    partner1_name=imported_name.partner1_name,
                                    partner2_name=imported_name.partner2_name,
                                    partner1_email=email_info.get('to_email', ''),  # Use recipient's email
                                    ceremony_date=imported_name.ceremony_date,  # Use date from import
                                    ceremony_location=imported_name.location,  # Use location from import
                                    ceremony_type=imported_name.role,  # Use role from import
                                    status='Inquiry',
                                    notes=self.format_email_info_as_notes(email_info)
                                )
                                
                                # Add imported information to notes
                                imported_notes = []
                                if imported_name.guest_count:
                                    imported_notes.append(f"Guest Count: {imported_name.guest_count}")
                                if imported_name.ceremony_time:
                                    imported_notes.append(f"Ceremony Time: {imported_name.ceremony_time}")
                                if imported_name.package:
                                    imported_notes.append(f"Package: {imported_name.package}")
                                if imported_name.fee:
                                    imported_notes.append(f"Fee: {imported_name.fee}")
                                if imported_name.travel_fee:
                                    imported_notes.append(f"Travel Fee: {imported_name.travel_fee}")
                                if imported_name.vows:
                                    imported_notes.append(f"Vows: {imported_name.vows}")
                                if imported_name.confirmed:
                                    imported_notes.append(f"Confirmed: {imported_name.confirmed}")
                                if imported_name.notes:
                                    imported_notes.append(f"Additional Notes: {imported_name.notes}")
                                
                                if imported_notes:
                                    new_couple.notes = "Imported Information:\n" + "\n".join(imported_notes) + "\n\n" + new_couple.notes
                                
                                # Update with any additional info from the email
                                if 'dates' in email_info['extracted_data']:
                                    print("Attempting to extract ceremony date...")
                                    ceremony_date = self.extract_date(email_info['extracted_data']['dates'])
                                    if ceremony_date and not new_couple.ceremony_date:
                                        new_couple.ceremony_date = ceremony_date
                                        print(f"Set ceremony date to: {ceremony_date}")
                                
                                if 'venues' in email_info['extracted_data']:
                                    print("Extracting venue information...")
                                    venue_info = ' | '.join(email_info['extracted_data']['venues'])
                                    if venue_info and not new_couple.ceremony_location:
                                        new_couple.ceremony_location = venue_info[:255]
                                        print(f"Set venue to: {new_couple.ceremony_location}")
                                
                                db.session.add(new_couple)
                                new_couples += 1
                                results.append(f"Created new couple entry for {imported_name.partner1_name} and {imported_name.partner2_name}")
                                break  # Stop processing more emails for this couple once we've created an entry
                            
                            processed_count += 1
                            
                        except Exception as e:
                            print(f"Error processing email: {str(e)}")
                            results.append(f"Error processing email for {imported_name.partner1_name} and {imported_name.partner2_name}: {str(e)}")
                            continue
                    
                    # Mark this imported name as processed
                    imported_name.is_processed = True
                    db.session.merge(imported_name)
                    
                except Exception as e:
                    print(f"Error processing couple {imported_name.partner1_name} and {imported_name.partner2_name}: {str(e)}")
                    results.append(f"Error processing couple: {str(e)}")
                    continue
            
            # Commit all changes
            try:
                print("\nCommitting changes to database...")
                db.session.commit()
                print("Successfully committed all changes")
            except Exception as e:
                print(f"Error saving to database: {str(e)}")
                db.session.rollback()
                results.append(f"Error saving to database: {str(e)}")
            
            # Add summary to results
            results.insert(0, f"Processed {processed_count} emails")
            if new_couples > 0:
                results.insert(1, f"Created {new_couples} new couples")
            if updated_couples > 0:
                results.insert(1, f"Updated {updated_couples} existing couples")
            
            print("\nEmail scanning process completed")
            return results
            
        except Exception as e:
            print(f"Error in scan_and_process_emails: {str(e)}")
            return [f"Error scanning emails: {str(e)}"]

    def extract_names(self, email_info: Dict[str, Any]) -> Mapping[str, Optional[str]]:
        """
        Extract partner names from email information.
        """
        names: Dict[str, Optional[str]] = {'partner1': None, 'partner2': None}
        
        # Try to extract names from the 'names' category
        if 'names' in email_info['extracted_data']:
            name_contexts = email_info['extracted_data']['names']
            
            # Look for patterns like "bride: Jane" or "groom John"
            for context in name_contexts:
                # Look for bride/groom/partner name patterns
                patterns = [
                    (r'bride[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', 'partner1'),
                    (r'groom[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', 'partner2'),
                    (r'partner\s*1[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', 'partner1'),
                    (r'partner\s*2[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', 'partner2')
                ]
                
                for pattern, partner_key in patterns:
                    match = re.search(pattern, context, re.IGNORECASE)
                    if match and not names[partner_key]:
                        names[partner_key] = match.group(1).strip()
        
        return names

    def update_couple_info(self, couple: Any, email_info: Dict[str, Any], db: SQLAlchemy) -> bool:
        """
        Update an existing couple with new information from email.
        Returns True if any updates were made.
        """
        updated = False
        
        # Update names if they were '[Name Pending]'
        names = self.extract_names(email_info)
        if couple.partner1_name == '[Name Pending]' and names.get('partner1'):
            couple.partner1_name = names['partner1']
            updated = True
        if couple.partner2_name == '[Name Pending]' and names.get('partner2'):
            couple.partner2_name = names['partner2']
            updated = True
        
        # Update ceremony date if found and not set
        if not couple.ceremony_date and 'dates' in email_info['extracted_data']:
            ceremony_date = self.extract_date(email_info['extracted_data']['dates'])
            if ceremony_date:
                couple.ceremony_date = ceremony_date
                updated = True
                
        # Update ceremony location if found and not set
        if not couple.ceremony_location and 'venues' in email_info['extracted_data']:
            venue_info = ' | '.join(email_info['extracted_data']['venues'])
            if venue_info:
                couple.ceremony_location = venue_info[:255]  # Respect field length limit
                updated = True
                
        # Update ceremony type if found and not set
        if not couple.ceremony_type and 'ceremony_types' in email_info['extracted_data']:
            ceremony_types = email_info['extracted_data']['ceremony_types']
            if ceremony_types:
                couple.ceremony_type = ceremony_types[0][:50]  # Use first found type, respect field length
                updated = True
                
        # Update email addresses if found and not set
        if 'from_email' in email_info and not couple.partner1_email:
            couple.partner1_email = email_info['from_email']
            updated = True
        if 'to_email' in email_info and not couple.partner2_email:
            couple.partner2_email = email_info['to_email']
            updated = True
            
        # Update phone numbers if found in email content
        phone_pattern = r'\b(?:\+?61|0)?(?:4\d{8}|[2378]\d{8})\b'  # Australian phone number pattern
        if not couple.partner1_phone or not couple.partner2_phone:
            phone_matches = re.findall(phone_pattern, email_info['content'])
            if phone_matches:
                if not couple.partner1_phone:
                    couple.partner1_phone = phone_matches[0]
                    updated = True
                elif len(phone_matches) > 1 and not couple.partner2_phone:
                    couple.partner2_phone = phone_matches[1]
                    updated = True
                    
        # Append new email information to notes
        new_notes = self.format_email_info_as_notes(email_info)
        if new_notes:
            if couple.notes:
                couple.notes = couple.notes + "\n\n" + new_notes
            else:
                couple.notes = new_notes
            updated = True
        
        return updated

    def format_email_info_as_notes(self, email_info: Dict[str, Any]) -> str:
        """
        Format extracted email information as readable notes.
        """
        notes = []
        
        # Add email metadata
        notes.append(f"Email from: {email_info['from_email']}")
        notes.append(f"Date: {email_info['date']}")
        notes.append(f"Subject: {email_info['subject']}")
        notes.append("")  # Empty line for spacing
        
        # Add extracted information by category
        for category, contexts in email_info['extracted_data'].items():
            if contexts:
                notes.append(f"{category.replace('_', ' ').title()}:")
                for context in contexts:
                    notes.append(f"- {context}")
                notes.append("")  # Empty line between categories
        
        return '\n'.join(notes)

    def extract_date(self, date_contexts: List[str]) -> Optional[datetime]:
        """
        Extract a date from the date contexts.
        Returns None if no valid date found.
        """
        import re
        from datetime import datetime
        
        # Look for date patterns
        date_patterns = [
            # Format: January 15, 2026
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
            # Format: 15/01/2026 or 15-01-2026
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
            # Format: 2026-01-15
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
        ]
        
        for context in date_contexts:
            for pattern in date_patterns:
                match = re.search(pattern, context)
                if match:
                    try:
                        if len(match.groups()) == 3:
                            if match.group(1) in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:
                                # First pattern: Month Day Year
                                month_names = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                                             'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
                                return datetime(int(match.group(3)), month_names[match.group(1)], int(match.group(2)))
                            else:
                                # Other patterns
                                return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                    except ValueError:
                        continue
        
        return None

    def extract_email_info(self, email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract relevant information from an email."""
        try:
            # Get headers
            headers = {header['name']: header['value'] for header in email['payload']['headers']}
            subject = headers.get('Subject', '')
            
            # Get body
            body = ''
            if 'parts' in email['payload']:
                for part in email['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode()
                        break
            elif 'body' in email['payload'] and 'data' in email['payload']['body']:
                body = base64.urlsafe_b64decode(email['payload']['body']['data']).decode()
            
            # Check for ceremony-related keywords
            ceremony_keywords = [
                'wedding', 'ceremony', 'celebrant', 'marriage',
                'vows', 'officiant', 'celebration', 'union'
            ]
            is_ceremony_related = any(keyword in body.lower() or keyword in subject.lower() 
                                    for keyword in ceremony_keywords)
            
            if not is_ceremony_related:
                return None
            
            # Check for confirmation indicators
            confirmation_keywords = [
                'confirm', 'booking', 'reserved', 'scheduled',
                'appointment', 'date', 'time', 'location'
            ]
            is_confirmation = any(keyword in body.lower() or keyword in subject.lower() 
                                for keyword in confirmation_keywords)
            
            # Check if email needs response
            needs_response = False
            question_indicators = ['?', 'please let me know', 'could you', 'would you', 'can you']
            if any(indicator in body.lower() for indicator in question_indicators):
                needs_response = True
            
            # Get thread context
            thread_context = []
            for msg in email.get('thread_messages', []):
                if msg['id'] != email['id']:  # Skip current message
                    thread_headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    thread_context.append({
                        'subject': thread_headers.get('Subject', ''),
                        'date': msg['internalDate'],
                        'snippet': msg.get('snippet', '')
                    })
            
            # Check for similar templates
            template_matches = []
            for name, template in self.email_templates.items():
                similarity = fuzz.ratio(body, template)
                if similarity > 80:  # 80% similarity threshold
                    template_matches.append(name)
            
            # Extract data from email content
            extracted_data = {}
            
            # Extract dates (simple patterns)
            date_patterns = [
                r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b',
                r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b'
            ]
            dates = []
            for pattern in date_patterns:
                dates.extend(re.findall(pattern, body, re.IGNORECASE))
            if dates:
                extracted_data['dates'] = [' '.join(date) if isinstance(date, tuple) else date for date in dates]
            
            # Extract venues/locations
            venue_keywords = ['venue', 'location', 'church', 'hall', 'reception', 'ceremony at', 'held at']
            venues = []
            for keyword in venue_keywords:
                pattern = rf'{keyword}[:\s]+([A-Za-z\s,]+?)(?:\.|,|\n|$)'
                matches = re.findall(pattern, body, re.IGNORECASE)
                venues.extend([match.strip() for match in matches if len(match.strip()) > 3])
            if venues:
                extracted_data['venues'] = list(set(venues))  # Remove duplicates
            
            return {
                'subject': subject,
                'content': body,
                'from_email': headers.get('From', ''),
                'to_email': headers.get('To', ''),
                'date': headers.get('Date', ''),
                'is_confirmation': is_confirmation,
                'needs_response': needs_response,
                'thread_context': thread_context,
                'template_matches': template_matches,
                'extracted_data': extracted_data
            }
            
        except Exception as e:
            print(f"Error extracting email info: {e}")
            return None

    def find_matching_couples(self, couples: List[Any], text: str, threshold: int = 80) -> List[Any]:
        """Find couples that match the text using fuzzy matching."""
        matching_couples = []
        
        for couple in couples:
            names = [
                couple.partner1_name,
                couple.partner2_name
            ]
            names = [name for name in names if name]  # Remove empty names
            
            if self._fuzzy_name_match(text, names, threshold):
                matching_couples.append(couple)
                
        return matching_couples

    def generate_email_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Generate an email from a template."""
        if template_name not in self.email_templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template = self.email_templates[template_name]
        
        # Replace placeholders
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, str(value))
            
        return template

    def _get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a thread."""
        if thread_id in self.thread_cache:
            return self.thread_cache[thread_id]
            
        try:
            thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
            messages = thread.get('messages', [])
            self.thread_cache[thread_id] = messages
            return messages
        except Exception as e:
            print(f"Error getting thread messages: {e}")
            return []

    def _fuzzy_name_match(self, text: str, names: List[str], threshold: int = 80) -> bool:
        """Check if any name appears in the text using fuzzy matching."""
        # Normalize text
        text = text.lower()
        
        # Generate name variations
        name_variations = []
        for name in names:
            name = name.lower()
            # Full name
            name_variations.append(name)
            # First name only
            if ' ' in name:
                name_variations.append(name.split()[0])
            # Last name only
            if ' ' in name:
                name_variations.append(name.split()[-1])
            # Initials
            if ' ' in name:
                initials = ''.join(word[0] for word in name.split())
                name_variations.append(initials)
        
        # Check each word in the text against name variations
        words = text.split()
        for word in words:
            for variation in name_variations:
                ratio = fuzz.ratio(word, variation)
                if ratio >= threshold:
                    return True
                    
        return False

    def add_label(self, msg_id: str, label_name: str) -> None:
        """Add a label to a specific email."""
        try:
            self.ensure_authenticated()
            
            # Get the email data
            email_data = self.get_email_data(msg_id)
            if not email_data:
                print(f"Could not get email data for message {msg_id}")
                return
                
            # Get the existing labels for the email
            existing_labels = email_data.get('labelIds', [])
            
            # Update the email with the new labels
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': [label_name], 'removeLabelIds': [label for label in existing_labels if label != label_name]}
            ).execute()
        except Exception as e:
            print(f"Error adding label '{label_name}' to email {msg_id}: {str(e)}")

    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates from files."""
        templates = {}
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        
        if os.path.exists(template_dir):
            for filename in os.listdir(template_dir):
                if filename.endswith('.txt'):
                    template_name = os.path.splitext(filename)[0]
                    with open(os.path.join(template_dir, filename)) as f:
                        templates[template_name] = f.read()
                        
        return templates 