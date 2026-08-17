from flask import Flask, Response, request
import requests
import hashlib


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
# IP HASH SERVER SELECTION
# ============================================================

def get_server_from_ip(client_ip):

    # --------------------------------------------------------
    # Client IP ko bytes mein convert karna
    # --------------------------------------------------------

    ip_bytes = client_ip.encode("utf-8")

    # --------------------------------------------------------
    # SHA-256 hash generate karna
    # --------------------------------------------------------

    hash_value = hashlib.sha256(ip_bytes).hexdigest()

    # --------------------------------------------------------
    # Hash ko integer mein convert karna
    # --------------------------------------------------------

    hash_number = int(hash_value, 16)

    # --------------------------------------------------------
    # Backend server index calculate karna
    # --------------------------------------------------------

    server_index = hash_number % len(BACKEND_SERVERS)

    # --------------------------------------------------------
    # Server URL + hash + index return karna
    # --------------------------------------------------------

    return (
        BACKEND_SERVERS[server_index],
        hash_value,
        server_index
    )


# ============================================================
# LOAD BALANCER ROUTE
# ============================================================

@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def load_balance(path):

    # ========================================================
    # CLIENT IP
    # ========================================================

    client_ip = request.remote_addr

    # ========================================================
    # IP HASH SERVER SELECTION
    # ========================================================

    backend_url, hash_value, server_index = get_server_from_ip(
        client_ip
    )

    print(
        f"IP Hash "
        f"| Client IP: {client_ip} "
        f"| Hash: {hash_value} "
        f"| Server Index: {server_index} "
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

    except requests.RequestException as error:

        print(
            f"Backend request failed "
            f"| Server: {backend_url} "
            f"| Error: {error}"
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
        "Flask IP Hash Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )