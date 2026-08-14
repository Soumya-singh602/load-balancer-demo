from flask import Flask, Response
import requests
import threading


app = Flask(__name__)


# ============================================================
# ROUND ROBIN
# ============================================================

# BACKEND_SERVERS = [
#     "http://127.0.0.1:8001",
#     "http://127.0.0.1:8002",
#     "http://127.0.0.1:8003",
# ]

# current_server = 0


# ============================================================
# WEIGHTED ROUND ROBIN
# ============================================================

# BACKEND_SERVERS = [
#     {
#         "url": "http://127.0.0.1:8001",
#         "weight": 3
#     },
#     {
#         "url": "http://127.0.0.1:8002",
#         "weight": 2
#     },
#     {
#         "url": "http://127.0.0.1:8003",
#         "weight": 1
#     }
# ]

# weighted_servers = []

# for server in BACKEND_SERVERS:
#     for _ in range(server["weight"]):
#         weighted_servers.append(server["url"])

# current_server = 0


# ============================================================
# LEAST CONNECTIONS
# ============================================================

BACKEND_SERVERS = [
    {
        "url": "http://127.0.0.1:8001",
        "connections": 0
    },
    {
        "url": "http://127.0.0.1:8002",
        "connections": 0
    },
    {
        "url": "http://127.0.0.1:8003",
        "connections": 0
    }
]


# Multiple requests ke time counter safely update karne ke liye
lock = threading.Lock()


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def load_balance(path):

    # ========================================================
    # LEAST CONNECTION SERVER SELECT
    # ========================================================

    with lock:

        server = min(
            BACKEND_SERVERS,
            key=lambda server: server["connections"]
        )

        # Selected server ki connection count increase
        server["connections"] += 1

        print(
            f"Request forwarded to {server['url']} "
            f"| Active connections: "
            f"{server['connections']}"
        )

    try:

        # Backend URL
        backend_url = server["url"]

        if path:
            backend_url += "/" + path

        # Backend ko request
        response = requests.get(
            backend_url,
            timeout=15
        )

        # Backend response client ko return
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
        # REQUEST COMPLETE
        # ====================================================

        with lock:

            server["connections"] -= 1

            print(
                f"Request completed on "
                f"{server['url']} "
                f"| Active connections: "
                f"{server['connections']}"
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