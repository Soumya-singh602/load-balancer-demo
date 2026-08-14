from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import json


# Command line se port number lena
PORT = int(sys.argv[1])


class BackendHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        response = {
            "server": f"Server-{PORT}",
            "port": PORT,
            "message": "Hello from backend server"
        }

        response_data = json.dumps(response).encode()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response_data))
        )

        self.end_headers()

        self.wfile.write(response_data)

    def log_message(self, format, *args):
        print(
            f"[Server-{PORT}] "
            f"{self.address_string()} - "
            f"{format % args}"
        )


# Backend server start
server = HTTPServer(
    ("127.0.0.1", PORT),
    BackendHandler
)

print(
    f"Backend server running on "
    f"http://127.0.0.1:{PORT}"
)

server.serve_forever()