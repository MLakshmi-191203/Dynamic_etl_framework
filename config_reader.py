from db import get_pg_conn


def get_active_configs(process_name=None):

    conn = get_pg_conn()
    cur = conn.cursor()

    if process_name:
        cur.execute("""
            SELECT *
            FROM dyn_etl.process_control
            WHERE process_name=%s AND active_flag='Y'
        """, (process_name,))
    else:
        cur.execute("""
            SELECT *
            FROM dyn_etl.process_control
            WHERE active_flag='Y'
        """)

    cols = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    conn.close()

    return [dict(zip(cols, row)) for row in rows]