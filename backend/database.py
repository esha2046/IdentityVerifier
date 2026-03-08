import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG, DATABASE_URL

def get_connection():
    try:
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def execute_query(query, params=None, fetchone=False, commit=False):
    conn = get_connection()
    if not conn:
        return None, "Database connection failed"
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        result = None
        if fetchone:
            result = cur.fetchone()
        elif not commit:
            result = cur.fetchall()
        if commit:
            conn.commit()
            if not result:
                result = cur.fetchone() if 'RETURNING' in query else None
        cur.close()
        conn.close()
        return result, None
    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)