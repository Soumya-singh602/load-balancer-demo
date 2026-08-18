
from flask import Flask, Response, request
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


# ============================================================
# LOCK
# ============================================================

lock = threading.Lock()


# ============================================================
# GET ACTIVE CONNECTIONS
# ============================================================

def get_active_connections(backend_url):

    try:

        response = requests.get(
            f"{backend_url}/status",
            timeout=2
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "active_connections",
            0
        )

    except requests.RequestException:

        # Server unavailable
        return float("inf")


# ============================================================
# SELECT SERVER
# ============================================================

def select_server():

    best_server = None
    lowest_connections = float("inf")

    for backend_url in BACKEND_SERVERS:

        active_connections = get_active_connections(
            backend_url
        )

        print(
            f"{backend_url} "
            f"| Active Connections: "
            f"{active_connections}"
        )

        if active_connections < lowest_connections:

            lowest_connections = active_connections
            best_server = backend_url

    return best_server


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

    # ========================================================
    # LEAST CONNECTIONS SERVER SELECTION
    # ========================================================

    with lock:

        backend_url = select_server()

    if backend_url is None:

        return Response(
            '{"error": "No backend server available"}',
            status=503,
            content_type="application/json"
        )

    print(
        f"Least Connections "
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

    except requests.RequestException as error:

        print(
            f"Backend error: {error}"
        )

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
        "Flask Least Connections "
        "Load Balancer running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )

