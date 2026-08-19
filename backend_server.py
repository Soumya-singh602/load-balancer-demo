from flask import Flask, jsonify, request

import sys
import time
import threading

from database.crud import (
    create_user,
    get_users,
    get_users_from_shard,
    get_user_from_shard,
    get_user_by_id,
    search_users,
    count_users,
    update_user,
    update_user_by_id,
    delete_user,
    delete_user_by_id,
)

from database.shard_router import (
    get_shard_id_from_email,
    get_shard_id,
)

from database.primary import get_primary_connection
from database.replica import get_replica_connection

from database.shard2_primary import get_shard2_primary_connection
from database.shard2_replica import get_shard2_replica_connection


# ============================================================
# SERVER CONFIGURATION
# ============================================================

if len(sys.argv) < 2:

    print(
        "Usage: python backend_server.py <port>"
    )

    sys.exit(1)


PORT = int(sys.argv[1])

app = Flask(__name__)

active_connections = 0

connection_lock = threading.Lock()


# ============================================================
# SHARD INFORMATION
# ============================================================

def get_shard_info(shard_id):

    if shard_id == 1:

        return {
            "shard": "Shard 1",
            "shard_id": 1,
            "write_port": 5432,
            "read_port": 5434,
        }

    if shard_id == 2:

        return {
            "shard": "Shard 2",
            "shard_id": 2,
            "write_port": 5435,
            "read_port": 5436,
        }

    raise ValueError(
        f"Invalid shard ID: {shard_id}"
    )


# ============================================================
# GET WRITE CONNECTION
# ============================================================

def get_write_connection(shard_id):

    if shard_id == 1:

        return get_primary_connection()

    if shard_id == 2:

        return get_shard2_primary_connection()

    raise ValueError(
        f"Invalid shard ID: {shard_id}"
    )


# ============================================================
# GET READ CONNECTION
# ============================================================

