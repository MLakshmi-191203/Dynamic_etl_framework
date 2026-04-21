# schema_engine.py

# =========================
# 🔹 CSV SCHEMA EXTRACTOR
# =========================
def get_csv_schema(df):

    schema = []

    for i, col in enumerate(df.columns):
        schema.append({
            "column_name": col.lower(),
            "ordinal_position": i + 1,
            "data_type": str(df[col].dtype)
        })

    return schema


# =========================
# 🔹 MYSQL SCHEMA EXTRACTOR
# =========================
def get_mysql_schema(conn, table):

    cur = conn.cursor()

    cur.execute(f"""
        SELECT column_name, ordinal_position, data_type
        FROM information_schema.columns
        WHERE table_name = '{table}'
    """)

    schema = []

    for row in cur.fetchall():
        schema.append({
            "column_name": row[0].lower(),
            "ordinal_position": row[1],
            "data_type": row[2]
        })

    return schema


# =========================
# 🔹 GET EXISTING METADATA
# =========================
def get_existing_metadata(conn, source_system, source_table):

    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type
        FROM dyn_etl.metadata
        WHERE source_system=%s AND source_table=%s
    """, (source_system, source_table))

    return {row[0]: row[1] for row in cur.fetchall()}


# =========================
# 🔹 DETECT SCHEMA CHANGES
# =========================
def detect_schema_changes(source_schema, existing_meta):

    actions = []

    source_cols = {col["column_name"]: col for col in source_schema}

    # 🔹 ADD + MODIFY
    for col_name, col_data in source_cols.items():

        if col_name not in existing_meta:
            actions.append({
                "action_type": "ADD",
                "column": col_data
            })

        elif existing_meta[col_name] != col_data["data_type"]:
            actions.append({
                "action_type": "MODIFY",
                "column": col_data
            })

    # 🔹 REMOVE
    for col_name in existing_meta:
        if col_name not in source_cols:
            actions.append({
                "action_type": "REMOVE",
                "column_name": col_name
            })

    return actions


# =========================
# 🔹 INSERT INTO METADATA
# =========================
def insert_metadata(conn, config, actions):

    cur = conn.cursor()

    for act in actions:

        if act["action_type"] in ["ADD", "MODIFY"]:

            col = act["column"]

            cur.execute("""
                INSERT INTO dyn_etl.metadata(
                    source_system,
                    source_table,
                    column_name,
                    ordinal_position,
                    data_type,
                    action_type,
                    old_column_name,
                    new_column_name
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                config["source_system"],
                config["source_table"],
                col["column_name"],
                col["ordinal_position"],
                col["data_type"],
                act["action_type"],
                None,
                None
            ))

        elif act["action_type"] == "REMOVE":

            cur.execute("""
                INSERT INTO dyn_etl.metadata (
                    source_system,
                    source_table,
                    column_name,
                    action_type
                )
                VALUES (%s,%s,%s,%s)
            """, (
                config["source_system"],
                config["source_table"],
                act["column_name"],
                "REMOVE"
            ))

    conn.commit()