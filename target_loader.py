def create_table_if_not_exists(conn, table, df, pk):

    cur = conn.cursor()

    columns = []

    for col in df.columns:
        columns.append(f"{col} TEXT")

    columns.append(f"PRIMARY KEY ({pk})")

    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        {",".join(columns)}
    )
    """

    cur.execute(ddl)
    conn.commit()


def upsert_data(conn, table, df, pk):

    cur = conn.cursor()

    insert_count = 0
    update_count = 0
    reject_count = 0

    for _, row in df.iterrows():

        try:
            cols = list(df.columns)
            values = tuple(row)

            col_str = ",".join(cols)
            val_str = ",".join(["%s"] * len(values))

            update_str = ",".join([f"{c}=EXCLUDED.{c}" for c in cols])

            query = f"""
            INSERT INTO {table} ({col_str})
            VALUES ({val_str})
            ON CONFLICT ({pk})
            DO UPDATE SET {update_str}
            """

            cur.execute(query, values)

            # 👉 NOTE: we don’t know insert/update here
            update_count += 1  

        except Exception as e:
            print("❌ Reject:", e)
            reject_count += 1

    conn.commit()

    return insert_count, update_count, reject_count