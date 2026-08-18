import os

import psycopg2

from dotenv import load_dotenv


load_dotenv()


PRIMARY_DB_CONFIG = {

    "host": os.getenv("PRIMARY_DB_HOST"),

    "port": os.getenv("PRIMARY_DB_PORT"),

    "database": os.getenv("PRIMARY_DB_NAME"),

    "user": os.getenv("PRIMARY_DB_USER"),

    "password": os.getenv("PRIMARY_DB_PASSWORD"),

}


def get_primary_connection():

    return psycopg2.connect(**PRIMARY_DB_CONFIG)