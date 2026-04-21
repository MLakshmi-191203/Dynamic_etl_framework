def log_run(
    conn,
    config,
    start_time,
    end_time,
    insert_count,
    update_count,
    reject_count,
    status,
    error_message
):

    cur = conn.cursor()

    query = """
    INSERT INTO dyn_etl.process_control_details (
        source_system,
        source_table,
        target_system,
        target_table,
        pipeline_start,
        pipeline_end,
        insert_count,
        update_count,
        reject_count,
        status,
        error_message
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        config["source_system"],
        config["source_table"],
        config["target_system"],
        config["target_table"],
        start_time,
        end_time,
        insert_count,
        update_count,
        reject_count,
        status,
        error_message
    ))

    conn.commit()