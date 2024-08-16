import imaplib
from twilio.rest import Client
import email
from email.header import decode_header
from openai import OpenAI
import os
import time
from colorama import init, Fore, Style
import chardet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration from environment variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")

# Twilio credentials from environment variables
account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
twilio_phone_number = os.getenv("twilio_phone_number")
to_phone_number = os.getenv("to_phone_number")

# OpenAI API configuration
client = OpenAI(api_key=os.getenv("openai_api_key"))

def safe_decode(payload):
    if payload is None:
        return ""
    
    # List of encodings to try
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii', 'latin-1', 'cp1252']
    
    # Try chardet first
    detected = chardet.detect(payload)
    if detected['encoding']:
        encodings.insert(0, detected['encoding'])
    
    # Try each encoding
    for encoding in encodings:
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # If all else fails, return a string representation of the bytes
    return str(payload)

def get_emails():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Search for all unread emails
    _, search_data = mail.search(None, '(UNSEEN SENTSINCE 15-Aug-2024)')
    email_ids = search_data[0].split()

    emails = []
    for email_id in email_ids:
        try:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = safe_decode(subject)
            
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        body = safe_decode(payload)
                        break
            else:
                payload = email_message.get_payload(decode=True)
                body = safe_decode(payload)
            
            emails.append({"id": email_id.decode(), "subject": subject, "body": body})
            
        except Exception as e:
            print(f"Error processing email {email_id}: {str(e)}")
            continue

    mail.close()
    mail.logout()

    return emails

def analyze_email(subject, body):
    prompt = f"Analyze the following email:\n\nSubject: {subject}\n\nBody: {body}\n\nIs this email important? Provide a brief summary and classify its importance as 'High', 'Medium', or 'Low'."
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant that analyzes emails and determines their importance based on severity High, Medium or Low."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = ""
    analysis = response.choices[0].message.content
    importance = "Low"
    if "High" in analysis:
        importance = "High"
        summary_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides concise summaries of emails."},
                {"role": "user", "content": f"Summarize this email in one sentence: \n\nSubject: {subject}\n\nBody: {body}"}
            ]
        )
        summary = summary_response.choices[0].message.content
    elif "Medium" in analysis:
        importance = "Medium"
    
    return importance, summary


def print_red(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def make_call_with_summary(summary):
    twilio_client = Client(account_sid, auth_token)

    call = twilio_client.calls.create(
        to=to_phone_number,
        from_=twilio_phone_number,
        twiml=f'<Response><Say voice="alice">{summary}</Say></Response>'
    )

    print(f"Call SID: {call.sid}")
    print(f"Call Status: {call.status}")

def main():
    while True:
        print("\nChecking for new emails...")
        emails = get_emails()
        important_count = 0
        medium_count = 0
        low_count = 0

        for email in emails:
            importance, summary = analyze_email(email["subject"], email["body"])
            
            if importance == "High":
                important_count += 1
                print_red(f"Important email found:\n{summary}\n")
                print("Placing a call.......")
                make_call_with_summary(summary)
            elif importance == "Medium":
                medium_count += 1
            else:
                low_count += 1

        total_emails = len(emails)
        print(f"\nEmail analysis complete:")
        print(f"Total new emails: {total_emails}")
        print(f"High importance: {important_count}")
        print(f"Medium importance: {medium_count}")
        print(f"Low importance: {low_count}")

        print("\nWaiting for 5 minutes before next check...")
        time.sleep(300)  # Wait for 5 minutes (300 seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")