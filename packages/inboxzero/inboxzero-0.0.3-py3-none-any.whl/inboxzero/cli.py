from .screen import InboxZeroApp
from .db import init_db,clear_user_credentials

def main():
    init_db()  # Initialize the database when the CLI starts
    # clear_user_credentials()
    app = InboxZeroApp()
    
    app.run()