import psycopg2


REPLICA_DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5434,
    "database": "loadbalancer_db",
    "user": "postgres",
    "password": "replicater123",
}


def get_replica_connection():
    return psycopg2.connect(**REPLICA_DB_CONFIG)