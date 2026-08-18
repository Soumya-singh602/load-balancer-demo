import psycopg2


PRIMARY_DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "loadbalancer_db",
    "user": "postgres",
    "password": "replicater123",
}


def get_primary_connection():
    return psycopg2.connect(**PRIMARY_DB_CONFIG)