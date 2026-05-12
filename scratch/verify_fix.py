import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
import psycopg2
from db import get_pg_engine

try:
    print("Testing direct psycopg2 connection...")
    conn = psycopg2.connect(
        host="localhost",
        database="etl_db",
        user="postgres",
        password="Postgre@2000"
    )
    print("Direct psycopg2 connection successful!")
    conn.close()

    print("Testing SQLAlchemy connection via db.py engine...")
    engine = get_pg_engine()
    
    # Correctly replace host in the URL object
    new_url = engine.url.set(host="localhost")
    print(f"Testing with URL: {new_url.render_as_string(hide_password=True)}")
    
    from sqlalchemy import create_engine
    test_engine = create_engine(new_url)
    
    df = pd.read_sql("""
    SELECT process_name
    FROM dyn_etl.process_control
    WHERE active_flag = TRUE
    """, test_engine)
    
    print("Successfully fetched active processes:")
    print(df)
    test_engine.dispose()
except Exception as e:
    print(f"Verification failed: {e}")
