"""
Email Transaction Scanner - A desktop app for viewing banking transactions from emails
Copyright (C) 2024 alcybersec

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import imaplib
import email
from email.header import decode_header
from email.policy import default
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
import json
import os

# Function to connect to ProtonMail using IMAP (through ProtonMail Bridge)
def connect_to_email(username, password, imap_server, imap_port):
    try:
        mail = imaplib.IMAP4(imap_server, imap_port)  # Non-SSL connection
        mail.login(username, password)
        return mail
    except Exception as e:
        print(f"Error connecting to email server: {e}")
        return None

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

def create_default_settings():
    default_settings = {
        "username": "",
        "password": "",
        "imap_server": "",
        "imap_port": ""
    }
    with open(SETTINGS_PATH, 'w') as file:
        json.dump(default_settings, file, indent=4)

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        create_default_settings()
    with open(SETTINGS_PATH, 'r') as file:
        return json.load(file)

def has_credentials(settings):
    return all(settings.get(key) for key in ["username", "password", "imap_server", "imap_port"])

# Function to get emails containing card transactions
def fetch_emails(mail, folder="INBOX"):
    mail.select(folder)
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails")  # Debug print
        email_list = []
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            if status == 'OK':
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1], policy=default)
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        print(f"Processing email with subject: {subject}")  # Debug print
                        email_list.append(msg)
        return email_list
    return []

# Function to extract transaction details using regex
def extract_transaction_details(email_body):
    # Only process valid transaction emails
    if not all(text in email_body for text in ["Mashreq Bank", "transaction", "purchase of AED"]):
        return None
        
    # More specific regex patterns
    card_ending_regex = r'Card ending with (\d{4})'
    amount_regex = r'purchase of AED ([\d,]+\.\d{2})'
    # Updated vendor regex to be more specific
    vendor_regex = r'at (.*?)\s+(?:Dubai|AE)\s+(?:AE)?\s+on'
    date_regex = r'on (\d{2}-[A-Z]{3}-\d{4} \d{2}:\d{2} [AP]M)'
    available_limit_regex = r'Available limit is AED\s+([\d,]+\.\d{2})'

    amount_match = re.search(amount_regex, email_body)
    vendor_match = re.search(vendor_regex, email_body, re.IGNORECASE)
    date_match = re.search(date_regex, email_body)
    available_limit_match = re.search(available_limit_regex, email_body)
    card_ending_match = re.search(card_ending_regex, email_body)

    # Only return if we have valid transaction details
    if not all([amount_match, vendor_match, date_match]):
        return None

    transaction = {
        "amount": amount_match.group(1) if amount_match else None,
        "vendor": vendor_match.group(1).strip() if vendor_match else None,
        "date": date_match.group(1) if date_match else None,
        "available_limit": available_limit_match.group(1) if available_limit_match else None,
        "card_ending": card_ending_match.group(1) if card_ending_match else None
    }

    # Validate transaction data before returning
    if all(transaction.values()):
        return transaction
    return None

def extract_neo_details(body, msg):
    try:
        # Extract amount
        amount_match = re.search(r'AED\s+([\d,]+\.?\d*)', body)
        amount = float(amount_match.group(1).replace(',', '')) if amount_match else None

        # Extract account number (last 4 digits)
        account_match = re.search(r'a/c no\. \w+(\d{4})', body)
        account = account_match.group(1) if account_match else None

        # Get email date from message object
        date_str = msg['date']
        date = parsedate_to_datetime(date_str).strftime('%d-%b-%Y %I:%M %p')

        if amount and account:
            return {
                'amount': amount,
                'account': account,
                'date': date
            }
    except Exception as e:
        print(f"Error extracting NEO details: {e}")
    return None

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in disposition:
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

# Main function
def main():
    settings = load_settings()
    username = settings.get("username")
    password = settings.get("password")
    imap_server = settings.get("imap_server")
    imap_port = settings.get("imap_port")
    
    mail = connect_to_email(username, password, imap_server, imap_port)
    if not mail:
        return [], []
    
    emails = fetch_emails(mail)
    
    card_transactions = []
    neo_transactions = []

    for msg in emails:
        body = get_email_body(msg)
        if not body:
            continue
            
        if "Transaction notification on your Mashreq NEO Account" in body:
            details = extract_neo_details(body, msg)
            if details and any(details.values()):
                neo_transactions.append(details)
        else:
            details = extract_transaction_details(body)
            if details and any(details.values()):
                card_transactions.append(details)

    return card_transactions, neo_transactions

if __name__ == "__main__":
    card_results, neo_results = main()
    
    if card_results:
        print("\nCard Transactions:")
        sorted_transactions = sorted(card_results, 
                           key=lambda x: datetime.strptime(x['date'], '%d-%b-%Y %I:%M %p'))
        print(sorted_transactions)
    
    if neo_results:
        print("\nNEO Account Funds Addition:")
        sorted_add_funds = sorted(neo_results, 
                          key=lambda x: datetime.strptime(x['date'], '%d-%b-%Y %I:%M %p'))
        print(sorted_add_funds)
    
    if not card_results and not neo_results:
        print("No transaction details found.")
