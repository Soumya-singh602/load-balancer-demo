import os

import psycopg2

from dotenv import load_dotenv


load_dotenv()


REPLICA_DB_CONFIG = {

    "host": os.getenv("REPLICA_DB_HOST"),

    "port": os.getenv("REPLICA_DB_PORT"),

    "database": os.getenv("REPLICA_DB_NAME"),

    "user": os.getenv("REPLICA_DB_USER"),

    "password": os.getenv("REPLICA_DB_PASSWORD"),

}


def get_replica_connection():

    return psycopg2.connect(**REPLICA_DB_CONFIG)