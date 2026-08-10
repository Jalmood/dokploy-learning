import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "Dokploy Learning Project")
APP_ENV = os.getenv("APP_ENV", "Development")
APP_VERSION = os.getenv("APP_VERSION", "1.0")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not configured")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "author": self.author,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )
        }


@app.route("/")
def home():
    database_status = "connected"
    messages = []

    try:
        messages = Message.query.order_by(
            Message.id.desc()
        ).all()

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
    message_text = request.form.get("message")
    author = request.form.get("author")

    if not message_text:
        return redirect(
            url_for("home")
        )

    try:
        new_message = Message(
            message=message_text,
            author=author
        )

        db.session.add(new_message)
        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print(
            f"Failed to insert message: {error}"
        )

    return redirect(
        url_for("home")
    )


@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        messages = Message.query.order_by(
            Message.id.desc()
        ).all()

        return jsonify([
            message.to_dict()
            for message in messages
        ])

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
        new_message = Message(
            message=data["message"],
            author=data.get("author")
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            "status": "created",
            "message": new_message.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


@app.route("/health")
def health():
    try:
        db.session.execute(
            db.text("SELECT 1")
        )

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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=APP_ENV == "Development"
    )