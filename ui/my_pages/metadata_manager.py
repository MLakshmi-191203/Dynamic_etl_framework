import streamlit as st
import pandas as pd
from db import get_pg_engine
from target_loader import get_connection_details, get_engine_from_details
from schema_evolution import apply_schema_changes

def show_metadata_manager():
    # -----------------------
    # 🎨 HEADER
    # -----------------------
    st.title("🗂️ Metadata Repository")
    st.markdown('<p style="color:#94a3b8; margin-top:-20px;">Manage and approve schema evolutions across all data assets</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:20px; border:1px solid rgba(255, 255, 255, 0.05); margin-bottom:25px;">
            <p style="color:#94a3b8; font-size:14px; margin:0;">
                Review extracted metadata and manage <b>Schema Drift</b>. 
                Switch <code>MTD_TYPE</code> to <b>MANUAL</b> to override primary keys or data types.
            </p>
        </div>
    """, unsafe_allow_html=True)

    engine = get_pg_engine()
    
    # Get list of source tables
    df_tables = pd.read_sql("SELECT DISTINCT source_table_name FROM dyn_etl.metadata", engine)
    tables = df_tables['source_table_name'].tolist()
    
    if not tables:
        st.warning("ℹ️ No metadata assets found. Please execute a pipeline to populate the repository.")
        engine.dispose()
        return

    selected_table = st.selectbox("Search and Select Asset", tables)

    if selected_table:
        # Check for pending changes
        df_pending = pd.read_sql(f"""
            SELECT COUNT(*) FROM dyn_etl.metadata 
            WHERE source_table_name = '{selected_table}' AND change_event IS NOT NULL
        """, engine)
        
        if df_pending.iloc[0,0] > 0:
            st.markdown(f"""
                <div style="background:rgba(234, 179, 8, 0.1); border:1px solid rgba(234, 179, 8, 0.2); border-radius:8px; padding:15px; margin-bottom:20px;">
                    <h4 style="color:#eab308; margin:0;">🚨 Schema Drift Detected</h4>
                    <p style="color:#94a3b8; font-size:13px; margin:5px 0 0 0;">
                        Changes detected for <code>{selected_table}</code>. Review and approve updates before deployment.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        df_meta = pd.read_sql(f"""
            SELECT id, source_column_name, source_data_type, target_column_name, target_data_type, is_primary_key, mtd_type, change_event, change_type, old_target_value
            FROM dyn_etl.metadata 
            WHERE source_table_name = '{selected_table}'
            ORDER BY source_ordinal_position
        """, engine)

        st.subheader(f"Inventory: {selected_table}")
        
        # Use data editor for manual overrides
        edited_df = st.data_editor(
            df_meta,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "source_column_name": st.column_config.TextColumn("Source Column"),
                "target_column_name": "Target Column",
                "source_data_type": "Source Type",
                "target_data_type": "Target Type",
                "is_primary_key": st.column_config.CheckboxColumn("Primary Key", default=False),
                "mtd_type": st.column_config.SelectboxColumn("MTD Type", options=["DYNAMIC", "MANUAL"], required=True, default="MANUAL"),
                "change_event": st.column_config.TextColumn("Change Event"),
                "change_type": st.column_config.TextColumn("Change Type"),
                "old_target_value": st.column_config.TextColumn("Old Value")
            },
            hide_index=True,
            width='stretch',
            num_rows="dynamic"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Deploy Changes & Approve Schema", width='stretch'):
            from sqlalchemy import text
            try:
                # 1. Apply changes to Target System
                df_pc = pd.read_sql(f"SELECT target_connection_name, target_table_name, target_schema FROM dyn_etl.process_control WHERE source_table_name = '{selected_table}'", engine)
                if not df_pc.empty:
                    tgt_config = df_pc.iloc[0].to_dict()
                    tgt_conn_details = get_connection_details(tgt_config['target_connection_name'])
                    tgt_engine = get_engine_from_details(tgt_conn_details)
                    
                    with st.status(f"Deploying schema updates to {tgt_config['target_table_name']}...") as s:
                        apply_schema_changes(tgt_engine, tgt_config, edited_df)
                        s.update(label="✅ Schema Deployment Successful!", state="complete")
                    tgt_engine.dispose()

                # 2. Update Metadata Table
                with engine.begin() as conn:
                    existing_ids = set(df_meta['id'].tolist())
                    edited_ids = set(edited_df['id'].dropna().astype(int).tolist())
                    deleted_ids = existing_ids - edited_ids
                    
                    if deleted_ids:
                        conn.execute(text(f"DELETE FROM dyn_etl.metadata WHERE id IN ({','.join(map(str, deleted_ids))})"))

                    for index, row in edited_df.iterrows():
                        pk_val = 'Y' if row['is_primary_key'] else 'N'
                        if pd.isna(row['id']):
                            conn.execute(
                                text("""
                                INSERT INTO dyn_etl.metadata (source_table_name, source_column_name, source_data_type, target_column_name, target_data_type, is_primary_key, mtd_type, el_created_date_time)
                                VALUES (:stn, :scn, :sdt, :tcn, :tdt, :pk, :mtd, NOW())
                                """), {"stn": selected_table, "scn": row["source_column_name"], "sdt": row["source_data_type"], "tcn": row["target_column_name"], "tdt": row["target_data_type"], "pk": pk_val, "mtd": row["mtd_type"]}
                            )
                        else:
                            conn.execute(
                                text("""
                                UPDATE dyn_etl.metadata 
                                SET target_column_name = :tcn, target_data_type = :tdt, source_column_name = :scn, source_data_type = :sdt, is_primary_key = :pk, mtd_type = :mtd,
                                    change_event = NULL, change_type = NULL, old_target_value = NULL
                                WHERE id = :id
                                """), {"tcn": row["target_column_name"], "tdt": row["target_data_type"], "scn": row["source_column_name"], "sdt": row["source_data_type"], "pk": pk_val, "mtd": row["mtd_type"], "id": int(row["id"])}
                            )
                st.toast("✅ Metadata approved and deployed")
                st.rerun()
            except Exception as e: st.error(f"❌ Deployment failed: {e}")

    engine.dispose()
