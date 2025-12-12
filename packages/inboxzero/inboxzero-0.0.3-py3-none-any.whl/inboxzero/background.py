import time
import threading
from typing import List, Callable
from datetime import datetime

from .core import fetch_emails, EmailMessage
from .notifyer import notify

class EmailFetcher:
    def __init__(self, on_new_emails: Callable[[List[EmailMessage]], None], refresh_interval: int = 60):
        self.on_new_emails = on_new_emails
        self.refresh_interval = refresh_interval
        self._latest_emails: List[EmailMessage] = []
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run_fetch_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def _run_fetch_loop(self):
        # Initial fetch on startup
        self._fetch_and_compare()
        while self._running:
            time.sleep(self.refresh_interval)
            self._fetch_and_compare()

    def _fetch_and_compare(self):
        try:
            current_emails = fetch_emails()
            # Determine newly added emails for notification purposes
            new_arrivals_for_notification = self._compare_emails_for_new_arrivals(current_emails)
            
            # Always pass the full list of current emails to the UI update callback
            # Use self.on_new_emails directly, as it will be wrapped by call_from_thread
            self.on_new_emails(current_emails)
            
            if new_arrivals_for_notification:
                self._send_notification(new_arrivals_for_notification)
            
            self._latest_emails = current_emails
        except Exception as e:
            # Important: When troubleshooting, ensure this print is visible for debugging
            print(f"Error fetching emails in background: {e}")

    def _compare_emails_for_new_arrivals(self, current_emails: List[EmailMessage]) -> List[EmailMessage]:
        """Compares current emails with previously known emails to find new arrivals."""
        if not self._latest_emails:
            # On initial load, consider all fetched emails as "new" for notification purposes
            # (though the UI will just display them all)
            return current_emails

        newly_arrived = []
        # Use UIDs for efficient comparison
        latest_uids = {email.uid for email in self._latest_emails}

        for email_msg in current_emails:
            if email_msg.uid not in latest_uids:
                newly_arrived.append(email_msg)
        
        # Sort by date to ensure chronological order for notifications/display
        newly_arrived.sort(key=lambda x: x.date, reverse=True)
        return newly_arrived

    def _send_notification(self, new_emails: List[EmailMessage]):
        if not new_emails:
            return

        if len(new_emails) == 1:
            email_ = new_emails[0]
            notify(
                f"From: {email_.sender}\nSubject: {email_.subject}",
                title="New Email Received",
            )
        else:
            notify(
                f"You have {len(new_emails)} new emails.",
                title="New Emails Received",
            )
