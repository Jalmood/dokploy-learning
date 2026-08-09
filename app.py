import os
from flask import Flask

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "Dokploy Learning Project")
APP_ENV = os.getenv("APP_ENV", "Development")
APP_VERSION = os.getenv("APP_VERSION", "1.0")


@app.route("/")
def home():
    return f"""
    <html>
        <head>
            <title>{APP_NAME}</title>
        </head>
        <body>
            <h1>{APP_NAME}</h1>

            <h2>Environment Variables Test</h2>

            <p>Environment: {APP_ENV}</p>
            <p>Version: {APP_VERSION}</p>

            <p>Hello from Docker + Dokploy!</p>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME,
        "environment": APP_ENV,
        "version": APP_VERSION
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