def get_read_connection(shard_id):

    if shard_id == 1:

        return get_replica_connection()

    if shard_id == 2:

        return get_shard2_replica_connection()

    raise ValueError(
        f"Invalid shard ID: {shard_id}"
    )


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

    shard1_write_status = check_database(
        get_primary_connection
    )

    shard1_read_status = check_database(
        get_replica_connection
    )

    shard2_write_status = check_database(
        get_shard2_primary_connection
    )

    shard2_read_status = check_database(
        get_shard2_replica_connection
    )

    all_healthy = (
        shard1_write_status == "healthy"
        and shard1_read_status == "healthy"
        and shard2_write_status == "healthy"
        and shard2_read_status == "healthy"
    )

    if all_healthy:

        overall_status = "healthy"

        status_code = 200

    else:

        overall_status = "degraded"

        status_code = 503

    return jsonify({

        "status": overall_status,

        "server": f"Server-{PORT}",

        "port": PORT,

        "shards": {

            "shard1": {

                "name": "Shard 1",

                "write_database": {

                    "status": shard1_write_status,

                    "port": 5432,

                },

                "read_database": {

                    "status": shard1_read_status,

                    "port": 5434,

                },

            },

            "shard2": {

                "name": "Shard 2",

                "write_database": {

                    "status": shard2_write_status,

                    "port": 5435,

                },

                "read_database": {

                    "status": shard2_read_status,

                    "port": 5436,

                },

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
# CREATE USER - AUTOMATIC SHARDING
#
# POST /users
#
# EMAIL
#   ↓
# SHARD ROUTER
#   ↓
# SHARD 1 / SHARD 2
#   ↓
# PRIMARY DATABASE
#
# ID generated by PostgreSQL.
#
# Shard 1 → odd IDs
# Shard 2 → even IDs
# ============================================================

@app.route("/users", methods=["POST"])
def create_user_auto():

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

        name = name.strip()

        email = email.strip().lower()

        # ----------------------------------------------------
        # AUTOMATIC SHARD SELECTION
        # ----------------------------------------------------

        shard_id = get_shard_id_from_email(
            email
        )

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = create_user(
            shard_id,
            name,
            email,
        )

        shard_info = get_shard_info(
            shard_id
        )

        return jsonify({

            "server": f"Server-{PORT}",

            "operation": "CREATE",

            "shard": shard_info["shard"],

            "shard_id": shard_id,

            "write_database": {

                "name":
                    f"{shard_info['shard']} Write",

                "port":
                    shard_info["write_port"],

            },

            "read_database": {

                "name":
                    f"{shard_info['shard']} Read",

                "port":
                    shard_info["read_port"],

            },

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

        }), 500


# ============================================================
# GET ALL USERS
#
# GET /users
#
# READ → BOTH SHARD REPLICAS
# ============================================================

@app.route("/users", methods=["GET"])
def users_list():

    try:

        users = get_users()

        formatted_users = []

        for user in users:

            formatted_users.append({

                "id": user[0],

                "name": user[1],

                "email": user[2],

                "shard": (
                    "Shard 1"
                    if user[3] == 1
                    else "Shard 2"
                ),

            })

        return jsonify({

            "server": f"Server-{PORT}",

            "database":
                "Shard Read Databases",

            "count":
                len(formatted_users),

            "users":
                formatted_users,

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users error: {e}"
        )

        return jsonify({

            "error": "Unable to fetch users",

        }), 500


# ============================================================
# GET USER BY GLOBAL ID
#
# GET /users/<id>
#
# ID
#   ↓
# SHARD ROUTER
#   ↓
# CORRECT REPLICA
#
# Example:
#
# GET /users/7
# 7 → Shard 1 → Replica :5434
#
# GET /users/8
# 8 → Shard 2 → Replica :5436
# ============================================================

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_auto(user_id):

    if user_id <= 0:

        return jsonify({
            "error": "Invalid user ID",
        }), 400

    try:

        user, shard_id = get_user_by_id(
            user_id
        )

        if user is None:

            return jsonify({

                "error": "User not found",

                "user_id": user_id,

            }), 404

        shard_info = get_shard_info(
            shard_id
        )

        return jsonify({

            "server": f"Server-{PORT}",

            "operation": "GET",

            "shard": shard_info["shard"],

            "shard_id": shard_id,

            "read_database": {

                "name":
                    f"{shard_info['shard']} Read",

                "port":
                    shard_info["read_port"],

            },

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

        }), 500


# ============================================================
# SEARCH USERS
#
# GET /users/search?q=...
#
# READ → BOTH SHARD REPLICAS
# ============================================================

@app.route("/users/search", methods=["GET"])
def users_search():

    search_term = request.args.get(
        "q",
        ""
    ).strip()

    if not search_term:

        return jsonify({

            "error":
                "Search query 'q' is required",

            "example":
                "/users/search?q=Rahul",

        }), 400

    try:

        users = search_users(
            search_term
        )

        formatted_users = []

        for user in users:

            formatted_users.append({

                "id": user[0],

                "name": user[1],

                "email": user[2],

                "shard": (
                    "Shard 1"
                    if user[3] == 1
                    else "Shard 2"
                ),

            })

        return jsonify({

            "server": f"Server-{PORT}",

            "database":
                "Shard Read Databases",

            "search":
                search_term,

            "count":
                len(formatted_users),

            "users":
                formatted_users,

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users/search error: {e}"
        )

        return jsonify({

            "error":
                "Unable to search users",

        }), 500


# ============================================================
# COUNT USERS
#
# GET /users/count
# ============================================================

@app.route("/users/count", methods=["GET"])
def users_count():

    try:

        total = count_users()

        return jsonify({

            "server": f"Server-{PORT}",

            "database":
                "Shard Read Databases",

            "total_users":
                total,

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /users/count error: {e}"
        )

        return jsonify({

            "error":
                "Unable to count users",

        }), 500


# ============================================================
# UPDATE USER BY GLOBAL ID
#
# PUT /users/<id>
#
# ID → SHARD
# WRITE → CORRECT PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user_auto(user_id):

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

        # ----------------------------------------------------
        # FIND SHARD FROM GLOBAL ID
        # ----------------------------------------------------

        shard_id = get_shard_id(
            user_id
        )

        # ----------------------------------------------------
        # CHECK USER
        # ----------------------------------------------------

        existing_user = get_user_from_shard(
            shard_id,
            user_id
        )

        if existing_user is None:

            return jsonify({

                "error":
                    "User not found",

                "user_id":
                    user_id,

            }), 404

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        user = update_user(
            shard_id,
            user_id,
            name.strip(),
        )

        shard_info = get_shard_info(
            shard_id
        )

        return jsonify({

            "server": f"Server-{PORT}",

            "operation": "UPDATE",

            "shard":
                shard_info["shard"],

            "shard_id":
                shard_id,

            "write_database": {

                "name":
                    f"{shard_info['shard']} Write",

                "port":
                    shard_info["write_port"],

            },

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

            "error":
                "Unable to update user",

        }), 500


# ============================================================
# DELETE USER BY GLOBAL ID
#
# DELETE /users/<id>
#
# ID → SHARD
# WRITE → CORRECT PRIMARY
# ============================================================

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user_auto(user_id):

    if user_id <= 0:

        return jsonify({
            "error": "Invalid user ID",
        }), 400

    try:

        # ----------------------------------------------------
        # FIND SHARD FROM GLOBAL ID
        # ----------------------------------------------------

        shard_id = get_shard_id(
            user_id
        )

        # ----------------------------------------------------
        # CHECK USER
        # ----------------------------------------------------

        existing_user = get_user_from_shard(
            shard_id,
            user_id
        )

        if existing_user is None:

            return jsonify({

                "error":
                    "User not found",

                "user_id":
                    user_id,

            }), 404

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        user = delete_user(
            shard_id,
            user_id
        )

        shard_info = get_shard_info(
            shard_id
        )

        return jsonify({

            "server": f"Server-{PORT}",

            "operation": "DELETE",

            "shard":
                shard_info["shard"],

            "shard_id":
                shard_id,

            "write_database": {

                "name":
                    f"{shard_info['shard']} Write",

                "port":
                    shard_info["write_port"],

            },

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

            "error":
                "Unable to delete user",

        }), 500


# ============================================================
# SHARD 1 - CREATE USER
#
# POST /shard1/users
#
# Optional testing endpoint.
# ============================================================

@app.route("/shard1/users", methods=["POST"])
def create_shard1_user():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error":
                "JSON request body is required",
        }), 400

    name = data.get("name")

    email = data.get("email")

    if not name or not email:

        return jsonify({
            "error":
                "name and email are required",
        }), 400

    try:

        user = create_user(
            1,
            name.strip(),
            email.strip().lower(),
        )

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 1",

            "shard_id":
                1,

            "write_database": {

                "name":
                    "Shard 1 Write",

                "port":
                    5432,

            },

            "read_database": {

                "name":
                    "Shard 1 Read",

                "port":
                    5434,

            },

            "user": {

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

            },

        }), 201

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"POST /shard1/users error: {e}"
        )

        return jsonify({

            "error":
                "Unable to create user",

        }), 500


# ============================================================
# SHARD 1 - GET ALL
#
# GET /shard1/users
# ============================================================

@app.route("/shard1/users", methods=["GET"])
def get_all_shard1_users():

    try:

        users = get_users_from_shard(1)

        formatted_users = []

        for user in users:

            formatted_users.append({

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

                "shard":
                    "Shard 1",

            })

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 1",

            "read_database": {

                "name":
                    "Shard 1 Read",

                "port":
                    5434,

            },

            "count":
                len(formatted_users),

            "users":
                formatted_users,

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /shard1/users error: {e}"
        )

        return jsonify({

            "error":
                "Unable to fetch Shard 1 users",

        }), 500


# ============================================================
# SHARD 1 - GET USER
#
# GET /shard1/users/<id>
# ============================================================

@app.route("/shard1/users/<int:user_id>", methods=["GET"])
def get_shard1_user(user_id):

    if user_id <= 0:

        return jsonify({
            "error":
                "Invalid user ID",
        }), 400

    try:

        user = get_user_from_shard(
            1,
            user_id
        )

        if user is None:

            return jsonify({

                "error":
                    "User not found",

                "user_id":
                    user_id,

                "shard":
                    "Shard 1",

            }), 404

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 1",

            "read_database": {

                "name":
                    "Shard 1 Read",

                "port":
                    5434,

            },

            "user": {

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

            },

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /shard1/users/{user_id} error: {e}"
        )

        return jsonify({

            "error":
                "Unable to fetch user",

        }), 500


