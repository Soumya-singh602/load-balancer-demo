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


current_server = 0

lock = threading.Lock()


# ============================================================
# LOAD BALANCER
# ============================================================

@app.route("/", defaults={"path": ""}, methods=[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
])
@app.route("/<path:path>", methods=[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
])
def load_balance(path):

    global current_server

    # --------------------------------------------------------
    # ROUND ROBIN SERVER SELECTION
    # --------------------------------------------------------

    with lock:

        backend_url = BACKEND_SERVERS[current_server]

        current_server = (
            current_server + 1
        ) % len(BACKEND_SERVERS)

    print(
        f"Round Robin "
        f"| Method: {request.method} "
        f"| Forwarded to: {backend_url}"
    )

    try:

        if path:
            backend_url += "/" + path

        # ----------------------------------------------------
        # FORWARD REQUEST
        # ----------------------------------------------------

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
# START LOAD BALANCER
# ============================================================

if __name__ == "__main__":

    print(
        "Flask Round Robin Load Balancer "
        "running on port 8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True
    )