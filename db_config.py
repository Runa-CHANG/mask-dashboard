# db_config.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_connection():
    return psycopg2.connect(
        dbname="mask_stats",
        user="mask_user",
        password="xZSEGWCTnUZVpVQr5p1k74dO5CUC9lZL",
        host="dpg-cvu667pr0fns73e595ug-a.oregon-postgres.render.com",
        port="5432"
    )