from db import get_pg_conn

def get_active_configs():
    conn = get_pg_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            id,
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
            load_type
        FROM dyn_etl.process_control
        WHERE is_active = true
    """)

    cols = [desc[0] for desc in cur.description]

    configs = []
    for row in cur.fetchall():
        config = dict(zip(cols, row))

        # 🔹 Normalize values (IMPORTANT)
        config["source_system"] = config["source_system"].upper()
        config["target_system"] = config["target_system"].upper()

        configs.append(config)

    conn.close()

    print("🔍 Active Configs Loaded:")
    for c in configs:
        print(c)

    return configs