import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_pg_conn
from main import run_pipeline


def show_config():

    st.header("⚙️ Pipeline Configuration")

    conn = get_pg_conn()
    cur = conn.cursor()

    # 🔹 Show existing configs
    cur.execute("SELECT * FROM dyn_etl.process_control")
    rows = cur.fetchall()

    st.subheader("📋 Existing Configs")
    st.dataframe(rows)

    st.subheader("➕ Add New Config")

    # 🔹 Source Config
    source = st.selectbox("Source", ["CSV", "MYSQL"])
    source_db = st.text_input("Source Database")
    source_schema = st.text_input("Source Schema")
    source_table = st.text_input("Source Table")
    file_path = st.text_input("File Path (for CSV)")

    # 🔹 Target Config
    target_db = st.text_input("Target Database", value="etl_db")
    target_schema = st.text_input("Target Schema", value="etl_data")
    target_table = st.text_input("Target Table")

    pk = st.text_input("Primary Key")
    load_type = st.selectbox("Load Type", ["FULL", "INCREMENTAL"])

    if st.button("Save Config"):

        cur.execute("""
            INSERT INTO dyn_etl.process_control (
                source_system,
                source_database,
                source_schema,
                source_table,
                file_path,
                target_system,
                target_database,
                target_schema,
                target_table,
                primary_key,
                load_type,
                is_active
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true)
        """, (
            source,
            source_db,
            source_schema,
            source_table,
            file_path,
            "POSTGRES",
            target_db,
            target_schema,
            target_table,
            pk,
            load_type
        ))

        conn.commit()
        st.success("✅ Config Saved")

        st.rerun()   # ✅ Correct place

    conn.close()

    # 🔹 Run Pipeline
    st.subheader("▶️ Run Pipelines")

    if st.button("Run Now"):
        run_pipeline()
        st.success("✅ Pipelines executed")