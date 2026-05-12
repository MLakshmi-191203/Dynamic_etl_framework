from datetime import datetime


def log_run(
    conn,
    config,
    start_time,
    end_time,
    insert_count,
    update_count,
    reject_count,
    status,
    error_msg
):

    cur = conn.cursor()

    # =========================
    # 🔹 CALCULATIONS
    # =========================
    duration = int((end_time - start_time).total_seconds())

    source_count = insert_count + update_count + reject_count
    success_count = insert_count + update_count

    # =========================
    # 🔹 INSERT AUDIT LOG
    # =========================
    cur.execute("""
        INSERT INTO dyn_etl.process_control_details (
            batch_id,
            process_name,
            pipeline_name,
            load_type,
            action,
            target_table_name,
            run_seq,
            source_in_count,
            success_in_count,
            failed_in_count,
            insert_in_count,
            update_in_count,
            delete_in_count,
            target_in_count,
            run_status,
            sql,
            exec_startdatetime,
            exec_enddatetime,
            exec_duration_in_sec,
            pipeline_starttime,
            pipeline_endtime,
            pipeline_duration_in_sec,
            metadata_starttime,
            metadata_endtime,
            metadata_duration_in_sec,
            file_system_id,
            startdate,
            enddate,
            source_file_name,
            source_file_url,
            created_at
        )
        VALUES (
            %s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,
            %s,%s,
            %s,%s,%s,
            %s,%s,%s,
            %s,%s,%s,
            %s,%s,%s,%s,%s,
            NOW()
        )
    """, (
        config.get("batch_id"),
        config.get("process_name"),
        config.get("process_name"),  # pipeline_name
        config.get("load_type"),
        config.get("action_type"),   # action
        config.get("target_table_name"),
        config.get("run_seq"),

        source_count,
        success_count,
        reject_count,

        insert_count,
        update_count,
        0,  # delete count

        success_count,

        status,
        error_msg,

        start_time,
        end_time,
        duration,

        start_time,
        end_time,
        duration,

        start_time,
        end_time,
        duration,

        None,  # file_system_id
        None,  # startdate
        None,  # enddate
        None,  # source_file_name
        None   # source_file_url
    ))

    conn.commit()