# ============================================================
# SHARD 2 - CREATE USER
#
# POST /shard2/users
# ============================================================

@app.route("/shard2/users", methods=["POST"])
def create_shard2_user():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error":
                "JSON request body is required",
        }), 400

    name = data.get("name")

    email = data.get("email")

    if not name or not email:

        return jsonify({
            "error":
                "name and email are required",
        }), 400

    try:

        user = create_user(
            2,
            name.strip(),
            email.strip().lower(),
        )

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 2",

            "shard_id":
                2,

            "write_database": {

                "name":
                    "Shard 2 Write",

                "port":
                    5435,

            },

            "read_database": {

                "name":
                    "Shard 2 Read",

                "port":
                    5436,

            },

            "user": {

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

            },

        }), 201

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"POST /shard2/users error: {e}"
        )

        return jsonify({

            "error":
                "Unable to create user",

        }), 500


# ============================================================
# SHARD 2 - GET ALL
#
# GET /shard2/users
# ============================================================

@app.route("/shard2/users", methods=["GET"])
def get_all_shard2_users():

    try:

        users = get_users_from_shard(2)

        formatted_users = []

        for user in users:

            formatted_users.append({

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

                "shard":
                    "Shard 2",

            })

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 2",

            "read_database": {

                "name":
                    "Shard 2 Read",

                "port":
                    5436,

            },

            "count":
                len(formatted_users),

            "users":
                formatted_users,

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /shard2/users error: {e}"
        )

        return jsonify({

            "error":
                "Unable to fetch Shard 2 users",

        }), 500


