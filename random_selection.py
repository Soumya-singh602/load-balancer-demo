from flask import Flask, Response, request
import requests
import random
from rate_limiter import is_allowed


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
# LOAD BALANCER ROUTE
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
    # RATE LIMITING
    # ========================================================

    client_ip = request.remote_addr

    if not is_allowed(client_ip):

        print(
            f"Rate Limit Exceeded "
            f"| IP: {client_ip}"
        )

        return Response(
            '{"error": "Rate limit exceeded", '
            '"message": "Too many requests. Try again later."}',
            status=429,
            content_type="application/json",
        )

    # ========================================================
    # RANDOM SERVER SELECTION
    # ========================================================

    backend_url = random.choice(
        BACKEND_SERVERS
    )

    print(
        f"Random Selection "
        f"| Method: {request.method} "
        f"| Forwarded to: {backend_url}"
    )

    # ========================================================
    # BUILD BACKEND URL
    # ========================================================

    if path:

        backend_url += "/" + path

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
            f"| Server: {backend_url} "
            f"| Error: {error}"
        )

        return Response(
            '{"error": "Backend server unavailable"}',
            status=503,
            content_type="application/json",
        )


# ============================================================
# START LOAD BALANCER
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Random Selection Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True,
    )