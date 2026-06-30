# db.py

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = dict(
    host=os.environ["DB_HOST"],
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    port=os.environ.get("DB_PORT", "5432"),
)

# Small pool shared by the Flask app so requests reuse connections instead of
# opening a new one each time (the shared university DB has a tight
# connection cap). minconn=1, maxconn=4 keeps the app's footprint low.
_pool = psycopg2.pool.SimpleConnectionPool(1, 4, **DB_CONFIG)


def get_connection():
    """Borrow a connection from the pool. Caller must call release_connection()."""
    return _pool.getconn()


def release_connection(conn):
    if conn is not None:
        _pool.putconn(conn)