# ============================================================
# SHARD 2 - GET USER
#
# GET /shard2/users/<id>
# ============================================================

@app.route("/shard2/users/<int:user_id>", methods=["GET"])
def get_shard2_user(user_id):

    if user_id <= 0:

        return jsonify({
            "error":
                "Invalid user ID",
        }), 400

    try:

        user = get_user_from_shard(
            2,
            user_id
        )

        if user is None:

            return jsonify({

                "error":
                    "User not found",

                "user_id":
                    user_id,

                "shard":
                    "Shard 2",

            }), 404

        return jsonify({

            "server":
                f"Server-{PORT}",

            "shard":
                "Shard 2",

            "read_database": {

                "name":
                    "Shard 2 Read",

                "port":
                    5436,

            },

            "user": {

                "id":
                    user[0],

                "name":
                    user[1],

                "email":
                    user[2],

            },

        })

    except Exception as e:

        print(
            f"[Server-{PORT}] "
            f"GET /shard2/users/{user_id} error: {e}"
        )

        return jsonify({

            "error":
                "Unable to fetch user",

        }), 500


# ============================================================
# SHARD INFORMATION
#
# GET /shards
# ============================================================

@app.route("/shards", methods=["GET"])
def shards():

    return jsonify({

        "shards": {

            "shard1": {

                "name":
                    "Shard 1",

                "write_database":
                    "5432",

                "read_database":
                    "5434",

                "id_range":
                    "Odd IDs: 1,3,5,7...",

            },

            "shard2": {

                "name":
                    "Shard 2",

                "write_database":
                    "5435",

                "read_database":
                    "5436",

                "id_range":
                    "Even IDs: 2,4,6,8...",

            },

        }

    })


# ============================================================
# ERROR HANDLER - 404
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "error":
            "Endpoint not found",

        "server":
            f"Server-{PORT}",

        "port":
            PORT,

    }), 404


# ============================================================
# ERROR HANDLER - 405
# ============================================================

@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({

        "error":
            "HTTP method not allowed",

        "server":
            f"Server-{PORT}",

        "port":
            PORT,

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