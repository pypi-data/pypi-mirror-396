# InboxZero: Email Management and Notification Tool

A command-line tool designed to help you manage your email inbox efficiently, providing notifications and quick actions directly from your terminal.

## Features
- **Email Notifications**: Get instant alerts for new emails.
- **Inbox Summary**: Quickly view a summary of your unread or important emails.
- **Customizable Actions**: Define your own actions for emails (e.g., mark as read, archive, reply templates).
- **Google Account Integration**: Securely connect with your Google Mail account using App Passwords.

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package installer)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MadushankaRajapaksha/inbox-zero.git
    cd inboxzero
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
     
    pip install -e .
    ```

## Configuration: Google Account Setup with App Passwords

To use InboxZero with your Google account, you need to set up an "App Password". This is a 16-digit passcode that grants non-Google applications or devices permission to access your Google Account without requiring your main password. **App Passwords can only be used with accounts that have 2-Step Verification turned on.**

### Steps to Generate a Google App Password

1.  **Enable 2-Step Verification (if not already enabled):**
    If 2-Step Verification is not already active for your Google Account, you must enable it first.
    - Go to your Google Account: [`myaccount.google.com`](https://myaccount.google.com/)
    - In the left navigation panel, select **Security**.
    - Under the "How you sign in to Google" section, find and select **2-Step Verification**.
    - Click **Get started** and follow the on-screen prompts to set up 2-Step Verification.

2.  **Generate the App Password:**
    Once 2-Step Verification is active:
    - Return to your Google Account: [`myaccount.google.com`](https://myaccount.google.com/)
    - In the left navigation panel, select **Security**.
    - Under "How you sign in to Google," select **App passwords**. You may be prompted to sign in again for security.
    - At the bottom of the "App passwords" page, use the dropdowns to:
        - Choose **Select app**: Select "Mail" or "Other" and type "InboxZero".
        - Choose **Select device**: Select "Windows Computer" or "Other" and type "InboxZero".
    - Click the **Generate** button.
    - A 16-character code will be displayed in a yellow bar. This is your App password. **It is crucial to copy this password immediately as it will only be displayed once.**
 

## Usage

After installation and configuration, you can use InboxZero from your terminal:

```bash
 

# Check for new emails and trigger notifications
inboxzero  
 
 
```

## Contributing
We welcome contributions! Please see our `CONTRIBUTING.md` (if available) for guidelines on how to submit issues, pull requests, and contribute to the development of InboxZero.

## License
This project is licensed under the [Your License Here] - see the `LICENSE` file for details.