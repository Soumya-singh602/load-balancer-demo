from flask import Flask, Response
import requests
import random


app = Flask(__name__)


# ============================================================
# BACKEND SERVERS
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
        f"Random Selection "
        f"| Forwarded to: {backend_url}"
    )

    try:

        # ====================================================
        # BACKEND PATH
        # ====================================================

        if path:
            backend_url += "/" + path

        # ====================================================
        # BACKEND REQUEST
        # ====================================================

        response = requests.get(
            backend_url,
            timeout=15
        )

        # ====================================================
        # RETURN RESPONSE TO CLIENT
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

        # ====================================================
        # BACKEND UNAVAILABLE
        # ====================================================

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