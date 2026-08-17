from flask import Flask, Response
import requests
import threading


app = Flask(__name__)


# ============================================================
# BACKEND SERVERS
# ============================================================

BACKEND_SERVERS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]


# Current server index
current_server = 0

# Lock for thread-safe access
lock = threading.Lock()


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def load_balance(path):

    global current_server

    # ========================================================
    # ROUND ROBIN SERVER SELECTION
    # ========================================================

    with lock:

        backend_url = BACKEND_SERVERS[current_server]

        current_server = (
            current_server + 1
        ) % len(BACKEND_SERVERS)

    print(
        f"Round Robin "
        f"| Forwarded to: {backend_url}"
    )

    try:

        # Backend path
        if path:
            backend_url += "/" + path

        # Backend request
        response = requests.get(
            backend_url,
            timeout=15
        )

        # Response client ko return
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type",
                "application/json"
            )
        )

    except requests.RequestException:

        return Response(
            '{"error": "Backend server unavailable"}',
            status=503,
            content_type="application/json"
        )


# ============================================================
# LOAD BALANCER START
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Round Robin Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )