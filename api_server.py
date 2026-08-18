from flask import Flask, jsonify, request

from database.crud import (
    create_user,
    get_users,
    update_user,
    delete_user,
)

app = Flask(__name__)


@app.route("/users", methods=["GET"])
def users_list():

    users = get_users()

    return jsonify({
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


@app.route("/users", methods=["POST"])
def users_create():

    data = request.get_json()

    user = create_user(
        data["name"],
        data["email"],
    )

    return jsonify({
        "database": "primary",
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    }), 201


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
        "database": "primary",
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    })


@app.route("/users/<int:user_id>", methods=["DELETE"])
def users_delete(user_id):

    user = delete_user(user_id)

    if user is None:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "database": "primary",
        "deleted_user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
        },
    })


if __name__ == "__main__":

    print("Database API running on http://127.0.0.1:8000")

    app.run(
        host="127.0.0.1",
        port=8000,
        threaded=True,
    )