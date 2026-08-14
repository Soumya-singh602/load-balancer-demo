from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

# Round Robin
#BACKEND_SERVERS = [
    #"http://127.0.0.1:8001",
    #"http://127.0.0.1:8002",
    #"http://127.0.0.1:8003",
#]

BACKEND_SERVERS = [
    {
        "url": "http://127.0.0.1:8001",
        "weight": 3
    },
    {
        "url": "http://127.0.0.1:8002",
        "weight": 2
    },
    {
        "url": "http://127.0.0.1:8003",
        "weight": 1
    }
]

weighted_servers = []

for server in BACKEND_SERVERS:
    for _ in range(server["weight"]):
        weighted_servers.append(server["url"])

current_server = 0




class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        global current_server

        # Select current backend server
        server = weighted_servers[current_server]

        # Move to next server
        current_server = (
            current_server + 1
        ) % len(weighted_servers)

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