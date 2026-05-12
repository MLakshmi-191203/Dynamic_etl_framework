import streamlit as st
import pandas as pd
from datetime import datetime
import time
from db import get_pg_engine, get_pg_conn
from airflow_service import airflow_api
from main import run_pipeline

def show_execution():
    # -----------------------
    # 🎨 HEADER SECTION
    # -----------------------
    st.markdown("""
        <div class="header-container">
            <div style="font-size: 40px; background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.2);">🚀</div>
            <div>
                <div class="header-title">Manual Execution Hub</div>
                <div class="header-subtitle">Trigger pipelines and monitor real-time orchestration status</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------
    # ⚡ TRIGGER PANEL
    # -----------------------
    st.markdown('<div class="form-panel">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        engine = get_pg_engine()
        df_procs = pd.read_sql("SELECT process_name, source_table_name, target_table_name, load_type, source_connection_name, target_connection_name FROM dyn_etl.process_control WHERE active_flag = TRUE", engine)
        df_conns = pd.read_sql("SELECT connection_name FROM dyn_etl.connection_parameters", engine)
        engine.dispose()
        
        proc_list = df_procs['process_name'].tolist()
        conn_list = df_conns['connection_name'].tolist()
        
        selected_proc = st.selectbox("Select Pipeline to Execute *", proc_list, placeholder="Choose a pipeline...")
        
        # Advanced Overrides
        with st.expander("⚙️ Execution Overrides (Advanced)"):
            c1, c2 = st.columns(2)
            with c1:
                src_override = st.selectbox("Override Source Connection", ["Current"] + conn_list)
                env_override = st.selectbox("Target Environment", ["Development", "Staging", "Production"])
            with c2:
                tgt_override = st.selectbox("Override Target Connection", ["Current"] + conn_list)
                sched_type = st.selectbox("Execution Type", ["Manual Run", "One-Time Run", "Immediate Execution"])

        # Details of selected pipeline
        details = df_procs[df_procs['process_name'] == selected_proc].iloc[0] if selected_proc else None
        if details is not None:
            st.markdown(f"""
                <div style="background: rgba(148, 163, 184, 0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #3b82f6; margin-top: 15px;">
                    <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Pipeline Metadata</div>
                    <div style="display: flex; gap: 20px; margin-top: 8px;">
                        <div><span style="color: #94a3b8;">Source:</span> <b style="color: white;">{details['source_table_name']}</b></div>
                        <div><span style="color: #94a3b8;">Target:</span> <b style="color: white;">{details['target_table_name']}</b></div>
                        <div><span style="color: #94a3b8;">Load:</span> <b style="color: white;">{details['load_type']}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        exec_mode = st.radio("Execution Mode", ["Airflow (Cloud)", "Direct (Local)"], index=0)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Trigger Execution", use_container_width=True):
            if selected_proc:
                with st.spinner(f"Initiating {selected_proc}..."):
                    if exec_mode == "Airflow (Cloud)":
                        success, info = airflow_api.trigger_dag(selected_proc)
                        if success:
                            st.toast(f"✅ DAG {selected_proc} triggered in Airflow")
                        else:
                            st.error(f"❌ Airflow error: {info}")
                    else:
                        # Direct local run (might be slow for UI, but good for demo)
                        try:
                            run_pipeline(selected_proc)
                            st.toast(f"✅ Local execution completed for {selected_proc}")
                        except Exception as e:
                            st.error(f"❌ Execution failed: {e}")
            else:
                st.warning("Please select a pipeline first.")

    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------
    # 🛠️ ACTION BUTTONS
    # -----------------------
    st.markdown("<br>", unsafe_allow_html=True)
    if selected_proc:
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            if st.button("⏸️ Pause Schedule", use_container_width=True):
                if airflow_api.update_dag_state(selected_proc, True): st.toast("Pipeline Paused")
        with col_a2:
            if st.button("▶️ Resume Schedule", use_container_width=True):
                if airflow_api.update_dag_state(selected_proc, False): st.toast("Pipeline Resumed")
        with col_a3:
            if st.button("🔄 Retry Failed", use_container_width=True):
                # Logic to retry (usually just trigger again in Airflow)
                airflow_api.trigger_dag(selected_proc)
                st.toast("Retry triggered")
        with col_a4:
            if st.button("📜 View Logs", use_container_width=True):
                st.info("Log streaming initialized... (Mocking live logs)")
                st.code(f"INFO: Starting pipeline {selected_proc}...\nINFO: Connecting to source...\nINFO: Fetched 4500 records.\nSUCCESS: Load complete.", language="bash")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # -----------------------
    # 📊 MONITORING SECTION
    # -----------------------
    st.subheader("📡 Real-time Monitoring")
    
    # Airflow DAG Runs
    try:
        dags = airflow_api.get_dags()
        active_dags = [d for d in dags if d['dag_id'] in proc_list]
        
        if active_dags:
            monitoring_data = []
            for dag in active_dags:
                last_run = airflow_api.get_last_run(dag['dag_id'])
                if last_run:
                    state = last_run.get('state', 'unknown').upper()
                    state_color = "#34d399" if state == "SUCCESS" else "#f87171" if state == "FAILED" else "#60a5fa"
                    monitoring_data.append({
                        "Pipeline": dag['dag_id'],
                        "Status": state,
                        "Start Time": last_run.get('start_date'),
                        "End Time": last_run.get('end_date'),
                        "Is Paused": dag.get('is_paused')
                    })
            
            if monitoring_data:
                df_mon = pd.DataFrame(monitoring_data)
                # Display custom monitoring cards
                cols = st.columns(3)
                for i, row in enumerate(monitoring_data[:3]): # Show top 3
                    with cols[i]:
                        st.markdown(f"""
                            <div class="form-panel" style="padding: 20px; border-top: 4px solid {'#34d399' if row['Status'] == 'SUCCESS' else '#f87171' if row['Status'] == 'FAILED' else '#60a5fa'};">
                                <div style="font-weight: 700; color: white;">{row['Pipeline']}</div>
                                <div style="font-size: 24px; font-weight: 800; color: white; margin: 10px 0;">{row['Status']}</div>
                                <div style="font-size: 11px; color: #94a3b8;">Started: {row['Start Time']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_mon, use_container_width=True, hide_index=True)
    except:
        st.info("ℹ️ Airflow monitoring unavailable. Showing local audit logs below.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝 Recent Execution History (Audit Logs)"):
        engine = get_pg_engine()
        df_history = pd.read_sql("""
            SELECT process_name, pipeline_starttime, run_status as status, insert_in_count as inserted, update_in_count as updated, sql as error 
            FROM dyn_etl.process_control_details 
            ORDER BY pipeline_starttime DESC LIMIT 10
        """, engine)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        engine.dispose()
