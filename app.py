import os

import psycopg2
from flask import Flask, jsonify, request

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
    return f"""
    <html>
        <head>
            <title>{APP_NAME}</title>
        </head>

        <body>

            <h1>{APP_NAME}</h1>

            <h2>Docker + Dokploy + PostgreSQL</h2>

            <p>Environment: {APP_ENV}</p>
            <p>Version: {APP_VERSION}</p>

            <hr>

            <p>
                <a href="/health">Health Check</a>
            </p>

            <p>
                <a href="/messages">View Messages</a>
            </p>

        </body>
    </html>
    """


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


@app.route("/messages", methods=["GET"])
def get_messages():

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                message,
                created_at
            FROM messages
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        messages = []

        for row in rows:
            messages.append({
                "id": row[0],
                "message": row[1],
                "created_at": row[2].isoformat()
            })

        return jsonify(messages)

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


@app.route("/messages", methods=["POST"])
def add_message():

    data = request.get_json(silent=True)

    if not data or not data.get("message"):
        return jsonify({
            "status": "error",
            "message": "message is required"
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO messages (message)
            VALUES (%s)
            RETURNING id
            """,
            (data["message"],)
        )

        message_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "created",
            "id": message_id,
            "message": data["message"]
        }), 201

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


initialize_database()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
