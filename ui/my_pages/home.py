import streamlit as st
import pandas as pd
from db import get_pg_conn, get_pg_engine

def show_home():
    # -----------------------
    # 🎨 HEADER
    # -----------------------
    st.title("🚀 ETL Orchestration Dashboard")
    st.markdown('<p style="color:#94a3b8; margin-top:-20px; font-size:18px;">Welcome to the Data Drive Enterprise Management Portal</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------
    # 📊 KEY METRICS (KPI Cards)
    # -----------------------
    conn = get_pg_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT SUM(INSERT_IN_COUNT + UPDATE_IN_COUNT) FROM dyn_etl.process_control_details")
        total_records = cur.fetchone()[0] or 0
        cur.execute("SELECT SUM(FAILED_IN_COUNT) FROM dyn_etl.process_control_details")
        total_failed = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM dyn_etl.process_config_details WHERE ACTIVE_FLAG = 'Y'")
        active_configs = cur.fetchone()[0] or 0
    except:
        total_records = total_failed = active_configs = 0
    finally:
        cur.close()
        conn.close()

    m1, m2, m3 = st.columns(3)
    
    # Processed KPI
    m1.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Processed</div>
            <div class="kpi-value" style="color: #9FC3CF;">{total_records:,}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Total records ingested</div>
        </div>
    """, unsafe_allow_html=True)

    # Failed KPI
    m2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Failed</div>
            <div class="kpi-value" style="color: #f87171;">{total_failed:,}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Exceptions detected</div>
        </div>
    """, unsafe_allow_html=True)

    # Active KPI
    m3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Pipelines</div>
            <div class="kpi-value" style="color: #60a5fa;">{active_configs}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Running orchestration jobs</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------
    # 📋 CONTENT SECTIONS
    # -----------------------
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:24px; border:1px solid rgba(255, 255, 255, 0.05);">
                <h3 style="margin:0;">🛠️ Framework Overview</h3>
                <p style="color:#94a3b8; font-size:14px; line-height:1.6; margin-top:15px;">
                    The Dynamic ETL Framework provides a self-service metadata-driven orchestration layer. 
                    Manage connection strings, define schema evolutions, and monitor pipeline health from a single interface.
                </p>
                <ul style="color:#f8fafc; font-size:14px; margin-top:10px;">
                    <li>Auto-Schema Drift Detection</li>
                    <li>AI-Powered Query Assistance</li>
                    <li>Airflow Integration</li>
                    <li>Real-time Process Monitoring</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:24px; border:1px solid rgba(255, 255, 255, 0.05);">
                <h3 style="margin:0;">📌 Recent Activities</h3>
                <p style="color:#94a3b8; font-size:14px; line-height:1.6; margin-top:15px;">
                    Monitor the latest pipeline executions and metadata changes directly from the audit logs.
                </p>
                <div style="background:rgba(15, 23, 42, 0.4); border-radius:8px; padding:12px; margin-top:10px; border-left:3px solid #9FC3CF;">
                    <small style="color:#64748b;">LATEST EXECUTION</small>
                    <div style="font-size:14px; font-weight:500;">Schema Refresh: sales_db → staging_area</div>
                    <div style="font-size:12px; color:#34d399;">Success (2.4s)</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Pipeline Configuration Overview")

    # Show a small preview table
    from db import get_pg_engine
    engine = get_pg_engine()
    try:
        query = "SELECT PROCESS_NAME, SOURCE_SYSTEM, TARGET_TABLE, ACTIVE_FLAG FROM dyn_etl.process_config_details LIMIT 5"
        df = pd.read_sql(query, engine)
        st.dataframe(df, width='stretch', hide_index=True)
    except:
        st.info("No pipeline configurations found yet.")