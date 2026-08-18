
from flask import Flask, jsonify, request
import sys
import time

from database.crud import (
    create_user,
    get_users,
    update_user,
    delete_user,
)


# ============================================================
# SERVER PORT
# ============================================================

PORT = int(sys.argv[1])

app = Flask(__name__)

# Active connections count
active_connections = 0


# ============================================================
# EXISTING LOAD BALANCER TEST ROUTE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    global active_connections

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

        active_connections -= 1

        print(
            f"[Server-{PORT}] "
            f"Active connections: {active_connections}"
        )


# ============================================================
# SERVER STATUS
# USED BY WEIGHTED LEAST CONNECTIONS
# ============================================================

@app.route("/status", methods=["GET"])
def status():

    return jsonify({
        "server": f"Server-{PORT}",
        "port": PORT,
        "active_connections": active_connections,
    })


# ============================================================
# GET USERS
# READ → REPLICA
# ============================================================

@app.route("/users", methods=["GET"])
def users_list():

    users = get_users()

    return jsonify({
        "server": f"Server-{PORT}",
        "database": "replica",
        "users": [
            {
                "id": user[0],
                "name": user[1],
                "email": user[2],
            }
            for user in users
        ],
    })


# ============================================================
# CREATE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users", methods=["POST"])
def users_create():

    data = request.get_json()

    user = create_user(
        data["name"],
        data["email"],
    )

    return jsonify({
        "server": f"Server-{PORT}",
        "database": "primary",
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    }), 201


# ============================================================
# UPDATE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["PUT"])
def users_update(user_id):

    data = request.get_json()

    user = update_user(
        user_id,
        data["name"],
    )

    if user is None:

        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "server": f"Server-{PORT}",
        "database": "primary",
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    })


# ============================================================
# DELETE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["DELETE"])
def users_delete(user_id):

    user = delete_user(user_id)

    if user is None:

        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "server": f"Server-{PORT}",
        "database": "primary",
        "deleted_user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    })


# ============================================================
# SERVER START
# ============================================================

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

