import imaplib
from twilio.rest import Client
import email
from email.header import decode_header
import os
import time
from colorama import init, Fore, Style
import chardet
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize colorama
init()

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

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

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
    _, search_data = mail.search(None, '(UNSEEN SENTSINCE 18-Nov-2024)')
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
            
            emails.append({
                "id": email_id.decode(), 
                "subject": subject, 
                "body": body,
                "from": email_message["From"]
            })
            
        except Exception as e:
            print(f"Error processing email {email_id}: {str(e)}")
            continue

    mail.close()
    mail.logout()

    return emails

def check_email_relevance(subject, body, keywords, similarity_threshold=0.7):
    """
    Check if email content matches any of the keywords using semantic similarity
    """
    email_text = f"{subject}. {body}"
    sentences = [s.strip() for s in email_text.split('.') if s.strip()]
    
    # Encode keywords and sentences
    keyword_embeddings = model.encode(keywords, convert_to_tensor=True)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    
    # Calculate similarities
    similarities = cosine_similarity(
        sentence_embeddings.cpu().numpy(), 
        keyword_embeddings.cpu().numpy()
    )
    
    # Get maximum similarity for each keyword
    max_similarities = np.max(similarities, axis=0)
    matched_keyword_indices = np.where(max_similarities > similarity_threshold)[0]
    
    if len(matched_keyword_indices) > 0:
        matched_keywords = [keywords[idx] for idx in matched_keyword_indices]
        relevant_sentences = []
        for keyword_idx in matched_keyword_indices:
            best_sentence_idx = np.argmax(similarities[:, keyword_idx])
            relevant_sentences.append(sentences[best_sentence_idx])
            
        return True, matched_keywords, relevant_sentences
    
    return False, [], []

def print_green(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def send_sms(message):
    twilio_client = Client(account_sid, auth_token)
    
    message = twilio_client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to_phone_number
    )
    
    print(f"SMS sent! Message SID: {message.sid}")

def main():
    # Define your keywords to match
    keywords = [
        "job opportunity",
        "career opening",
        "interview request",
    ]
    
    print(f"Monitoring emails for keywords: {', '.join(keywords)}")
    
    print("\nChecking for new emails...")
    emails = get_emails()
    matched_count = 0

    for email in emails:
        is_relevant, matched_keywords, relevant_sentences = check_email_relevance(
            email["subject"], 
            email["body"], 
            keywords
        )
        
        if is_relevant:
            matched_count += 1
            summary = (f"Important email from {email['from']}\n"
                       f"Subject: {email['subject']}\n"
                       f"Matched keywords: {', '.join(matched_keywords)}\n"
                       f"Relevant content: {' '.join(relevant_sentences)}")
            
            print_green("Email found...sending SMS")
            print(summary)
            
            # Send SMS
            sms_message = f"Important email: {email['subject']}\nMatched keywords: {', '.join(matched_keywords)}"
            send_sms(sms_message)

    print(f"\nEmail check complete:")
    print(f"Total new emails: {len(emails)}")
    print(f"Matched emails: {matched_count}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
