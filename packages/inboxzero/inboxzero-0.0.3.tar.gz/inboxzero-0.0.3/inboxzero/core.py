import imaplib
import smtplib
import email
from email.header import decode_header
from email.message import EmailMessage as StdlibEmailMessage
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
import socket
import re

from .db import get_user_credentials, save_user_credentials, init_db


class AuthError(Exception):
    """Custom exception for authentication failures."""

    pass


@dataclass
class EmailMessage:
    id: int
    uid: int
    sender: str
    recipient: str
    subject: str
    date: datetime
    body: str
    unread: bool


def _decode_header_value(value: Optional[str]) -> str:
    """Safely decode email header values."""
    if value is None:
        return ""
    try:
        decoded_parts = decode_header(value)
        result = []
        for decoded, enc in decoded_parts:
            if isinstance(decoded, bytes):
                result.append(decoded.decode(enc or "utf-8", errors="ignore"))
            else:
                result.append(str(decoded))
        return " ".join(result)
    except Exception:
        return str(value)


def _get_email_body(msg: StdlibEmailMessage) -> str:
    """Extract plain text body from email message."""
    body = ""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                            break
                    except Exception:
                        continue
        else:
            if msg.get_content_type() == "text/plain":
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
    except Exception as e:
        body = f"[Error reading email body: {str(e)}]"

    return body.strip()


def fetch_emails(num_emails: int = 50, timeout: int = 15) -> List[EmailMessage]:
    """
    Fetch emails from Gmail IMAP server with improved error handling.

    Args:
        num_emails: Number of recent emails to fetch (default: 50)
        timeout: Connection timeout in seconds (default: 15)

    Returns:
        List of EmailMessage objects sorted by date (newest first)

    Raises:
        AuthError: If authentication fails
        Exception: For other errors with descriptive messages
    """
    credentials = get_user_credentials()
    if not credentials:
        raise AuthError("No user credentials found. Please log in.")
    
    EMAIL, APP_PASSWORD = credentials

    emails: List[EmailMessage] = []
    imap = None

    try:
        # Create IMAP connection with timeout
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap.sock.settimeout(timeout)

        # Login with better error handling
        try:
            imap.login(EMAIL, APP_PASSWORD)
        except imaplib.IMAP4.error as e:
            error_str = str(e).upper()
            if (
                "AUTHENTICATIONFAILED" in error_str
                or "INVALID CREDENTIALS" in error_str
            ):
                raise AuthError(
                    "Invalid email or app password. "
                )
            else:
                raise AuthError(f"Login failed: {str(e)}")

        # Select inbox
        status, response = imap.select("INBOX")
        if status != "OK":
            raise Exception(f"Failed to select INBOX: {response}")

        # Search for all emails
        status, messages = imap.search(None, "ALL")
        if status != "OK":
            raise Exception(f"Failed to search emails: {messages}")

        email_ids = messages[0].split()
        if not email_ids:
            return []  # Empty inbox

        # Get most recent email IDs
        total_emails = len(email_ids)
        start_index = max(0, total_emails - num_emails)
        recent_email_ids = email_ids[start_index:]

        # Fetch emails in batches for better performance
        batch_size = 10
        for i in range(0, len(recent_email_ids), batch_size):
            batch = recent_email_ids[i : i + batch_size]
            batch_emails = _fetch_email_batch(imap, batch)
            emails.extend(batch_emails)

        # Sort by date (newest first)
        emails.sort(key=lambda x: x.date, reverse=True)

        return emails

    except AuthError:
        raise
    except imaplib.IMAP4.error as e:
        raise Exception(f"IMAP protocol error: {str(e)}")
    except socket.timeout:
        raise Exception("Connection timeout - check your internet connection")
    except socket.gaierror:
        raise Exception("Network error - cannot reach Gmail servers")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")
    finally:
        # Ensure connection is closed
        if imap:
            try:
                imap.close()
                imap.logout()
            except Exception:
                pass  # Ignore errors during cleanup


def _fetch_email_batch(
    imap: imaplib.IMAP4_SSL, email_ids: List[bytes]
) -> List[EmailMessage]:
    """
    Fetch a batch of emails efficiently.

    Args:
        imap: Active IMAP connection
        email_ids: List of email IDs to fetch

    Returns:
        List of EmailMessage objects
    """
    emails = []

    # Convert bytes to strings for the fetch command
    id_list = b",".join(email_ids).decode()

    try:
        # Fetch email data with FLAGS for read/unread status
        status, msg_data = imap.fetch(id_list, "(RFC822 FLAGS)")
        if status != "OK":
            return emails

        # Process each email in the response
        i = 0
        while i < len(msg_data):
            item = msg_data[i]

            # Skip non-tuple items (they're just closing parentheses)
            if not isinstance(item, tuple):
                i += 1
                continue

            try:
                # Extract email data
                flags_info = item[0]
                raw_email = item[1]

                # Parse the email
                msg = email.message_from_bytes(raw_email)

                # Extract email ID from the response
                email_id_match = re.search(rb"(\d+)\s+\(", flags_info)
                if email_id_match:
                    email_id = int(email_id_match.group(1))
                else:
                    i += 1
                    continue

                # Check if unread (\\Seen flag not present)
                flags_str = flags_info.decode("utf-8", errors="ignore")
                is_unread = "\\Seen" not in flags_str

                # Parse date safely
                date_str = msg.get("Date", "")
                try:
                    email_date = parsedate_to_datetime(date_str)
                except Exception:
                    email_date = datetime.now()  # Fallback to current time

                # Create EmailMessage object
                emails.append(
                    EmailMessage(
                        id=email_id,
                        uid=email_id,
                        sender=_decode_header_value(msg.get("From", "Unknown")),
                        recipient=_decode_header_value(msg.get("To", "")),
                        subject=_decode_header_value(
                            msg.get("Subject", "(No Subject)")
                        ),
                        date=email_date,
                        body=_get_email_body(msg),
                        unread=is_unread,
                    )
                )
            except Exception as e:
                # Log error but continue processing other emails
                print(f"Error processing email: {e}")

            i += 1

    except Exception as e:
        print(f"Error fetching email batch: {e}")

    return emails


# Test function for debugging
if __name__ == "__main__":
    try:
        print("Testing email fetch...")
        emails = fetch_emails(num_emails=10)
        print(f"Successfully fetched {len(emails)} emails")

        if emails:
            print("\nFirst email:")
            email = emails[0]
            print(f"  From: {email.sender}")
            print(f"  Subject: {email.subject}")
            print(f"  Date: {email.date}")
            print(f"  Unread: {email.unread}")
    except Exception as e:
        print(f"Error: {e}")


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Sends an email using the user's configured SMTP credentials.

    Args:
        to_email: The recipient's email address.
        subject: The subject of the email.
        body: The plain text body of the email.

    Raises:
        AuthError: If authentication fails.
        Exception: For other errors during email sending.
    """
    credentials = get_user_credentials()
    if not credentials:
        raise AuthError("No user credentials found. Please log in to send emails.")

    from_email, app_password = credentials

    try:
        # Create the email message
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        # Connect to SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        raise AuthError(
            f"SMTP authentication failed. Check your email and app password. Original error: {e}"
        )
    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error occurred: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while sending email: {e}")
