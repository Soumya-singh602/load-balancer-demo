from http.server import BaseHTTPRequestHandler, HTTPServer
import requests


BACKEND_SERVERS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]


current_server = 0


class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        global current_server

        # Select current backend server
        server = BACKEND_SERVERS[current_server]

        # Move to next server
        current_server = (
            current_server + 1
        ) % len(BACKEND_SERVERS)

        print(f"Request forwarded to {server}")

        try:

            response = requests.get(
                server + self.path,
                timeout=5
            )

            self.send_response(response.status_code)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(response.content)

        except requests.RequestException:

            self.send_response(503)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                b'{"error": "Backend server unavailable"}'
            )


load_balancer = HTTPServer(
    ("127.0.0.1", 8000),
    LoadBalancerHandler
)

print("Load Balancer running on port 8000")

load_balancer.serve_forever()