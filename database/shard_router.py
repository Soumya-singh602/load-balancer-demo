from database.primary import get_primary_connection
from database.replica import get_replica_connection

from database.shard2_primary import get_shard2_primary_connection
from database.shard2_replica import get_shard2_replica_connection


# ============================================================
# SHARD PRIMARY CONNECTION
# ============================================================

def get_shard_primary_connection(shard_id):

    if shard_id == 1:
        return get_primary_connection()

    if shard_id == 2:
        return get_shard2_primary_connection()

    raise ValueError(f"Invalid shard ID: {shard_id}")


# ============================================================
# SHARD REPLICA CONNECTION
# ============================================================

def get_shard_replica_connection(shard_id):

    if shard_id == 1:
        return get_replica_connection()

    if shard_id == 2:
        return get_shard2_replica_connection()

    raise ValueError(f"Invalid shard ID: {shard_id}")


# ============================================================
# GLOBAL USER ID → SHARD ROUTING
#
# SHARD 1 → ODD IDs
# SHARD 2 → EVEN IDs
#
# Example:
#
# 1  → Shard 1
# 2  → Shard 2
# 3  → Shard 1
# 4  → Shard 2
# 5  → Shard 1
# 6  → Shard 2
# ============================================================

def get_shard_id(user_id):

    if user_id <= 0:
        raise ValueError("Invalid user ID")

    if user_id % 2 == 1:
        return 1

    return 2


# ============================================================
# EMAIL → SHARD ROUTING
#
# Used during CREATE USER.
#
# This decides where the new user will be created.
# ============================================================

def get_shard_id_from_email(email):

    if not email:
        raise ValueError("Email is required")

    email = email.strip().lower()

    # Stable deterministic routing.
    # Do NOT use Python's hash() because its result
    # can change between different Python processes.

    total = sum(ord(char) for char in email)

    if total % 2 == 0:
        return 1

    return 2