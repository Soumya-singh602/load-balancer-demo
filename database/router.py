from database.primary import get_primary_connection
from database.replica import get_replica_connection


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def get_database_connection(method):
    method = method.upper()

    if method in WRITE_METHODS:
        return get_primary_connection()

    return get_replica_connection()