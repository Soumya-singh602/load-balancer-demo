
from flask import Flask, Response, request
import requests


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
# IP HASH FUNCTION
# ============================================================

def get_server_by_ip(client_ip):

    # Convert IP into numeric hash
    hash_value = 0

    for character in client_ip:

        hash_value = (
            hash_value * 31
            + ord(character)
        )

    # Select backend server
    server_index = (
        hash_value % len(BACKEND_SERVERS)
    )

    return BACKEND_SERVERS[server_index]


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
    # CLIENT IP
    # ========================================================

    client_ip = request.remote_addr

    # ========================================================
    # IP HASH SERVER SELECTION
    # ========================================================

    backend_url = get_server_by_ip(client_ip)

    print(
        f"IP Hash "
        f"| Client IP: {client_ip} "
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
        "Flask IP Hash Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True,
    )

