# Building an Intelligent Email Analyzer with Twilio Voice Alerts and OpenAI GPT-4

## Introduction

In today's fast-paced digital world, managing your inbox can be overwhelming. What if you could have an AI assistant that reads your emails, determines their importance, and calls you about the most critical ones? In this tutorial, you'll learn how to build a Python application that does just that, using Twilio Programmable Voice and OpenAI's GPT-4.

This intelligent email analyzer will:
1. Retrieve unread emails from your inbox
2. Use GPT-4 to analyze and classify each email's importance
3. Make a voice call to alert you about highly important emails

By the end of this tutorial, you'll have a powerful tool to help you stay on top of your most crucial communications without being tied to your inbox.

[Image suggestion: A diagram showing the flow of the application - Email Inbox → Python Script → OpenAI Analysis → Twilio Voice Call]

## Prerequisites

Before we dive in, make sure you have the following:

- A free Twilio account. If you don't have one, [sign up here](https://www.twilio.com/try-twilio).
- A paid OpenAI account with access to the GPT-4 API. [Sign up here](https://platform.openai.com/).
- Python 3.7 or later installed on your computer. [Download Python](https://www.python.org/downloads/).
- Basic knowledge of Python programming.
- An email account that supports IMAP access. Most major email providers (Gmail, Outlook, Yahoo) support this.

## Setting Up Your Development Environment

### Creating a Virtual Environment

Let's start by setting up a clean development environment. Open your terminal and run the following commands:

```bash
mkdir email-analyzer
cd email-analyzer
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

This creates a new directory for your project and sets up a virtual environment to manage your dependencies.

### Installing Required Packages

Now, let's install the necessary Python packages:

```bash
pip install twilio openai python-dotenv colorama chardet
```

Here's what each package does:
- `twilio`: Twilio's Python SDK for making voice calls
- `openai`: OpenAI's Python client for accessing GPT-4
- `python-dotenv`: For loading environment variables from a .env file
- `colorama`: For adding color to console output
- `chardet`: For detecting character encoding in emails

## Configuring Your Environment Variables

To keep your sensitive information secure, you'll use environment variables. Create a file named `.env` in your project directory with the following content:

```text
EMAIL=your_email@example.com
PASSWORD=your_email_password
IMAP_SERVER=your_imap_server
account_sid=your_twilio_account_sid
auth_token=your_twilio_auth_token
twilio_phone_number=your_twilio_phone_number
to_phone_number=your_personal_phone_number
openai_api_key=your_openai_api_key
```

Replace the placeholder values with your actual credentials. Here's how to get each:

1. `EMAIL` and `PASSWORD`: Your email address and password.
2. `IMAP_SERVER`: The IMAP server for your email provider (e.g., `imap.gmail.com` for Gmail).
3. `account_sid` and `auth_token`: Find these in your [Twilio Console](https://www.twilio.com/console).
4. `twilio_phone_number`: A Twilio phone number you've purchased.
5. `to_phone_number`: Your personal phone number where you want to receive calls.
6. `openai_api_key`: Your OpenAI API key from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

[Image suggestion: A screenshot of the Twilio Console showing where to find the account SID and auth token]

!!!warning
Never commit your `.env` file to version control. Add it to your `.gitignore` file to prevent accidental exposure of your credentials.
!!!

## Building the Email Analyzer

Now, let's break down the main components of our email analyzer.

### Retrieving Unread Emails

First, we'll implement the function to retrieve unread emails:

```python
import imaplib
import email
from email.header import decode_header
import chardet
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")

def safe_decode(payload):
    # ... (implementation as provided in the original code)

def get_emails():
    # ... (implementation as provided in the original code)
```

The `get_emails()` function does the following:
1. Connects to the IMAP server using SSL.
2. Logs in with your email credentials.
3. Searches for unread emails sent since August 15, 2024 (you may want to adjust this date).
4. Retrieves the subject and body of each email.
5. Safely decodes the email content, handling various character encodings.

[Image suggestion: A flowchart showing the steps of the `get_emails()` function]

### Analyzing Emails with OpenAI's GPT-4

Next, we'll implement the email analysis using OpenAI's GPT-4:

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("openai_api_key"))

def analyze_email(subject, body):
    # ... (implementation as provided in the original code)
```

The `analyze_email()` function:
1. Constructs a prompt for GPT-4, including the email subject and body.
2. Sends the prompt to the GPT-4 model.
3. Interprets the model's response to classify the email's importance as "High", "Medium", or "Low".
4. For high-importance emails, it generates a concise summary.

[Image suggestion: An example of the GPT-4 prompt and response for email analysis]

### Implementing Twilio Voice Calls

Now, let's set up the function to make voice calls using Twilio Programmable Voice:

```python
from twilio.rest import Client

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
twilio_phone_number = os.getenv("twilio_phone_number")
to_phone_number = os.getenv("to_phone_number")

def make_call_with_summary(summary):
    # ... (implementation as provided in the original code)
```

The `make_call_with_summary()` function:
1. Initializes a Twilio client with your account credentials.
2. Creates a new call using Twilio's `calls.create()` method.
3. Uses TwiML (Twilio Markup Language) to define the call's behavior, in this case, reading out the email summary.

[Image suggestion: A screenshot of the Twilio Console showing a completed call log]

### The Main Application Loop

Finally, let's implement the main loop that ties everything together:

```python
import time
from colorama import init, Fore, Style

def print_red(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def main():
    # ... (implementation as provided in the original code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
```

The `main()` function:
1. Continuously checks for new emails every 5 minutes.
2. Analyzes each new email using GPT-4.
3. Prints a summary of email importance to the console.
4. For high-importance emails, it makes a Twilio voice call with the email summary.

## Running and Testing the Application

To run your email analyzer, make sure all your credentials are correctly set in the `.env` file, then execute:

```bash
python email_analyzer.py
```

The script will start running and check for new emails every 5 minutes. To test it:

1. Send yourself an email with varying levels of importance.
2. Wait for the script to detect and analyze the new email.
3. If the email is classified as "High" importance, you should receive a phone call with a summary of the email.

[Image suggestion: A screenshot of the console output showing email analysis results]

!!!info
The script uses the date "August 15, 2024" as a filter for emails. Make sure to adjust this date in the `get_emails()` function to match your testing needs.
!!!

## Potential Enhancements and Use Cases

This email analyzer can be extended in various ways:

1. **SMS Notifications**: Use Twilio Programmable SMS to send text messages for medium-importance emails.
2. **Web Interface**: Create a web dashboard to view and manage analyzed emails.
3. **Custom Voice**: Use Twilio's advanced TTS voices for more natural-sounding calls.
4. **Scheduled Runs**: Instead of running continuously, schedule the script to run at specific times.
5. **Email Actions**: Implement functionality to reply to or forward important emails automatically.
