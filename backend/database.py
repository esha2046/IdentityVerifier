import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def run_query(query, params=None):
    conn = connect_db()
    if not conn:
        return None, "Connection failed"
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        # Check if we need to return data or just commit
        if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
            if 'LIMIT 1' in query.upper() or query.count('WHERE') == 1 and 'anchor_id = %s' in query:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.fetchone() if 'RETURNING' in query.upper() else None
        
        cursor.close()
        conn.close()
        return result, None
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return None, str(e)