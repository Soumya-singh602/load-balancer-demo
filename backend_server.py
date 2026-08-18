
from flask import Flask, jsonify, request
import sys
import time
import threading

from database.crud import (
    create_user,
    get_users,
    get_user,
    search_users,
    count_users,
    update_user,
    delete_user,
)

from database.primary import get_primary_connection
from database.replica import get_replica_connection


# ============================================================
# SERVER CONFIGURATION
# ============================================================

if len(sys.argv) < 2:
    print("Usage: python api_server.py <port>")
    sys.exit(1)

PORT = int(sys.argv[1])

app = Flask(__name__)

active_connections = 0
connection_lock = threading.Lock()


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database(connection_function):

    connection = None

    try:
        connection = connection_function()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return "healthy"

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"Database health check failed: {e}"
        )

        return "unhealthy"

    finally:

        if connection:
            connection.close()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    primary_status = check_database(
        get_primary_connection
    )

    replica_status = check_database(
        get_replica_connection
    )

    if (
        primary_status == "healthy"
        and replica_status == "healthy"
    ):
        overall_status = "healthy"

        status_code = 200

    else:
        overall_status = "degraded"

        status_code = 503

    return jsonify({
        "status": overall_status,

        "server": f"Server-{PORT}",

        "port": PORT,

        "database": {
            "primary": {
                "status": primary_status,
                "port": 5432,
            },

            "replica": {
                "status": replica_status,
                "port": 5434,
            },
        },
    }), status_code


# ============================================================
# LOAD BALANCER TEST ROUTE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    global active_connections

    with connection_lock:
        active_connections += 1
        current_connections = active_connections

    print(
        f"[Server-{PORT}] "
        f"Active connections: {current_connections}"
    )

    try:

        time.sleep(10)

        with connection_lock:
            current_connections = active_connections

        return jsonify({
            "server": f"Server-{PORT}",
            "port": PORT,
            "active_connections": current_connections,
            "message": "Hello from Flask backend server",
        })

    finally:

        with connection_lock:
            active_connections -= 1
            current_connections = active_connections

        print(
            f"[Server-{PORT}] "
            f"Active connections: {current_connections}"
        )


# ============================================================
# SERVER STATUS
# ============================================================

@app.route("/status", methods=["GET"])
def status():

    with connection_lock:
        current_connections = active_connections

    return jsonify({
        "server": f"Server-{PORT}",
        "port": PORT,
        "active_connections": current_connections,
    })


# ============================================================
# GET ALL USERS
# READ → REPLICA
# ============================================================

@app.route("/users", methods=["GET"])
def users_list():

    try:

        users = get_users()

        return jsonify({
            "server": f"Server-{PORT}",
            "database": "replica",
            "count": len(users),
            "users": [
                {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                }
                for user in users
            ],
        })

    except Exception as e:

        print(f"[Server-{PORT}] GET /users error: {e}")

        return jsonify({
            "error": "Unable to fetch users",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# SEARCH USERS
# READ → REPLICA
# ============================================================

@app.route("/users/search", methods=["GET"])
def users_search():

    search_term = request.args.get("q", "").strip()

    if not search_term:

        return jsonify({
            "error": "Search query 'q' is required",
            "example": "/users/search?q=Rahul",
        }), 400

    try:

        users = search_users(search_term)

        return jsonify({
            "server": f"Server-{PORT}",
            "database": "replica",
            "search": search_term,
            "count": len(users),
            "users": [
                {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                }
                for user in users
            ],
        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users/search error: {e}"
        )

        return jsonify({
            "error": "Unable to search users",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# COUNT USERS
# READ → REPLICA
# ============================================================

@app.route("/users/count", methods=["GET"])
def users_count():

    try:

        total = count_users()

        return jsonify({
            "server": f"Server-{PORT}",
            "database": "replica",
            "total_users": total,
        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users/count error: {e}"
        )

        return jsonify({
            "error": "Unable to count users",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# GET SINGLE USER
# READ → REPLICA
# ============================================================

@app.route("/users/<int:user_id>", methods=["GET"])
def user_detail(user_id):

    if user_id <= 0:

        return jsonify({
            "error": "Invalid user ID",
        }), 400

    try:

        user = get_user(user_id)

        if user is None:

            return jsonify({
                "error": "User not found",
                "user_id": user_id,
            }), 404

        return jsonify({
            "server": f"Server-{PORT}",
            "database": "replica",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
            },
        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users/{user_id} error: {e}"
        )

        return jsonify({
            "error": "Unable to fetch user",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# CREATE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users", methods=["POST"])
def users_create():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "JSON request body is required",
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:

        return jsonify({
            "error": "name and email are required",
        }), 400

    try:

        user = create_user(
            name.strip(),
            email.strip(),
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

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"POST /users error: {e}"
        )

        return jsonify({
            "error": "Unable to create user",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# UPDATE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["PUT"])
def users_update(user_id):

    if user_id <= 0:

        return jsonify({
            "error": "Invalid user ID",
        }), 400

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "JSON request body is required",
        }), 400

    name = data.get("name")

    if not name:

        return jsonify({
            "error": "name is required",
        }), 400

    try:

        user = update_user(
            user_id,
            name.strip(),
        )

        if user is None:

            return jsonify({
                "error": "User not found",
                "user_id": user_id,
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

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"PUT /users/{user_id} error: {e}"
        )

        return jsonify({
            "error": "Unable to update user",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# DELETE USER
# WRITE → PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["DELETE"])
def users_delete(user_id):

    if user_id <= 0:

        return jsonify({
            "error": "Invalid user ID",
        }), 400

    try:

        user = delete_user(user_id)

        if user is None:

            return jsonify({
                "error": "User not found",
                "user_id": user_id,
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

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"DELETE /users/{user_id} error: {e}"
        )

        return jsonify({
            "error": "Unable to delete user",
            "server": f"Server-{PORT}",
        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Endpoint not found",
        "server": f"Server-{PORT}",
        "port": PORT,
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "error": "HTTP method not allowed",
        "server": f"Server-{PORT}",
        "port": PORT,
    }), 405


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
        threaded=True,
    )

