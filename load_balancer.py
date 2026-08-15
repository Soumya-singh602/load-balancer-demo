from flask import Flask, Response, request
import requests
import threading
import hashlib
import random


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

# lock = threading.Lock()


# ============================================================
# WEIGHTED LEAST CONNECTIONS
# ============================================================

# BACKEND_SERVERS = [
#     {
#         "url": "http://127.0.0.1:8001",
#         "weight": 3,
#         "connections": 0
#     },
#     {
#         "url": "http://127.0.0.1:8002",
#         "weight": 2,
#         "connections": 0
#     },
#     {
#         "url": "http://127.0.0.1:8003",
#         "weight": 1,
#         "connections": 0
#     }
# ]

# lock = threading.Lock()


# ============================================================
# IP HASH
# ============================================================

# BACKEND_SERVERS = [
#     "http://127.0.0.1:8001",
#     "http://127.0.0.1:8002",
#     "http://127.0.0.1:8003"
# ]


# ============================================================
# RANDOM
# ============================================================

BACKEND_SERVERS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003"
]


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def load_balance(path):

    # ========================================================
    # RANDOM SERVER SELECTION
    # ========================================================

    backend_url = random.choice(BACKEND_SERVERS)

    print(
        f"Random selection "
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
        "Flask Random Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )