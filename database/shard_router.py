from database.primary import get_primary_connection
from database.replica import get_replica_connection

from database.shard2_primary import get_shard2_primary_connection
from database.shard2_replica import get_shard2_replica_connection


def get_shard_primary_connection(shard_id):

    if shard_id == 1:
        return get_primary_connection()

    if shard_id == 2:
        return get_shard2_primary_connection()

    raise ValueError(f"Invalid shard ID: {shard_id}")


def get_shard_replica_connection(shard_id):

    if shard_id == 1:
        return get_replica_connection()

    if shard_id == 2:
        return get_shard2_replica_connection()

    raise ValueError(f"Invalid shard ID: {shard_id}")


def get_shard_id(user_id):

    if user_id % 2 == 0:
        return 1

    return 2

def get_shard_id_from_email(email):

    if hash(email) % 2 == 0:
        return 1

    return 2