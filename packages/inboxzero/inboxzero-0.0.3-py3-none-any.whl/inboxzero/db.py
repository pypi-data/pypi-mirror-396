import sqlite3
import os
from typing import Optional, Tuple

DATABASE_FILE = "inboxzero.db"

def _get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database by creating the users table if it doesn't exist."""
    with _get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                app_password TEXT NOT NULL
            );
        """)
        conn.commit()


def clear_user_credentials():
    """Deletes all user credentials from the database."""
    with _get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()


def save_user_credentials(email: str, app_password: str):
    """Saves or updates user credentials in the database."""
    with _get_db_connection() as conn:
        cursor = conn.cursor()
        # Attempt to update existing record
        cursor.execute("""
            UPDATE users SET email = ?, app_password = ?
        """, (email, app_password))
        
        # If no rows were updated, insert a new one
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO users (email, app_password)
                VALUES (?, ?)
            """, (email, app_password))
        
        conn.commit()

def get_user_credentials() -> Optional[Tuple[str, str]]:
    """Retrieves user credentials from the database."""
    with _get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, app_password FROM users LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row["email"], row["app_password"]
        return None

if __name__ == "__main__":
    # Example usage for testing
    init_db()
    print("Database initialized and 'users' table created.")

    # Save some dummy credentials
    save_user_credentials("test@example.com", "test_app_password")
    print("Dummy credentials saved.")

    # Retrieve credentials
    creds = get_user_credentials()
    if creds:
        print(f"Retrieved credentials: Email={creds[0]}, App Password={creds[1]}")
    else:
        print("No credentials found.")

    # Update credentials
    save_user_credentials("new_test@example.com", "new_app_password")
    print("Credentials updated.")

    

    creds = get_user_credentials()
    if creds:
        print(f"Retrieved credentials: Email={creds[0]}, App Password={creds[1]}")
    else:
        print("No credentials found.")
