import sys
import os
sys.path.append(os.getcwd())
import psycopg2
from db import get_pg_conn

try:
    conn = psycopg2.connect(
        host="localhost",
        database="etl_db",
        user="postgres",
        password="Lakshmi@2000"
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Connection successful")
    cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'dyn_etl'")
    if cur.fetchone():
        print("Schema 'dyn_etl' exists")
    else:
        print("Schema 'dyn_etl' DOES NOT exist")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
