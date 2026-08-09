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
            <h2>Automatic Deployment Test</h2>

            <p>Hello from Docker + Dokploy!</p>
            <p>This page was automatically updated from GitHub.</p>
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
