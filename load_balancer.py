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

# BACKEND_SERVERS = [
#     {
#         "url": "http://127.0.0.1:8001",
#         "connections": 0
#     },
#     {
#         "url": "http://127.0.0.1:8002",
#         "connections": 0
#     },
#     {
#         "url": "http://127.0.0.1:8003",
#         "connections": 0
#     }
# ]


# ============================================================
# WEIGHTED LEAST CONNECTIONS
# ============================================================

BACKEND_SERVERS = [
    {
        "url": "http://127.0.0.1:8001",
        "connections": 0,
        "weight": 3
    },
    {
        "url": "http://127.0.0.1:8002",
        "connections": 0,
        "weight": 2
    },
    {
        "url": "http://127.0.0.1:8003",
        "connections": 0,
        "weight": 1
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
    # WEIGHTED LEAST CONNECTION
    # ========================================================

    with lock:

        server = min(
            BACKEND_SERVERS,
            key=lambda server:
                server["connections"] / server["weight"]
        )

        server["connections"] += 1

        load_ratio = (
            server["connections"] / server["weight"]
        )

        print(
            f"Request forwarded to {server['url']} "
            f"| Weight: {server['weight']} "
            f"| Active connections: {server['connections']} "
            f"| Load Ratio: {load_ratio:.2f}"
        )

    try:

        backend_url = server["url"]

        if path:
            backend_url += "/" + path

        response = requests.get(
            backend_url,
            timeout=15
        )

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

        with lock:

            server["connections"] -= 1

            load_ratio = (
                server["connections"] / server["weight"]
            )

            print(
                f"Request completed on "
                f"{server['url']} "
                f"| Weight: {server['weight']} "
                f"| Active connections: {server['connections']} "
                f"| Load Ratio: {load_ratio:.2f}"
            )


# ============================================================
# LOAD BALANCER START
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Weighted Least Connections "
        "Load Balancer running on port 8000"
    )

    print(
        "Weights: "
        "8001=3, "
        "8002=2, "
        "8003=1"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )