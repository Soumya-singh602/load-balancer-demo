
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
        "weight": 3,
    },
    {
        "url": "http://127.0.0.1:8002",
        "weight": 2,
    },
    {
        "url": "http://127.0.0.1:8003",
        "weight": 1,
    },
]


# ============================================================
# THREAD LOCK
# ============================================================

lock = threading.Lock()


# ============================================================
# GET BACKEND ACTIVE CONNECTIONS
# ============================================================

def get_active_connections(server):

    try:

        response = requests.get(
            f"{server['url']}/status",
            timeout=2,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "active_connections",
            0,
        )

    except requests.RequestException as error:

        print(
            f"Health check failed "
            f"| Server: {server['url']} "
            f"| Error: {error}"
        )

        return None


# ============================================================
# SELECT SERVER
# WEIGHTED LEAST CONNECTIONS
# ============================================================

def select_server():

    best_server = None
    best_load = float("inf")

    for server in BACKEND_SERVERS:

        active_connections = get_active_connections(
            server
        )

        # Server unavailable
        if active_connections is None:

            continue

        weight = server["weight"]

        # Weighted Least Connections formula
        load = active_connections / weight

        print(
            f"{server['url']} "
            f"| Weight: {weight} "
            f"| Active Connections: "
            f"{active_connections} "
            f"| Load: {load:.2f}"
        )

        if load < best_load:

            best_load = load
            best_server = server

    return best_server


# ============================================================
# LOAD BALANCER ROUTES
# ============================================================

@app.route(
    "/",
    defaults={"path": ""},
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
    ],
)
@app.route(
    "/<path:path>",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
    ],
)
def load_balance(path):

    # ========================================================
    # SELECT BACKEND
    # ========================================================

    with lock:

        backend_server = select_server()

    if backend_server is None:

        return Response(
            '{"error": "No backend server available"}',
            status=503,
            content_type="application/json",
        )

    backend_url = backend_server["url"]

    # ========================================================
    # BUILD BACKEND URL
    # ========================================================

    if path:

        backend_url += "/" + path

    print(
        f"Weighted Least Connections "
        f"| Method: {request.method} "
        f"| Forwarded to: {backend_server['url']}"
    )

    try:

        # ====================================================
        # FORWARD REQUEST
        # ====================================================

        headers = {}

        content_type = request.headers.get(
            "Content-Type"
        )

        if content_type:

            headers["Content-Type"] = content_type

        response = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
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
                "application/json",
            ),
        )

    except requests.RequestException as error:

        print(
            f"Backend request failed "
            f"| Server: {backend_server['url']} "
            f"| Error: {error}"
        )

        return Response(
            '{"error": "Backend server unavailable"}',
            status=503,
            content_type="application/json",
        )


# ============================================================
# LOAD BALANCER START
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Weighted Least Connections "
        "Load Balancer running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True,
    )

