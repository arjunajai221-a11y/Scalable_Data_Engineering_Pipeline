from pathlib import Path
import os

import mysql.connector
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, encoding="utf-8-sig")


def get_connection():
    """Create and return a MySQL database connection."""

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


if __name__ == "__main__":
    connection = None

    try:
        connection = get_connection()

        if connection.is_connected():
            print("MySQL connection successful!")
            print("Database:", connection.database)

    except mysql.connector.Error as error:
        print("MySQL connection failed:", error)

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed.")
