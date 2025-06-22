import os
import pickle
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Union, Mapping
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
from email.utils import parsedate_to_datetime
import re
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.scoping import scoped_session
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailService:
    def __init__(self):
        self.service = None  # type: Any
        self.creds = None    # type: Optional[Credentials]
        self.flow = None     # type: Optional[InstalledAppFlow]
        self.SCOPES = SCOPES  # Use the same scopes defined at module level

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
        """
        Search for emails using the given query.
        """
        try:
            print(f"Searching emails with query: {query}")
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            print(f"Found {len(messages)} messages matching query")
            
            emails = []
            for message in messages:
                try:
                    email_data = self.get_email_data(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    print(f"Error getting email data for message {message['id']}: {str(e)}")
                    continue
            
            print(f"Successfully retrieved {len(emails)} email details")
            return emails
            
        except Exception as e:
            print(f"Error searching emails: {str(e)}")
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
            # Ensure we're authenticated
            self.ensure_authenticated()
            
            # Search specifically in sent mail
            query = f'in:sent newer_than:{days_to_scan}d'
            emails = self.search_emails(query)
            
            if not emails:
                return ["No sent emails found to process"]
            
            results = []
            processed_count = 0
            new_couples = 0
            updated_couples = 0
            
            # Get database session from current app context
            from app import db, Couple
            
            for email in emails:
                try:
                    # Extract email content and metadata
                    email_info = self.extract_email_info(email)
                    if not email_info:
                        continue
                        
                    # Get the email addresses
                    partner_email = email_info['from_email'] if '@' in email_info['from_email'] else email_info['to_email']
                    
                    # Check if this couple already exists
                    existing_couple = Couple.query.filter(
                        (Couple.partner1_email == partner_email) | 
                        (Couple.partner2_email == partner_email)
                    ).first() if partner_email else None
                    
                    # Extract names from the email content
                    names = self.extract_names(email_info)
                    
                    # Skip if we don't have at least one partner's name
                    if not names.get('partner1') and not names.get('partner2'):
                        results.append(f"Skipped email {partner_email} - no partner names found")
                        continue
                    
                    if existing_couple:
                        # Update existing couple with new information
                        updated = self.update_couple_info(existing_couple, email_info, db)
                        if updated:
                            updated_couples += 1
                            results.append(f"Updated information for couple with email {partner_email}")
                    else:
                        # Create new couple - ensure we have at least one partner name
                        partner1_name = names.get('partner1', 'Partner 1')  # Use placeholder if not found
                        partner2_name = names.get('partner2', 'Partner 2')  # Use placeholder if not found
                        
                        new_couple = Couple(
                            celebrant_id=user_id,
                            partner1_email=partner_email,
                            partner1_name=partner1_name,
                            partner2_name=partner2_name,
                            status='Inquiry',
                            notes=self.format_email_info_as_notes(email_info)
                        )
                        
                        # Set ceremony details if found
                        if 'dates' in email_info['extracted_data']:
                            ceremony_date = self.extract_date(email_info['extracted_data']['dates'])
                            if ceremony_date:
                                new_couple.ceremony_date = ceremony_date
                        
                        if 'venues' in email_info['extracted_data']:
                            venue_info = ' | '.join(email_info['extracted_data']['venues'])
                            new_couple.ceremony_location = venue_info[:255]  # Respect field length
                        
                        db.session.add(new_couple)
                        new_couples += 1
                        results.append(f"Created new couple entry from email {partner_email}")
                    
                    processed_count += 1
                    
                except Exception as e:
                    results.append(f"Error processing email: {str(e)}")
                    continue
            
            # Commit all changes
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                results.append(f"Error saving to database: {str(e)}")
            
            # Add summary to results
            results.insert(0, f"Processed {processed_count} sent emails")
            if new_couples > 0:
                results.insert(1, f"Created {new_couples} new couples")
            if updated_couples > 0:
                results.insert(1, f"Updated {updated_couples} existing couples")
            
            return results
            
        except Exception as e:
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
        
        # Update venue if found and not set
        if not couple.ceremony_location and 'venues' in email_info['extracted_data']:
            venue_info = ' | '.join(email_info['extracted_data']['venues'])
            couple.ceremony_location = venue_info[:255]  # Respect field length
            updated = True
        
        # Append new notes if they don't exist
        new_notes = self.format_email_info_as_notes(email_info)
        if new_notes and new_notes not in (couple.notes or ''):
            couple.notes = ((couple.notes or '') + '\n\n' + new_notes).strip()
            updated = True
        
        if updated:
            db.session.merge(couple)
        
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
        """
        Extract relevant information from an email.
        """
        try:
            # Get email metadata
            headers = {h['name']: h['value'] for h in email.get('payload', {}).get('headers', [])}
            subject = headers.get('Subject', '')
            from_email = self.extract_email_address(headers.get('From', ''))
            to_email = self.extract_email_address(headers.get('To', ''))
            date_str = headers.get('Date', '')
            content = self.get_email_content(email)
            
            # Initialize extracted info
            info = {
                'subject': subject,
                'from_email': from_email,
                'to_email': to_email,
                'date': date_str,
                'extracted_data': {}
            }
            
            # Keywords to look for and their categories
            keywords = {
                'names': [
                    'bride', 'groom', 'partner', 'fiancé', 'fiancee', 'couple',
                    'mr', 'mrs', 'ms', 'miss', 'dr', 'professor'
                ],
                'dates': [
                    'wedding date', 'ceremony date', 'wedding day', 
                    'getting married', 'tying the knot', 'big day',
                    'january', 'february', 'march', 'april', 'may', 'june',
                    'july', 'august', 'september', 'october', 'november', 'december',
                    '2024', '2025', '2026'
                ],
                'venues': [
                    'venue', 'location', 'ceremony venue', 'reception venue',
                    'garden', 'beach', 'hotel', 'restaurant', 'winery', 'estate',
                    'farm', 'barn', 'chapel', 'church', 'cathedral', 'temple',
                    'outdoor', 'indoor', 'backyard'
                ],
                'timing': [
                    'morning', 'afternoon', 'evening', 'sunset', 'sunrise',
                    'time', 'o\'clock', 'am', 'pm'
                ],
                'guest_count': [
                    'guests', 'people', 'attendees', 'capacity', 'numbers',
                    'intimate', 'small', 'large', 'big'
                ],
                'style': [
                    'traditional', 'modern', 'rustic', 'elegant', 'casual',
                    'formal', 'bohemian', 'vintage', 'classic', 'romantic',
                    'simple', 'elaborate', 'cultural', 'religious'
                ],
                'contact_info': [
                    'phone', 'mobile', 'cell', 'tel', 'email', 'contact',
                    'reach', 'call', 'text', 'message', '@'
                ],
                'budget': [
                    'budget', 'cost', 'price', 'fee', 'deposit', 'payment',
                    'expensive', 'affordable', 'package', 'rate'
                ],
                'planning_stage': [
                    'planning', 'early stages', 'beginning', 'started',
                    'thinking about', 'considering', 'decided', 'booked',
                    'confirmed', 'reserved', 'inquiry', 'enquiry'
                ]
            }
            
            # Extract information for each category
            for category, keyword_list in keywords.items():
                matches = []
                for keyword in keyword_list:
                    # Look for keyword matches in content
                    pattern = rf'\b{keyword}\b'
                    matches.extend(self.find_context(content, pattern))
                
                if matches:
                    info['extracted_data'][category] = matches
            
            # Only return if we found any relevant information
            return info if info['extracted_data'] else None
            
        except Exception as e:
            print(f"Error extracting email info: {str(e)}")
            return None

    def find_context(self, text: str, pattern: str, context_chars: int = 50) -> List[str]:
        """
        Find matches for a pattern and return the surrounding context.
        """
        import re
        matches = []
        for match in re.finditer(pattern, text.lower()):
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            context = text[start:end].strip()
            matches.append(context)
        return matches

    def extract_email_address(self, header_value: str) -> str:
        """
        Extract email address from a header value.
        Handles formats like: "Name <email@example.com>" or just "email@example.com"
        """
        import re
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        match = re.search(email_pattern, header_value)
        return match.group(0) if match else header_value

    def get_email_content(self, email: Dict[str, Any]) -> str:
        """
        Get the text content of an email, handling different MIME types and encodings.
        """
        try:
            if 'payload' not in email:
                return ''
                
            payload = email['payload']
            
            # Handle multipart messages
            if 'parts' in payload:
                text_content = []
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            import base64
                            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                            text_content.append(decoded)
                return '\n'.join(text_content)
            
            # Handle single part messages
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    import base64
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return ''
            
        except Exception as e:
            print(f"Error getting email content: {str(e)}")
            return ''

    def needs_followup(self, email: Dict[str, Any]) -> bool:
        """
        Determine if a sent email needs follow-up.
        Returns True if:
        - The email was sent more than 7 days ago
        - No reply has been received
        - Contains wedding-related keywords
        """
        try:
            # Get email metadata
            headers = {h['name']: h['value'] for h in email.get('payload', {}).get('headers', [])}
            date_str = headers.get('Date')
            
            if not date_str:
                return False
                
            # Parse the email date
            email_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            days_since_sent = (datetime.now(timezone.utc) - email_date).days
            
            # Check if it's been more than 7 days
            if days_since_sent >= 7:
                # Search for any replies to this email
                thread_id = email.get('threadId')
                if thread_id:
                    replies = self.search_emails(f'in:inbox threadId:{thread_id}')
                    if not replies:  # No replies found
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking for follow-up need: {str(e)}")
            return False

    def is_wedding_related(self, email: Dict[str, Any]) -> bool:
        """
        Check if an email is wedding-related based on its content.
        """
        # Get email subject and snippet
        subject = email.get('subject', '').lower()
        snippet = email.get('snippet', '').lower()
        
        # Keywords that indicate wedding-related content
        wedding_keywords = [
            'wedding', 'ceremony', 'celebrant',
            'marriage', 'officiant', 'bride', 'groom',
            'venue', 'reception', 'engagement'
        ]
        
        # Check subject and snippet for keywords
        for keyword in wedding_keywords:
            if keyword in subject or keyword in snippet:
                return True
        
        return False
        
    def needs_response(self, email: Dict[str, Any]) -> bool:
        """
        Determine if an email needs a response.
        """
        # Get email metadata
        headers = {h['name']: h['value'] for h in email.get('payload', {}).get('headers', [])}
        to_header = headers.get('To', '').lower()
        from_header = headers.get('From', '').lower()
        
        # If the email was sent to us and hasn't been replied to
        if 'in-reply-to' not in headers and '@' in to_header:
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