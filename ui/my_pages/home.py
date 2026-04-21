import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import get_pg_conn

def show_home():

    st.header("🏠 Dashboard")

    conn = get_pg_conn()
    cur = conn.cursor()

    # Total pipelines
    cur.execute("SELECT COUNT(*) FROM dyn_etl.process_control")
    total = cur.fetchone()[0]

    # Failed pipelines
    cur.execute("""
        SELECT COUNT(*) 
        FROM dyn_etl.process_control_details
        WHERE status = 'FAILED'
    """)
    failed = cur.fetchone()[0]

    # Success pipelines
    cur.execute("""
        SELECT COUNT(*) 
        FROM dyn_etl.process_control_details
        WHERE status = 'SUCCESS'
    """)
    success = cur.fetchone()[0]

    conn.close()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pipelines", total)
    col2.metric("Success Runs", success)
    col3.metric("Failed Runs", failed)