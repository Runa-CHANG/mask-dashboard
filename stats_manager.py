# stats_manager.py
from db_config import get_connection
from datetime import datetime
import psycopg2
import psycopg2.extras
import pandas as pd


def add_history_entry(label):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mask_stats (timestamp, label)
                VALUES (%s, %s)
            """, (now, label))
        conn.commit()

def get_history_dataframe():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM mask_stats ORDER BY timestamp DESC LIMIT 100")
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["timestamp", "label"])



def get_aggregated_stats():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT label, COUNT(*) as count
                FROM mask_stats
                GROUP BY label
            """)
            rows = cur.fetchall()

    result = {
        'Without_Mask': 0,
        'With_Mask': 0,
        'Incorrectly_Worn_Mask': 0,
        'Partially_Worn_Mask': 0
    }
    for row in rows:
        result[row['label']] = row['count']
    return result
