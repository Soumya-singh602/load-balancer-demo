from database.router import get_database_connection


def create_user(name, email):
    connection = get_database_connection("POST")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email)
                VALUES (%s, %s)
                RETURNING id, name, email;
                """,
                (name, email),
            )

            user = cursor.fetchone()
            connection.commit()

            return user

    finally:
        connection.close()


def get_users():
    connection = get_database_connection("GET")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email FROM users ORDER BY id;"
            )

            return cursor.fetchall()

    finally:
        connection.close()


def update_user(user_id, name):
    connection = get_database_connection("PUT")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET name = %s
                WHERE id = %s
                RETURNING id, name, email;
                """,
                (name, user_id),
            )

            user = cursor.fetchone()
            connection.commit()

            return user

    finally:
        connection.close()


def delete_user(user_id):
    connection = get_database_connection("DELETE")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM users
                WHERE id = %s
                RETURNING id, name, email;
                """,
                (user_id,),
            )

            user = cursor.fetchone()
            connection.commit()

            return user

    finally:
        connection.close()