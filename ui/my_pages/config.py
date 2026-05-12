import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2
import mysql.connector
from db import get_pg_conn, get_pg_engine

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
    if not row: return None
    return {
        "system": row[0], "host": row[1], "port": row[2], "database": row[3],
        "username": row[4], "password": row[5], "file_path": row[6]
    }

def get_schemas(conn_details):
    if not conn_details: return []
    try:
        if conn_details["system"] == "POSTGRES":
            conn = psycopg2.connect(
                host=conn_details["host"], port=conn_details["port"],
                database=conn_details["database"], user=conn_details["username"], password=conn_details["password"]
            )
            cur = conn.cursor()
            cur.execute("SELECT schema_name FROM information_schema.schemata")
            schemas = [r[0] for r in cur.fetchall()]
            conn.close()
            return schemas
        elif conn_details["system"] == "MYSQL":
            conn = mysql.connector.connect(
                host=conn_details["host"], port=conn_details["port"],
                database=conn_details["database"], user=conn_details["username"], password=conn_details["password"]
            )
            cur = conn.cursor()
            cur.execute("SHOW DATABASES")
            schemas = [r[0] for r in cur.fetchall()]
            conn.close()
            return schemas
    except: return []

def get_pipeline_details(proc_name):
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM dyn_etl.process_control WHERE process_name = %s", (proc_name,))
    columns = [desc[0] for desc in cur.description]
    row = cur.fetchone()
    conn.close()
    if not row: return None
    return dict(zip(columns, row))

