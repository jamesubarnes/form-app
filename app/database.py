import os
import psycopg2

# Database configuration
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "formapp"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
}


def get_db_connection() -> psycopg2.extensions.connection:
    """Create and return a database connection"""
    return psycopg2.connect(**DB_CONFIG)


def insert_user(
    first_name: str, last_name: str, email: str, favourite_colour: str
) -> int:
    """Insert a user and return the new user id."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (first_name, last_name, email, favourite_colour)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (first_name, last_name, email, favourite_colour),
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
