from flask import Flask, Response
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
        "connections": 0
    },
    {
        "url": "http://127.0.0.1:8002",
        "weight": 2,
        "connections": 0
    },
    {
        "url": "http://127.0.0.1:8003",
        "weight": 1,
        "connections": 0
    }
]


# ============================================================
# THREAD LOCK
# ============================================================

lock = threading.Lock()


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def load_balance(path):

    # ========================================================
    # WEIGHTED LEAST CONNECTION SELECTION
    # ========================================================

    with lock:

        backend_server = min(
            BACKEND_SERVERS,
            key=lambda server:
                server["connections"] / server["weight"]
        )

        # Increase active connections
        backend_server["connections"] += 1

        backend_url = backend_server["url"]

        current_load = (
            backend_server["connections"]
            / backend_server["weight"]
        )

        print(
            f"Weighted Least Connections "
            f"| Forwarded to: {backend_url} "
            f"| Weight: {backend_server['weight']} "
            f"| Active Connections: "
            f"{backend_server['connections']} "
            f"| Load: {current_load:.2f}"
        )

    try:

        # ====================================================
        # BACKEND PATH
        # ====================================================

        if path:
            backend_url += "/" + path

        # ====================================================
        # SEND REQUEST
        # ====================================================

        response = requests.get(
            backend_url,
            timeout=15
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

    finally:

        # ====================================================
        # REQUEST COMPLETED
        # DECREASE CONNECTION COUNT
        # ====================================================

        with lock:

            backend_server["connections"] -= 1

            current_load = (
                backend_server["connections"]
                / backend_server["weight"]
            )

            print(
                f"Connection completed "
                f"| Server: {backend_server['url']} "
                f"| Active Connections: "
                f"{backend_server['connections']} "
                f"| Load: {current_load:.2f}"
            )


# ============================================================
# START LOAD BALANCER
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Weighted Least Connections Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )