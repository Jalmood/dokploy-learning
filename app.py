import os

import psycopg2
from flask import Flask, jsonify, request, redirect, url_for, render_template

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "Dokploy Learning Project")
APP_ENV = os.getenv("APP_ENV", "Development")
APP_VERSION = os.getenv("APP_VERSION", "1.0")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not configured")

    return psycopg2.connect(
        DATABASE_URL,
        connect_timeout=5
    )


def initialize_database():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()
        conn.close()

        print("Database initialized successfully")

    except Exception as error:
        print(f"Database initialization failed: {error}")


@app.route("/")
def home():
    messages = []
    database_status = "connected"

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, message, created_at
            FROM messages
            ORDER BY id DESC
        """)

        messages = cur.fetchall()

        cur.close()
        conn.close()

    except Exception as error:
        database_status = f"error: {str(error)}"

    return render_template(
        "index.html",
        app_name=APP_NAME,
        app_env=APP_ENV,
        app_version=APP_VERSION,
        messages=messages,
        database_status=database_status
    )


@app.route("/add-message", methods=["POST"])
def add_message_form():
    message = request.form.get("message")

    if not message:
        return redirect(url_for("home"))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO messages (message)
            VALUES (%s)
            """,
            (message,)
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as error:
        print(f"Failed to insert message: {error}")

    return redirect(url_for("home"))


@app.route("/health")
def health():
    database_status = "disconnected"

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1")
        cur.fetchone()

        cur.close()
        conn.close()

        database_status = "connected"

    except Exception as error:
        database_status = f"error: {str(error)}"

    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "environment": APP_ENV,
        "version": APP_VERSION,
        "database": database_status
    })


initialize_database()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )