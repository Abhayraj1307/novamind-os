import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# You will need to add these to your .env file later
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_unread_emails(limit: int = 5):
    """Connects to email and fetches top N unread subjects."""
    try:
        if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
            return ["Email config missing (EMAIL_USER/EMAIL_PASSWORD)."]

        # Connect
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        mail.select("inbox")

        # Search Unread
        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()[-limit:] # Get last N

        results = []
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    results.append(f"From: {sender} | Subject: {subject}")
        
        mail.close()
        mail.logout()
        return results
    except Exception as e:
        return [f"Error accessing email: {str(e)}"]

def send_email(to_email: str, subject: str, body: str):
    """Sends an email via SMTP."""
    try:
        if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
            return "Email config missing (EMAIL_USER/EMAIL_PASSWORD)."

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.EMAIL_USER, to_email, text)
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"
