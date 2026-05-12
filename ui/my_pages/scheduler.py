import streamlit as st
import pandas as pd
from datetime import datetime
from db import get_pg_conn, get_pg_engine
from airflow_service import airflow_api

def show_scheduler():
    # -----------------------
    # 🎨 PAGE STYLE (Local Overrides)
    # -----------------------
    st.markdown("""
        <style>
        .dag-card {
            background: rgba(15, 23, 42, 0.8) !important;
            border-radius: 16px !important;
            padding: 28px !important;
            margin-bottom: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            transition: var(--transition) !important;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.3) !important;
        }
        .dag-card:hover {
            border-color: #9FC3CF !important;
            background: rgba(15, 23, 42, 0.95) !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5) !important;
        }
        .status-badge {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-success { background: rgba(52, 211, 153, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
        .status-failed { background: rgba(248, 113, 113, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.2); }
        .status-running { background: rgba(96, 165, 250, 0.1); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.2); }
        .status-paused { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }
        
        .airflow-btn {
            background: #9FC3CF !important;
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # -----------------------
    # ⏰ HEADER
    # -----------------------
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⏰ Airflow Scheduler")
        st.markdown('<p style="color:#94a3b8; margin-top:-20px;">Manage and monitor enterprise ETL orchestrations</p>', unsafe_allow_html=True)
    with col2:
        st.link_button("🚀 Open Airflow UI", "http://localhost:8080", width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------
    # 📊 FETCH AIRFLOW DATA
    # -----------------------
    try:
        with st.spinner("Connecting to orchestration engine..."):
            dags = airflow_api.get_dags()
    except Exception as e:
        st.error(f"⚠️ Connectivity Issue: {e}")
        st.info("💡 **Tip**: Ensure Airflow containers are active and port 8080 is mapped correctly.")
        return

    if not dags:
        st.warning("ℹ️ No active pipelines found in the orchestration engine.")
        return

    # -----------------------
    # 📈 METRICS
    # -----------------------
    total_dags = len(dags)
    active_dags = sum(1 for d in dags if not d.get("is_paused"))
    paused_dags = total_dags - active_dags

    m1, m2, m3 = st.columns(3)
    
    # Total Pipelines KPI
    m1.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Pipelines</div>
            <div class="kpi-value" style="color: #ffffff;">{total_dags}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Orchestrated assets</div>
        </div>
    """, unsafe_allow_html=True)

    # Active KPI
    m2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active</div>
            <div class="kpi-value" style="color: #60a5fa;">{active_dags}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Scheduled runs</div>
        </div>
    """, unsafe_allow_html=True)

    # Paused KPI
    m3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Paused</div>
            <div class="kpi-value" style="color: #94a3b8;">{paused_dags}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:8px; font-weight:500;">Disabled pipelines</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Pipeline Orchestration")

    # -----------------------
    # 🗂️ DAG CARDS
    # -----------------------
    for dag in dags:
        dag_id = dag["dag_id"]
        is_paused = dag["is_paused"]
        
        last_run = airflow_api.get_last_run(dag_id)
        last_status = last_run["state"] if last_run else "no_runs"
        last_run_time = last_run["execution_date"] if last_run else "Never"
        
        if last_run_time != "Never":
            try:
                dt = datetime.fromisoformat(last_run_time.replace("Z", "+00:00"))
                last_run_time = dt.strftime("%b %d, %H:%M")
            except: pass

        next_run = dag.get("next_dagrun_data_interval_start", "N/A")
        if next_run and next_run != "N/A":
            try:
                dt = datetime.fromisoformat(next_run.replace("Z", "+00:00"))
                next_run = dt.strftime("%b %d, %H:%M")
            except: pass

        status_cls = f"status-{last_status}" if last_status in ["success", "failed", "running"] else "status-paused"
        
        # Card Layout
        st.markdown(f"""
            <div class="dag-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h3 style="margin:0; font-size:18px;">{dag_id}</h3>
                        <p style="color:#64748b; font-size:13px; margin:4px 0 0 0;">Schedule: {dag.get('schedule_interval', {}).get('value', 'Manual')}</p>
                    </div>
                    <div class="status-badge {status_cls}">{last_status}</div>
                </div>
                <div style="display:flex; gap:40px; margin-top:20px;">
                    <div>
                        <small style="color:#64748b; text-transform:uppercase; font-size:10px; font-weight:700;">Last Run</small>
                        <div style="font-size:14px; font-weight:500;">{last_run_time}</div>
                    </div>
                    <div>
                        <small style="color:#64748b; text-transform:uppercase; font-size:10px; font-weight:700;">Next Scheduled</small>
                        <div style="font-size:14px; font-weight:500;">{next_run}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Actions Overlay
        action_col1, action_col2, _ = st.columns([0.1, 0.1, 1])
        with action_col1:
            state_label = "▶️" if is_paused else "⏸️"
            if st.button(state_label, key=f"state_{dag_id}", help="Pause/Resume Pipeline"):
                if airflow_api.update_dag_state(dag_id, not is_paused):
                    st.rerun()
        with action_col2:
            if st.button("🚀", key=f"run_{dag_id}", help="Trigger Pipeline Now"):
                success, msg = airflow_api.trigger_dag(dag_id)
                if success: st.toast(f"Pipeline {dag_id} triggered successfully!")
                else: st.error(msg)

    # -----------------------
    # 📋 AUDIT LOGS
    # -----------------------
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 Framework Audit Logs (Database)"):
        engine = get_pg_engine()
        try:
            query = "SELECT * FROM dyn_etl.process_control_details ORDER BY pipeline_starttime DESC LIMIT 10"
            df_history = pd.read_sql(query, engine)
            st.dataframe(df_history, width='stretch', hide_index=True)
        except Exception as e:
            st.error(f"Error fetching execution history: {e}")

    if st.button("🔄 Refresh Dashboard", width='stretch'):
        st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Audit Logs (Reset IDs)", type="secondary", help="Truncates the audit log table and resets identity sequence to 1"):
        from target_loader import truncate_table
        try:
            engine = get_pg_engine()
            # Framework audit log table
            audit_config = {'target_table_name': 'process_control_details', 'target_schema': 'dyn_etl'}
            truncate_table(engine, audit_config, restart_identity=True)
            engine.dispose()
            st.toast("✅ Audit logs cleared and sequence reset!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to clear logs: {e}")