def show_config():
    # -----------------------
    # 🎨 HEADER
    # -----------------------
    st.title("⚙️ Framework Configuration")
    st.markdown('<p style="color:#94a3b8; margin-top:-20px;">Manage enterprise connections and pipeline parameters</p>', unsafe_allow_html=True)

    # Drift Notification
    try:
        engine = get_pg_engine()
        df_drift = pd.read_sql("SELECT DISTINCT source_table_name FROM dyn_etl.metadata WHERE change_event IS NOT NULL", engine)
        engine.dispose()
        if not df_drift.empty:
            st.warning(f"🚨 **Schema Drift Detected**: Changes found in metadata. Please review in the **Metadata** tab.")
    except: pass

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔌 Connection Management", "📋 Pipeline Definitions"])

    # -----------------------
    # 🔌 CONNECTIONS
    # -----------------------
    with tab1:
        st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:24px; border:1px solid rgba(255, 255, 255, 0.05); margin-bottom:25px;">
                <h3 style="margin:0;">Manage Data Sources</h3>
                <p style="color:#94a3b8; font-size:14px; margin-top:5px;">Configure credentials for source and target systems</p>
            </div>
        """, unsafe_allow_html=True)

        engine = get_pg_engine()
        df_conns = pd.read_sql("SELECT connection_name FROM dyn_etl.connection_parameters", engine)
        engine.dispose()

        conn_options = ["-- New Connection --"] + df_conns['connection_name'].tolist()
        selected_conn = st.selectbox("Select Connection to Edit", conn_options)

        edit_mode = selected_conn != "-- New Connection --"
        existing_data = get_connection_details(selected_conn) if edit_mode else None

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                conn_name = st.text_input("Connection Name", value=selected_conn if edit_mode else "", disabled=edit_mode)
                system = st.selectbox("System Type", ["POSTGRES", "MYSQL", "CSV", "SQLITE", "SQL_SERVER"], 
                                      index=["POSTGRES", "MYSQL", "CSV", "SQLITE", "SQL_SERVER"].index(existing_data["system"]) if edit_mode else 0)
                host = st.text_input("Host", value=existing_data["host"] or "" if edit_mode else "")
                port = st.text_input("Port", value=str(existing_data["port"]) if edit_mode and existing_data["port"] else "")

            with col2:
                db = st.text_input("Database", value=existing_data["database"] or "" if edit_mode else "")
                user = st.text_input("Username", value=existing_data["username"] or "" if edit_mode else "")
                pwd = st.text_input("Password", type="password", value=existing_data["password"] or "" if edit_mode else "")
                file_path = st.text_input("File Path (CSV only)", value=existing_data["file_path"] or "" if edit_mode else "")

        btn_label = "Update Connection" if edit_mode else "💾 Save Connection"
        if st.button(btn_label, width='stretch'):
            try:
                conn = get_pg_conn()
                cur = conn.cursor()
                port_value = int(port) if port.strip() else None
                if system in ["CSV", "SQLITE"]: host, port_value, db, user, pwd = None, None, None, None, None
                if edit_mode:
                    cur.execute("""
                        UPDATE dyn_etl.connection_parameters
                        SET source_system=%s, host=%s, port=%s, database_name=%s, username=%s, password=%s, file_path=%s
                        WHERE connection_name=%s
                    """, (system, host or None, port_value, db or None, user or None, pwd or None, file_path or None, selected_conn))
                    st.toast("✅ Connection Updated")
                else:
                    cur.execute("""
                        INSERT INTO dyn_etl.connection_parameters
                        (connection_name, source_system, host, port, database_name, username, password, file_path)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (conn_name, system, host or None, port_value, db or None, user or None, pwd or None, file_path or None))
                    st.toast("✅ Connection Saved")
                conn.commit()
                conn.close()
                st.rerun()
            except Exception as e: st.error(f"❌ {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Inventory of Connections")
        engine = get_pg_engine()
        df = pd.read_sql("SELECT connection_name, source_system, host, database_name FROM dyn_etl.connection_parameters", engine)
        st.dataframe(df, width="stretch", hide_index=True)
        engine.dispose()

    # -----------------------
    # 📋 PIPELINES
    # -----------------------
    with tab2:
        st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:24px; border:1px solid rgba(255, 255, 255, 0.05); margin-bottom:25px;">
                <h3 style="margin:0;">Pipeline Definitions</h3>
                <p style="color:#94a3b8; font-size:14px; margin-top:5px;">Configure source-to-target mapping and load types</p>
            </div>
        """, unsafe_allow_html=True)

        engine = get_pg_engine()
        df_procs = pd.read_sql("SELECT process_name FROM dyn_etl.process_control", engine)
        df_conn = pd.read_sql("SELECT connection_name FROM dyn_etl.connection_parameters", engine)
        engine.dispose()

        if df_conn.empty:
            st.warning("⚠️ Please create a connection first.")
            return

        proc_options = ["-- New Pipeline --"] + df_procs['process_name'].tolist()
        selected_proc = st.selectbox("Select Pipeline to Edit", proc_options)
        edit_p_mode = selected_proc != "-- New Pipeline --"
        p_data = get_pipeline_details(selected_proc) if edit_p_mode else None
        conn_list = df_conn["connection_name"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            process_name = st.text_input("Process Name *", value=selected_proc if edit_p_mode else "", disabled=edit_p_mode)
            source_conn = st.selectbox("Source Connection", conn_list, 
                                       index=conn_list.index(p_data["source_connection_name"]) if edit_p_mode and p_data["source_connection_name"] in conn_list else 0)
            src_details = get_connection_details(source_conn)
            source_database = st.text_input("Source Database", value=src_details["database"] if src_details else "", disabled=True)
            s_schemas = get_schemas(src_details) or ["N/A"]
            source_schema = st.selectbox("Source Schema", s_schemas,
                                         index=s_schemas.index(p_data["source_schema"]) if edit_p_mode and p_data["source_schema"] in s_schemas else 0)
            source_table = st.text_input("Source Table *", value=p_data["source_table_name"] if edit_p_mode else "")

        with col2:
            target_conn = st.selectbox("Target Connection", conn_list,
                                       index=conn_list.index(p_data["target_connection_name"]) if edit_p_mode and p_data["target_connection_name"] in conn_list else 0)
            tgt_details = get_connection_details(target_conn)
            target_database = st.text_input("Target Database", value=tgt_details["database"] if tgt_details else "", disabled=True)
            t_schemas = get_schemas(tgt_details) or ["N/A"]
            target_schema = st.selectbox("Target Schema", t_schemas,
                                         index=t_schemas.index(p_data["target_schema"]) if edit_p_mode and p_data["target_schema"] in t_schemas else 0)
            target_table = st.text_input("Target Table *", value=p_data["target_table_name"] if edit_p_mode else "")

        st.markdown("### ⚙️ Operational Settings")
        col3, col4 = st.columns(2)
        with col3:
            primary_key = st.text_input("Primary Key", value=p_data["primary_key"] or "" if edit_p_mode else "")
            load_type = st.selectbox("Load Type", ["FULL", "INCREMENTAL"], 
                                     index=["FULL", "INCREMENTAL"].index(p_data["load_type"]) if edit_p_mode else 0)
            action_type = st.selectbox("Action Type", ["INSERT", "UPSERT", "TRUNCATE"],
                                       index=["INSERT", "UPSERT", "TRUNCATE"].index(p_data["action_type"]) if edit_p_mode else 0)
            condition = st.text_input("Incremental Column", value=p_data["condition"] or "" if edit_p_mode else "")
        with col4:
            run_seq = st.number_input("Run Sequence", 1, 100, int(p_data["run_seq"]) if edit_p_mode else 1)
            frequency = st.selectbox("Frequency", ["MANUAL", "DAILY", "WEEKLY"],
                                     index=["MANUAL", "DAILY", "WEEKLY"].index(p_data["frequency"]) if edit_p_mode else 0)
            active_flag = st.checkbox("Active Pipeline", value=p_data["active_flag"] if edit_p_mode else True)
            restart_identity = st.checkbox("Restart Identity on Truncate", value=p_data.get("restart_identity", True) if edit_p_mode else True)
            admin_email = st.text_input("Admin Email", value=p_data["admin_email"] or "" if edit_p_mode else "")

        p_btn_label = "Update Pipeline" if edit_p_mode else "🚀 Save Pipeline"
        if st.button(p_btn_label, width='stretch'):
            if not process_name or not source_table or not target_table: st.error("❌ Mandatory fields missing")
            else:
                try:
                    conn = get_pg_conn()
                    cur = conn.cursor()
                    if edit_p_mode:
                        cur.execute("""
                            UPDATE dyn_etl.process_control SET
                                source_connection_name=%s, target_connection_name=%s, source_table_name=%s, target_table_name=%s,
                                source_database=%s, source_schema=%s, target_database=%s, target_schema=%s,
                                primary_key=%s, load_type=%s, action_type=%s, condition=%s,
                                run_seq=%s, frequency=%s, active_flag=%s, restart_identity=%s, admin_email=%s, el_updated_date=NOW()
                            WHERE process_name=%s
                        """, (source_conn, target_conn, source_table, target_table, source_database, source_schema, target_database, target_schema,
                              primary_key, load_type, action_type, condition, run_seq, frequency, active_flag, restart_identity, admin_email, selected_proc))
                        st.toast("✅ Pipeline Updated")
                    else:
                        batch_id = datetime.now().strftime("%Y%m%d%H%M%S")
                        cur.execute("""
                            INSERT INTO dyn_etl.process_control (batch_id, process_name, source_connection_name, target_connection_name,
                                source_table_name, target_table_name, source_database, source_schema, target_database, target_schema,
                                primary_key, load_type, action_type, condition, run_seq, frequency, active_flag, restart_identity, admin_email, el_created_date)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                        """, (batch_id, process_name, source_conn, target_conn, source_table, target_table, source_database, source_schema,
                              target_database, target_schema, primary_key, load_type, action_type, condition, run_seq, frequency, active_flag, restart_identity, admin_email))
                        st.toast("✅ Pipeline Created")
                    conn.commit()
                    conn.close()
                    st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Inventory of Pipelines")
        engine = get_pg_engine()
        df = pd.read_sql("SELECT process_name, source_table_name, target_table_name, load_type, active_flag FROM dyn_etl.process_control ORDER BY run_seq", engine)
        st.dataframe(df, width="stretch", hide_index=True)
        engine.dispose()