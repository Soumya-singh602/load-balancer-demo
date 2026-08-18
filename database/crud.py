from database.router import get_database_connection

from database.shard_router import (
    get_shard_id_from_email,
    get_shard_primary_connection,
    get_shard_replica_connection,
)


SHARDS = [1, 2]


# ============================================================
# CREATE USER
# WRITE → SHARD PRIMARY
# ============================================================

def create_user(name, email):

    shard_id = get_shard_id_from_email(email)

    connection = get_shard_primary_connection(shard_id)

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


# ============================================================
# GET ALL USERS
# READ → ALL SHARD REPLICAS
# ============================================================

def get_users():

    all_users = []

    for shard_id in SHARDS:

        connection = get_shard_replica_connection(shard_id)

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, name, email
                    FROM users
                    ORDER BY id;
                    """
                )

                users = cursor.fetchall()

                all_users.extend(users)

        finally:

            connection.close()

    return sorted(all_users, key=lambda user: user[0])


# ============================================================
# GET SINGLE USER
# READ → SEARCH ALL SHARD REPLICAS
# ============================================================

def get_user(user_id):

    for shard_id in SHARDS:

        connection = get_shard_replica_connection(shard_id)

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, name, email
                    FROM users
                    WHERE id = %s;
                    """,
                    (user_id,),
                )

                user = cursor.fetchone()

                if user is not None:
                    return user

        finally:

            connection.close()

    return None


# ============================================================
# SEARCH USERS
# READ → ALL SHARD REPLICAS
# ============================================================

def search_users(search_term):

    all_users = []

    for shard_id in SHARDS:

        connection = get_shard_replica_connection(shard_id)

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, name, email
                    FROM users
                    WHERE name ILIKE %s
                       OR email ILIKE %s
                    ORDER BY id;
                    """,
                    (
                        f"%{search_term}%",
                        f"%{search_term}%",
                    ),
                )

                users = cursor.fetchall()

                all_users.extend(users)

        finally:

            connection.close()

    return sorted(all_users, key=lambda user: user[0])


# ============================================================
# COUNT USERS
# READ → ALL SHARD REPLICAS
# ============================================================

def count_users():

    total = 0

    for shard_id in SHARDS:

        connection = get_shard_replica_connection(shard_id)

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM users;
                    """
                )

                total += cursor.fetchone()[0]

        finally:

            connection.close()

    return total


# ============================================================
# FIND USER SHARD
# INTERNAL HELPER
# ============================================================

def find_user_shard(user_id):

    for shard_id in SHARDS:

        connection = get_shard_replica_connection(shard_id)

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, name, email
                    FROM users
                    WHERE id = %s;
                    """,
                    (user_id,),
                )

                user = cursor.fetchone()

                if user is not None:
                    return shard_id, user

        finally:

            connection.close()

    return None, None


# ============================================================
# UPDATE USER
# FIND SHARD → WRITE TO THAT SHARD PRIMARY
# ============================================================

def update_user(user_id, name):

    shard_id, user = find_user_shard(user_id)

    if user is None:
        return None

    connection = get_shard_primary_connection(shard_id)

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

            updated_user = cursor.fetchone()

            connection.commit()

            return updated_user

    finally:

        connection.close()


# ============================================================
# DELETE USER
# FIND SHARD → DELETE FROM THAT SHARD PRIMARY
# ============================================================

def delete_user(user_id):

    shard_id, user = find_user_shard(user_id)

    if user is None:
        return None

    connection = get_shard_primary_connection(shard_id)

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

            deleted_user = cursor.fetchone()

            connection.commit()

            return deleted_user

    finally:

        connection.close()