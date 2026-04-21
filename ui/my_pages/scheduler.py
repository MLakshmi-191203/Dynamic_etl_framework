import streamlit as st
from db import get_pg_conn

def show_scheduler():

    st.header("⏱️Logs")

    conn = get_pg_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT source_table, status, pipeline_start, pipeline_end
        FROM dyn_etl.process_control_details
        ORDER BY pipeline_start DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    st.dataframe(rows)

    conn.close()