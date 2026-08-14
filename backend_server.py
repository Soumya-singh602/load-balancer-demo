from flask import Flask, jsonify
import sys
import time


# Command line se port number lena
PORT = int(sys.argv[1])

app = Flask(__name__)

# Active connections count
active_connections = 0


@app.route("/", methods=["GET"])
def home():

    global active_connections

    # New request active hui
    active_connections += 1

    print(
        f"[Server-{PORT}] "
        f"Active connections: {active_connections}"
    )

    try:

        # Request ko 10 seconds tak active rakhenge
        time.sleep(10)

        return jsonify({
            "server": f"Server-{PORT}",
            "port": PORT,
            "active_connections": active_connections,
            "message": "Hello from Flask backend server"
        })

    finally:

        # Request complete hone par count decrease
        active_connections -= 1

        print(
            f"[Server-{PORT}] "
            f"Active connections: {active_connections}"
        )


if __name__ == "__main__":

    print(
        f"Flask backend server running on "
        f"http://127.0.0.1:{PORT}"
    )

    app.run(
        host="127.0.0.1",
        port=PORT,
        threaded=True
    )