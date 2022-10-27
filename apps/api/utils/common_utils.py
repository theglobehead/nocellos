import psycopg2
from loguru import logger
from psycopg2.extensions import connection
from os import environ


class CommonUtils:
    @staticmethod
    def connection() -> connection:
        conn = psycopg2.connect(
            host=environ["DB_HOST"],
            database=environ["DB_NAME"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"],
            port="7595",
        )

        return conn
