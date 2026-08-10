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

    status = db.Column(
        db.String(50),
        nullable=False,
        server_default="Active"
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
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )
        }

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    project = db.Column(
        db.String(100),
        nullable=True
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        server_default="Medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        server_default="New"
    )

    progress = db.Column(
        db.Integer,
        nullable=False,
        server_default="0"
    )

    start_date = db.Column(
        db.Date,
        nullable=True
    )

    due_date = db.Column(
        db.Date,
        nullable=True
    )

    assigned_to = db.Column(
        db.String(100),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "project": self.project,
            "priority": self.priority,
            "status": self.status,
            "progress": self.progress,
            "start_date": (
                self.start_date.isoformat()
                if self.start_date
                else None
            ),
            "due_date": (
                self.due_date.isoformat()
                if self.due_date
                else None
            ),
            "assigned_to": self.assigned_to,
            "notes": self.notes,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            )
        }

@app.route("/")
def home():
    database_status = "connected"
    tasks = []

    try:
        tasks = Task.query.order_by(
            Task.id.desc()
        ).all()

    except Exception as error:
        database_status = f"error: {str(error)}"

    return render_template(
        "index.html",
        app_name=APP_NAME,
        app_env=APP_ENV,
        app_version=APP_VERSION,
        tasks=tasks,
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

@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    project = request.form.get("project")
    priority = request.form.get("priority", "Medium")
    status = request.form.get("status", "New")
    start_date = request.form.get("start_date")
    due_date = request.form.get("due_date")
    assigned_to = request.form.get("assigned_to")
    notes = request.form.get("notes")

    if not title:
        return redirect(url_for("home"))

    try:
        new_task = Task(
            title=title,
            description=description,
            category=category,
            project=project,
            priority=priority,
            status=status,
            start_date=start_date or None,
            due_date=due_date or None,
            assigned_to=assigned_to,
            notes=notes
        )

        db.session.add(new_task)
        db.session.commit()

    except Exception as error:
        db.session.rollback()
        print(f"Failed to create task: {error}")

    return redirect(url_for("home"))

@app.route("/tasks/<int:task_id>/update", methods=["POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        task.title = request.form.get("title", task.title)
        task.category = request.form.get("category")
        task.project = request.form.get("project")
        task.priority = request.form.get("priority", task.priority)
        task.status = request.form.get("status", task.status)

        progress = request.form.get("progress", task.progress)

        try:
            progress = int(progress)
            progress = max(0, min(100, progress))
        except (TypeError, ValueError):
            progress = task.progress

        task.progress = progress

        # Keep status and progress consistent
        if task.status == "Completed":
            task.progress = 100
            task.completed_at = db.func.now()

        elif task.progress == 100:
            task.status = "Completed"
            task.completed_at = db.func.now()

        else:
            task.completed_at = None

        db.session.commit()

    except Exception as error:
        db.session.rollback()
        print(f"Failed to update task: {error}")

    return redirect(url_for("home"))

@app.route("/tasks/<int:task_id>/edit")
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    return render_template(
        "edit_task.html",
        task=task,
        app_name=APP_NAME
    )

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        db.session.delete(task)
        db.session.commit()

    except Exception as error:
        db.session.rollback()
        print(f"Failed to delete task: {error}")

    return redirect(url_for("home"))

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