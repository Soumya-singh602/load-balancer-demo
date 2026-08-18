
from flask import Flask, Response, request
import requests
import threading


app = Flask(__name__)


# ============================================================
# BACKEND SERVERS WITH WEIGHTS
# ============================================================

BACKEND_SERVERS = [
    {
        "url": "http://127.0.0.1:8001",
        "weight": 3
    },
    {
        "url": "http://127.0.0.1:8002",
        "weight": 2
    },
    {
        "url": "http://127.0.0.1:8003",
        "weight": 1
    }
]


# ============================================================
# CREATE WEIGHTED SERVER LIST
# ============================================================

weighted_servers = []

for server in BACKEND_SERVERS:

    for _ in range(server["weight"]):

        weighted_servers.append(server["url"])


# Current server index
current_server = 0

# Thread-safe access
lock = threading.Lock()


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route(
    "/",
    defaults={"path": ""},
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ]
)
@app.route(
    "/<path:path>",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ]
)
def load_balance(path):

    global current_server

    # ========================================================
    # WEIGHTED ROUND ROBIN SERVER SELECTION
    # ========================================================

    with lock:

        backend_url = weighted_servers[current_server]

        current_server = (
            current_server + 1
        ) % len(weighted_servers)

    print(
        f"Weighted Round Robin "
        f"| Method: {request.method} "
        f"| Forwarded to: {backend_url}"
    )

    # ========================================================
    # BACKEND PATH
    # ========================================================

    if path:

        backend_url += "/" + path

    try:

        # ====================================================
        # FORWARD REQUEST
        # ====================================================

        response = requests.request(
            method=request.method,
            url=backend_url,
            headers={
                "Content-Type": request.headers.get(
                    "Content-Type",
                    "application/json"
                )
            },
            data=request.get_data(),
            timeout=15,
        )

        # ====================================================
        # RETURN RESPONSE
        # ====================================================

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
        "Flask Weighted Round Robin "
        "Load Balancer running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )

