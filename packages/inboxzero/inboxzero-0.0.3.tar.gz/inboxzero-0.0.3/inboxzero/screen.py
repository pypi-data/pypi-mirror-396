from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, DataTable, Static, Input, Button, TextArea
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual import events
from textual.message import Message
from rich.text import Text
from datetime import datetime
import asyncio
from typing import List, Optional, Set
import functools # Import functools

from .core import fetch_emails, EmailMessage, AuthError, send_email
from .notifyer import notify
from .db import save_user_credentials, clear_user_credentials


class EmailSent(Message):
    """Message to indicate that an email was sent successfully."""
    pass

class EmailSendFailed(Message):
    """Message to indicate that an email failed to send."""
    def __init__(self, error: Exception):
        self.error = error
        super().__init__()

class EmailModal(ModalScreen):
    """A modal screen to display a single email."""

    BINDINGS = [("escape", "close_modal", "Close")]

    DEFAULT_CSS = """
        EmailModal {
            align: center middle;
        }
    """

    def __init__(self, email: EmailMessage, **kwargs):
        super().__init__(**kwargs)
        self.email = email

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Static(f"[b]From:[/b] {self.email.sender}", id="modal-from")
            yield Static(f"[b]To:[/b] {self.email.recipient}", id="modal-to")
            yield Static(f"[b]Subject:[/b] {self.email.subject}", id="modal-subject")
            yield Static(
                f"[b]Date:[/b] {self.email.date.strftime('%Y-%m-%d %H:%M:%S')}",
                id="modal-date",
            )
            yield TextArea(self.email.body, id="modal-body", read_only=True)
            yield Button("Back", variant="primary", id="back-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-button":
            self.app.pop_screen()

    def action_close_modal(self) -> None:
        self.app.pop_screen()


class ComposeModal(ModalScreen):
    """A modal screen to compose a new email."""

    DEFAULT_CSS = """
    ComposeModal {
        align: center middle;
    }
    #compose-scroll-container {
        width: 80%;
        max-height: 80%;
        align: center middle;
    }
    #compose-container {
        width: 100%;
        height: auto;
        padding: 2;
        background: $panel;
        border: thick $primary;
        layout: vertical;
    }
    #compose-header {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }
    #compose-to, #compose-subject {
        width: 100%;
        margin-bottom: 1;
    }
    #compose-body {
        height: 1fr;
        width: 1fr;
        margin-bottom: 1;
    }
    #compose-buttons {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="compose-scroll-container"):
            with Vertical(id="compose-container"):
                yield Static("✍️ Compose New Email", id="compose-header")
                yield Input(placeholder="To:", id="compose-to")
                yield Input(placeholder="Subject:", id="compose-subject")
                yield TextArea(id="compose-body") # Removed placeholder, as it's not supported
                with Horizontal(id="compose-buttons"):
                    yield Button("Send", variant="primary", id="send-button")
                    yield Button("Cancel", id="cancel-button")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-button":
            to_input = self.query_one("#compose-to", Input)
            subject_input = self.query_one("#compose-subject", Input)
            body_textarea = self.query_one("#compose-body", TextArea)

            to_email = to_input.value.strip()
            subject = subject_input.value.strip()
            body = body_textarea.text.strip()

            # Basic validation
            if not to_email:
                self.app.update_status("❌ Recipient email cannot be empty.")
                return
            if "@" not in to_email or "." not in to_email:
                self.app.update_status("❌ Please enter a valid recipient email address.")
                return
            
            # Subject can be empty, body can be empty.

            self.app.update_status("📧 Sending email...")
            self.app.pop_screen() # Close modal immediately

            # Run the email sending logic in a worker thread
            self.app.run_send_email_worker(to_email, subject, body)

        elif event.button.id == "cancel-button":
            self.app.pop_screen()
            self.app.update_status("Compose cancelled.")


    def send_email_worker(self, to_email: str, subject: str, body: str):
        """A worker to send an email and post the result as a message."""
        try:
            send_email(to_email=to_email, subject=subject, body=body)
            self.app.post_message(EmailSent())
        except Exception as e:
            self.app.post_message(EmailSendFailed(e))

class SendErrorModal(ModalScreen):
    """A modal screen to display an email sending error."""

    def __init__(self, error_message: str, **kwargs):
        super().__init__(**kwargs)
        self.error_message = error_message

    DEFAULT_CSS = """
    SendErrorModal {
        align: center middle;
    }
    #error-container {
        width: 50%;
        height: auto;
        padding: 2;
        background: $error;
        border: thick $error-darken-2;
    }
    #error-title {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }
    #error-message {
        text-align: center;
    }
    #dismiss-button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="error-container"):
            yield Static("❌ Email Send Error", id="error-title")
            yield Static(self.error_message, id="error-message")
            yield Button("Dismiss", variant="primary", id="dismiss-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dismiss-button":
            self.app.pop_screen()


class NetworkErrorModal(ModalScreen):
    """A modal screen to display a network error."""

    def __init__(self, error_message: str, **kwargs):
        super().__init__(**kwargs)
        self.error_message = error_message

    DEFAULT_CSS = """
    NetworkErrorModal {
        align: center middle;
    }
    #error-container {
        width: 50%;
        height: auto;
        padding: 2;
        background: $error;
        border: thick $error-darken-2;
    }
    #error-title {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }
    #error-message {
        text-align: center;
    }
    #retry-button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="error-container"):
            yield Static("🔌 Network Error", id="error-title")
            yield Static(self.error_message, id="error-message")
            yield Button("Retry", variant="error", id="retry-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "retry-button":
            self.app.pop_screen()
            self.app.action_refresh()


class LoginScreen(Screen):
    """A screen for user login."""

    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
    }

    #login-container {
        width: 50%;
        max-height: 80%; /* Ensure scrollability */
        align: center middle;
        padding: 2;
        background: $panel;
        border: thick $primary;
        layout: vertical;
        overflow: auto; /* Make the container itself scrollable */
    }

    #login-title {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }

    #email-input, #password-input {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    #app-password-instructions {
        margin-top: 1;
        margin-bottom: 1;
        padding: 0 1; /* Add some horizontal padding */
        text-align: left; /* Align instructions text to left */
    }

    #login-buttons {
        width: 100%;
        margin-top: 1;
    }
    """
    logo = r"""
    ____      __              _____
   /  _/___  / /_  ____  _  _/__  /  ___  _________
   / // __ \/ __ \/ __ \| |/_/ / /  / _ \/ ___/ __ \
 _/ // / / / /_/ / /_/ />  <  / /__/  __/ /  / /_/ /
/___/_/ /_/_.___/\____/_/|_| /____/\___/_/   \____/
                                                    
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"): # Removed outer ScrollableContainer
            yield Static(self.logo, id="login-title")
            yield Input(placeholder="Email Address", id="email-input")
            yield Static(
                "To log in, please generate a Google App Password:\n"
                "1. Go to your Google Account (myaccount.google.com)\n"
                "2. Navigate to 'Security'\n"
                "3. Under 'How you sign in to Google', select 'App passwords'\n"
                "4. Follow the instructions to generate a new app password\n"
                "5. Use this generated password in the 'App Password' field below.",
                id="app-password-instructions"
            )
            yield Input(placeholder="App Password", password=True, id="password-input")
            with Horizontal(id="login-buttons"):
                yield Button("Login", variant="primary", id="login-button")
                yield Button("Quit", id="quit-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-button":
            email_input = self.query_one("#email-input", Input)
            password_input = self.query_one("#password-input", Input)
            
            email = email_input.value
            app_password = password_input.value

            if email and app_password:
                try:
                    save_user_credentials(email, app_password)
                    self.app.pop_screen()
                    self.app.action_refresh()
                    self.app.update_status("Login successful. Fetching emails...")
                except Exception as e:
                    self.app.update_status(f"Error saving credentials: {str(e)}")
            else:
                self.app.update_status("Please enter both email and app password.")
        elif event.button.id == "quit-button":
            self.app.exit()


class InboxZeroApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        height: 1fr;
        layout: vertical;
    }
    
    #top-ui {
        height: auto;
        padding: 1;
    }
    
    #search-and-compose {
        height: auto;
    }

    #email-list {
       width: 100%;
       height: 1fr;
       border: solid $primary;
   }
    
    #status-bar {
        dock: bottom;
        height: 3;
        background: $boost;
        color: $text;
        padding: 1;
    }

    #modal-container {
        width: 80%;
        height: 80%;
        padding: 1;
        background: $panel-darken-2 80%;
        border: thick $primary;
    }

    #modal-body {
        height: 1fr;
        width: 1fr;
    }
    
    #back-button {
        width: 100%;
    }
    
    #search-input {
        width: 4fr;
    }
    
    #compose-button {
        width: 1fr;
    }
    #logout-button {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("d", "delete_email", "Delete"),
        Binding("a", "archive_email", "Archive"),
        Binding("r", "reply_email", "Reply"),
        Binding("s", "snooze_email", "Snooze"),
        Binding("enter", "open_email", "Open"),
        Binding("m", "mark_read", "Mark Read"),
        Binding("u", "mark_unread", "Mark Unread"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.all_emails: List[EmailMessage] = [] # Master list of all fetched emails
        self.displayed_emails: List[EmailMessage] = [] # Emails currently shown in the table (filtered or all)
        self.current_selection: Optional[int] = None
        self.is_loading = False
        self.notified_uids: Set[int] = set()
        self.fetch_worker = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Vertical(id="top-ui"):
            with Horizontal(id="search-and-compose"):
                yield Input(placeholder="Search emails...", id="search-input")
                yield Button("Compose", variant="primary", id="compose-button")
                yield Button("Logout", variant="error", id="logout-button")

        with Vertical(id="main-container"):
            email_table = DataTable(id="email-list", cursor_type="row")
            email_table.add_columns("📧", "From", "Subject", "Date")
            yield email_table

        yield Static("Initializing...", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load emails when app starts"""
        self.update_status("🔄 Connecting to email server...")
        # Start background email fetching
        self.fetch_worker = self.run_worker(self._email_fetch_loop, exclusive=True)

    def on_unmount(self) -> None:
        """Cancel workers when app closes"""
        if self.fetch_worker:
            self.fetch_worker.cancel()

    async def _email_fetch_loop(self):
        """Background loop to fetch emails periodically."""
        # Initial fetch
        await self._fetch_and_update_emails()

        # Periodic refresh every 60 seconds
        while True:
            await asyncio.sleep(60)
            await self._fetch_and_update_emails()

    async def _fetch_and_update_emails(self):
        """Fetch emails and update UI with notifications for new emails."""
        if self.is_loading:
            return

        self.is_loading = True

        try:
            # Fetch emails in background thread
            self.update_status("🔄 Fetching emails...")
            current_emails = await asyncio.to_thread(fetch_emails, num_emails=50)

            if not current_emails:
                self.update_status("📭 No emails found in inbox")
                self.update_table([])
                return

            # Detect new emails for notifications
            previous_uids = {email.uid for email in self.all_emails} # Use all_emails for previous UIDs
            new_emails = [
                e for e in current_emails if e.uid not in previous_uids and e.unread
            ]

            # Send notifications for new unread emails
            if new_emails and previous_uids:  # Only notify if not initial load
                self._send_notifications(new_emails)

            self.all_emails = current_emails # Update master list
            self.displayed_emails = current_emails # Initially, display all emails

            # Update the table with all current emails
            self.update_table() # Call without argument, it will use self.displayed_emails

            # Update status bar
            unread_count = sum(1 for e in self.all_emails if e.unread) # Use all_emails for count
            self.update_status(
                f"📬 {len(self.all_emails)} emails ({unread_count} unread)" # Use all_emails for count
            )

        except AuthError as e:
            self.update_status(f"🔐 Authentication failed: {str(e)}")
            self.push_screen(LoginScreen())
        except Exception as e:
            error_msg = str(e)[:50]
            self.update_status(f"❌ Error: {error_msg}")
            self.push_screen(NetworkErrorModal(f"Error fetching emails: {error_msg}"))
            self.log.error(f"Email fetch error: {e}")
        finally:
            self.is_loading = False

    def _send_notifications(self, new_emails: List[EmailMessage]):
        """Send desktop notifications for new emails."""
        if not new_emails:
            return

        try:
            if len(new_emails) == 1:
                email = new_emails[0]
                sender = email.sender.split("<")[0].strip()
                notify(
                    f"From: {sender}\nSubject: {email.subject[:60]}",
                    title="📧 New Email",
                    urgency="normal",
                )
            else:
                notify(
                    f"You have {len(new_emails)} new unread emails",
                    title="📧 New Emails",
                    urgency="normal",
                )
        except Exception as e:
            self.log.error(f"Notification error: {e}")

    def update_table(self):
        """Update the email table efficiently."""
        table = self.query_one("#email-list", DataTable)

        # Store current selection
        current_selection_uid = self.current_selection
        current_row_index = -1

        if self.displayed_emails and current_selection_uid is not None:
            for i, email_msg in enumerate(self.displayed_emails):
                if email_msg.uid == current_selection_uid:
                    current_row_index = i
                    break

        # Clear and rebuild table
        table.clear()

        if not self.displayed_emails:
            # Show empty state
            table.add_row("📭", "No emails found", "", "", key="no_emails")
        else:
            for email_msg in self.displayed_emails:
                icon = "🔵" if email_msg.unread else "⚪"
                from_field = email_msg.sender.split("<")[0].strip()[:30]
                subject = (
                    email_msg.subject[:50] + "..."
                    if len(email_msg.subject) > 50
                    else email_msg.subject
                )
                date = email_msg.date.strftime("%Y-%m-%d %H:%M")
                table.add_row(icon, from_field, subject, date, key=str(email_msg.uid))

            # Restore cursor position
            if current_selection_uid is not None:
                new_row_index = -1
                for i, email_msg in enumerate(self.displayed_emails):
                    if email_msg.uid == current_selection_uid:
                        new_row_index = i
                        break

                if new_row_index != -1:
                    table.move_cursor(row=new_row_index)
                else:
                    table.move_cursor(row=0)
            else:
                # Select first email
                table.move_cursor(row=0)

        # Focus table
        if self.displayed_emails and not table.has_focus:
            table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Handle row selection - store selection and show preview."""
        row_key_value = str(event.row_key.value)

        # Skip special rows
        if not row_key_value.isdigit():
            return

        self.current_selection = int(row_key_value)
        selected_email = next(
            (e for e in self.displayed_emails if e.uid == self.current_selection), None
        )

        if selected_email:
            preview = f"From: {selected_email.sender.split('<')[0].strip()} | Subject: {selected_email.subject[:40]}"
            self.update_status(preview)
            # Only push the EmailModal if it's not already mounted, to prevent multiple modals
            if not any(isinstance(screen, EmailModal) for screen in self.app.screen_stack): # Check if any EmailModal is active
                self.push_screen(EmailModal(selected_email))
        else:
            self.update_status("❌ No email selected")

    def action_open_email(self) -> None:
        """Opens the selected email in a modal view (triggered by 'Enter' key)."""
        if self.current_selection is not None:
            selected_email = next(
                (e for e in self.displayed_emails if e.uid == self.current_selection), None
            )
            if selected_email:
                if not any(isinstance(screen, EmailModal) for screen in self.app.screen_stack): # Prevent opening multiple modals
                    self.push_screen(EmailModal(selected_email))
            else:
                self.update_status("❌ No email selected")
        else:
            self.update_status("❌ Please select an email first")

    def action_refresh(self) -> None:
        """Manually refresh emails."""
        self.update_status("🔄 Refreshing...")
        # Trigger immediate fetch
        self.run_worker(self._fetch_and_update_emails, exclusive=False)

    def update_status(self, message: str):
        """Update status bar with timestamp."""
        try:
            status = self.query_one("#status-bar", Static)
            timestamp = datetime.now().strftime("%H:%M:%S")
            status.update(f"[{timestamp}] {message} | ⌨️  Press ? for help")
        except Exception:
            pass  # Widget might not be mounted yet

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "compose-button":
            self.push_screen(ComposeModal())
        elif event.button.id == "logout-button":
            try:
                clear_user_credentials()
                self.app.push_screen(LoginScreen())
                self.update_status("Logged out successfully.")
            except Exception as e:
                self.update_status(f"Error logging out: {str(e)}")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.filter_emails(event.value)

    def run_send_email_worker(self, to_email: str, subject: str, body: str):
        """A worker to send an email and post the result as a message."""
        # This function is now part of the main app
        def worker():
            try:
                send_email(to_email=to_email, subject=subject, body=body)
                self.post_message(EmailSent())
            except Exception as e:
                self.post_message(EmailSendFailed(e))

        self.run_worker(worker, thread=True, name="send_email_worker", group="actions", exclusive=True)

    def on_email_sent(self, message: EmailSent) -> None:
        """Handle successful email sending."""
        self.update_status("✅ Email sent successfully!")

    def on_email_send_failed(self, message: EmailSendFailed) -> None:
        """Handle failed email sending."""
        error = message.error
        if isinstance(error, AuthError):
            self.update_status(f"🔐 Authentication failed: {str(error)}. Please check your login credentials.")
            self.push_screen(LoginScreen())
        else:
            self.update_status(f"❌ Failed to send email: {str(error)}")
            self.push_screen(SendErrorModal(f"Failed to send email: {str(error)}"))

    def filter_emails(self, search_term: str) -> None:
        """Filter the displayed emails based on the search term."""
        if not search_term:
            self.displayed_emails = self.all_emails  # Show all emails if search is empty
        else:
            filtered_emails = []
            for email_msg in self.all_emails: # Filter from the master list
                # Search in sender, subject, and body (case-insensitive)
                if (
                    search_term.lower() in email_msg.sender.lower()
                    or search_term.lower() in email_msg.subject.lower()
                    or search_term.lower() in email_msg.body.lower()
                ):
                    filtered_emails.append(email_msg)
            self.displayed_emails = filtered_emails
        
        self.update_table() # Now calls update_table without arguments

