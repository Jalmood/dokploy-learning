import os

import psycopg2
from flask import Flask, jsonify, request, redirect, url_for

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


@app.route("/", methods=["GET"])
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

    message_rows = ""

    for row in messages:
        message_rows += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{APP_NAME}</title>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}

            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .info {{
                color: #666;
                margin-bottom: 30px;
            }}

            form {{
                margin-bottom: 30px;
            }}

            input[type="text"] {{
                width: 70%;
                padding: 10px;
                font-size: 16px;
            }}

            button {{
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}

            th {{
                background-color: #f0f0f0;
            }}

            .status {{
                margin-top: 20px;
                padding: 10px;
                background-color: #eeeeee;
            }}
        </style>

    </head>

    <body>

        <div class="container">

            <h1>{APP_NAME}</h1>

            <div class="info">
                Environment: {APP_ENV}<br>
                Version: {APP_VERSION}
            </div>

            <h2>Add Message</h2>

            <form method="POST" action="/add-message">

                <input
                    type="text"
                    name="message"
                    placeholder="Write a message..."
                    required
                >

                <button type="submit">
                    Add Message
                </button>

            </form>

            <h2>Messages</h2>

            <table>

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Message</th>
                        <th>Created At</th>
                    </tr>
                </thead>

                <tbody>
                    {message_rows}
                </tbody>

            </table>

            <div class="status">
                Database: {database_status}
            </div>

        </div>

    </body>
    </html>
    """


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


@app.route("/health", methods=["GET"])
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
            SELECT id, message, created_at
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
def add_message_api():
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
