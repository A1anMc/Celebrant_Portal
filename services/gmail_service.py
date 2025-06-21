import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
from email.utils import parsedate_to_datetime
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        self.service = None  # type: Any
        self.creds = None    # type: Optional[Credentials]

    def authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth 2.0."""
        if not os.path.exists('credentials.json'):
            raise FileNotFoundError(
                "credentials.json not found. Please download it from Google Cloud Console "
                "and place it in the application root directory."
            )

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    raise Exception(f"Failed to refresh credentials: {str(e)}")
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise Exception(
                        f"Failed to authenticate with Google: {str(e)}. "
                        "Make sure you have valid credentials.json and "
                        "proper permissions."
                    )

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {str(e)}")

    def search_emails(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for emails matching the query and return their details."""
        if not self.service:
            self.authenticate()

        results = self.service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            email_data = self.get_email_data(message['id'])
            if email_data:
                emails.append(email_data)

        return emails

    def get_email_data(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific email."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=msg_id, format='full').execute()
            
            headers = message['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'].lower() == 'subject')
            from_email = next(h['value'] for h in headers if h['name'].lower() == 'from')
            date_str = next(h['value'] for h in headers if h['name'].lower() == 'date')
            date = parsedate_to_datetime(date_str)

            # Get email body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = self.get_body_from_parts(parts)
            else:
                data = message['payload']['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode() if data else ''

            return {
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body
            }
        except Exception as e:
            print(f"Error processing email {msg_id}: {str(e)}")
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

    def extract_couple_info(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract couple information from email content."""
        body = email_data['body'].lower()
        
        # Common patterns for names and contact info
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        # Extract potential partner information
        emails = re.findall(email_pattern, body)
        phones = re.findall(phone_pattern, body)
        
        # Look for date patterns
        date_patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',     # DD/MM/YYYY or MM/DD/YYYY
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',     # YYYY/MM/DD
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b',  # Month DD, YYYY
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december) \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b'  # Full month name
        ]
        
        potential_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                try:
                    # Try different date formats
                    date_formats = [
                        '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',  # Numeric formats
                        '%B %d, %Y', '%B %dst, %Y', '%B %dnd, %Y', '%B %drd, %Y', '%B %dth, %Y',  # Full month name
                        '%b %d, %Y', '%b %dst, %Y', '%b %dnd, %Y', '%b %drd, %Y', '%b %dth, %Y'   # Abbreviated month
                    ]
                    
                    # Clean up the date string
                    date_str = match.replace('-', '/').lower()
                    date_str = re.sub(r'(?:st|nd|rd|th),?\s*', ' ', date_str)
                    
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_date:
                        # Only add future dates or dates within past 6 months
                        six_months_ago = datetime.now() - timedelta(days=180)
                        five_years_future = datetime.now() + timedelta(days=365*5)
                        
                        if six_months_ago <= parsed_date <= five_years_future:
                            potential_dates.append(parsed_date.strftime('%Y-%m-%d'))
                
                except Exception as e:
                    print(f"Error parsing date '{match}': {str(e)}")
                    continue

        # Extract location information with improved patterns
        location_patterns = [
            r'location:\s*(.*?)(?:\n|$)',
            r'venue:\s*(.*?)(?:\n|$)',
            r'ceremony (?:at|in)\s+(.*?)(?:on|for|\.|\n|$)',
            r'wedding (?:at|in)\s+(.*?)(?:on|for|\.|\n|$)',
            r'(?:the )?(?:ceremony|wedding|celebration) will be (?:at|in)\s+(.*?)(?:on|for|\.|\n|$)'
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            locations.extend(match.strip() for match in matches if match.strip())

        # Remove duplicates while preserving order
        emails = list(dict.fromkeys(emails))
        phones = list(dict.fromkeys(phones))
        potential_dates = list(dict.fromkeys(potential_dates))
        locations = list(dict.fromkeys(locations))

        if not (emails or phones or potential_dates or locations):
            return None

        return {
            'subject': email_data['subject'],
            'from_email': email_data['from'],
            'date_received': email_data['date'],
            'potential_emails': emails,
            'potential_phones': phones,
            'potential_dates': potential_dates,
            'potential_locations': locations,
            'raw_body': body
        }

    def scan_for_couples(self, days: int = 30) -> List[Dict[str, Any]]:
        """Scan emails from the last X days for potential couple information."""
        query = f'newer_than:{days}d'
        emails = self.search_emails(query)
        
        couples_data = []
        for email_data in emails:
            couple_info = self.extract_couple_info(email_data)
            if couple_info:
                couples_data.append(couple_info)
        
        return couples_data 