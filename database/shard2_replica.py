import os

import psycopg2

from dotenv import load_dotenv


load_dotenv()


SHARD2_REPLICA_DB_CONFIG = {

    "host": os.getenv("SHARD2_REPLICA_DB_HOST"),

    "port": os.getenv("SHARD2_REPLICA_DB_PORT"),

    "database": os.getenv("SHARD2_REPLICA_DB_NAME"),

    "user": os.getenv("SHARD2_REPLICA_DB_USER"),

    "password": os.getenv("SHARD2_REPLICA_DB_PASSWORD"),

}


def get_shard2_replica_connection():

    return psycopg2.connect(**SHARD2_REPLICA_DB_CONFIG)