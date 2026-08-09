from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>Dokploy Learning</title>
        </head>
        <body>
            <h1>Dokploy Learning Project</h1>
            <p>Hello from Docker + Dokploy!</p>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "dokploy-learning"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
