import pandas as pd
import os
from db import get_pg_conn, get_engine_from_details
from sqlalchemy import create_engine


def get_connection_details(conn_name):

    conn = get_pg_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT source_system, host, port, database_name, username, password, file_path
        FROM dyn_etl.connection_parameters
        WHERE connection_name = %s
    """, (conn_name,))

    row = cur.fetchone()
    conn.close()

    if not row:
        raise Exception(f"Connection not found: {conn_name}")

    return {
        "system": row[0],
        "host": row[1],
        "port": row[2],
        "database": row[3],
        "username": row[4],
        "password": row[5],
        "file_path": row[6]
    }


def load_source(config):
    """
    Generic source loader that handles any system supported by SQLAlchemy.
    """
    conn_details = get_connection_details(config["source_connection_name"])
    system = conn_details["system"].upper()

    # CSV
    if system == "CSV":
        path = conn_details["file_path"]

        if not os.path.exists(path):
            raise Exception(f"File not found: {path}")

        return pd.read_csv(path)

    # Generic DB Load
    try:
        engine = get_engine_from_details(conn_details)
        
        # Determine if we should use schema
        table = config["source_table_name"]
        schema = config.get("source_schema")
        
        if schema and schema != "N/A":
            full_table_name = f"{schema}.{table}"
        else:
            full_table_name = table

        df = pd.read_sql(f"SELECT * FROM {full_table_name}", engine)
        engine.dispose()
        return df

    except Exception as e:
        raise Exception(f"Failed to load source from {system}: {e}")