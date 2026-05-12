from source_loader import get_connection_details
from db import get_engine_from_details
from sqlalchemy import Table, MetaData, Column, Integer, String, Float, DateTime, inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as my_insert
import pandas as pd
from sqlalchemy import text


def get_target_connection(config):
    # This is now returning an engine instead of a raw connection for better dynamism
    conn_details = get_connection_details(config["target_connection_name"])
    return get_engine_from_details(conn_details)


def create_table_if_not_exists(engine, config, df, pk):
    """
    Creates target table dynamically using Metadata from the tracking table.
    """
    table_name = config['target_table_name']
    source_table = config['source_table_name']
    schema_name = config.get('target_schema')
    if schema_name == "N/A": schema_name = None

    # Fetch metadata from tracking table
    from db import get_pg_engine
    pg_engine = get_pg_engine()
    df_meta = pd.read_sql(f"SELECT target_column_name, target_data_type, is_primary_key FROM dyn_etl.metadata WHERE source_table_name = '{source_table}'", pg_engine)
    pg_engine.dispose()

    metadata = MetaData()
    columns = []

    if df_meta.empty:
        # Fallback to dataframe if metadata is missing (should not happen with new logic)
        for col in df.columns:
            dtype = str(df[col].dtype)
            if "int" in dtype: sa_type = Integer
            elif "float" in dtype: sa_type = Float
            elif "datetime" in dtype: sa_type = DateTime
            else: sa_type = String(255)
            is_pk = (col.lower() == pk.lower()) if pk else False
            columns.append(Column(col, sa_type, primary_key=is_pk))
    else:
        for _, row in df_meta.iterrows():
            col_name = row['target_column_name']
            raw_type = row['target_data_type'].upper()
            
            if "INT" in raw_type: sa_type = Integer
            elif "DOUBLE" in raw_type or "FLOAT" in raw_type: sa_type = Float
            elif "DATETIME" in raw_type or "TIMESTAMP" in raw_type: sa_type = DateTime
            else: sa_type = String(255)
            
            is_pk = (row['is_primary_key'] == 'Y')
            columns.append(Column(col_name, sa_type, primary_key=is_pk))

    Table(table_name, metadata, *columns, schema=schema_name)
    print(f"🛠️ Ensuring table exists: {schema_name}.{table_name}")
    metadata.create_all(engine)


def truncate_table(engine, config, restart_identity=True):
    """
    Truncates the target table. Supports PostgreSQL RESTART IDENTITY.
    """
    table_name = config['target_table_name']
    schema_name = config.get('target_schema')
    if schema_name == "N/A": schema_name = None
    
    # Handle quoting for special characters in table names
    full_table_name = f'"{schema_name}"."{table_name}"' if schema_name else f'"{table_name}"'
    dialect = engine.dialect.name
    
    sql = f"TRUNCATE TABLE {full_table_name}"
    
    if dialect == 'postgresql' and restart_identity:
        sql += " RESTART IDENTITY"
    with engine.begin() as conn:
        print(f"🧹 Truncating table: {full_table_name} (Restart Identity: {restart_identity})")
        conn.execute(text(sql))


def upsert_data(engine, config, df, pk):
    """
    Dialect-aware upsert using SQLAlchemy constructs.
    Supports TRUNCATE action if specified in config.
    """
    table_name = config['target_table_name']
    schema_name = config.get('target_schema')
    action_type = config.get('action_type', 'UPSERT').upper()
    load_type = config.get('load_type', 'INCREMENTAL').upper()
    restart_id = config.get('restart_identity', True)
    
    if schema_name == "N/A": schema_name = None
    
    metadata = MetaData()
    metadata.reflect(bind=engine, schema=schema_name, only=[table_name])
    table = metadata.tables[f"{schema_name}.{table_name}" if schema_name else table_name]

    dialect = engine.dialect.name
    records = df.to_dict(orient='records')
    
    insert_count, update_count, reject_count = 0, 0, 0

    # Wrap the entire operation in a single transaction for atomicity
    with engine.begin() as conn:
        # 1. Handle Truncate if required
        if action_type == 'TRUNCATE' and load_type == 'FULL':
            full_table_name = f'"{schema_name}"."{table_name}"' if schema_name else f'"{table_name}"'
            sql = f"TRUNCATE TABLE {full_table_name}"
            if dialect == 'postgresql' and restart_id:
                sql += " RESTART IDENTITY"
            print(f"🧹 Atomic Truncate: {full_table_name}")
            conn.execute(text(sql))

        # 2. Perform Data Load
        for record in records:
            try:
                if dialect == 'postgresql':
                    if action_type == 'TRUNCATE' or action_type == 'INSERT':
                        conn.execute(table.insert().values(record))
                        insert_count += 1
                    else:
                        stmt = pg_insert(table).values(record)
                        update_cols = {c: stmt.excluded[c] for c in record.keys() if c.lower() != pk.lower()}
                        stmt = stmt.on_conflict_do_update(index_elements=[pk], set_=update_cols)
                        conn.execute(stmt)
                        update_count += 1

                elif dialect == 'mysql':
                    if action_type == 'TRUNCATE' or action_type == 'INSERT':
                        conn.execute(table.insert().values(record))
                        insert_count += 1
                    else:
                        stmt = my_insert(table).values(record)
                        update_cols = {c: stmt.inserted[c] for c in record.keys() if c.lower() != pk.lower()}
                        stmt = stmt.on_duplicate_key_update(update_cols)
                        conn.execute(stmt)
                        update_count += 1

                else:
                    if action_type == 'TRUNCATE' or action_type == 'INSERT':
                        conn.execute(table.insert().values(record))
                        insert_count += 1
                    else:
                        if pk in record:
                            conn.execute(table.delete().where(getattr(table.c, pk) == record[pk]))
                        conn.execute(table.insert().values(record))
                        insert_count += 1

            except Exception as e:
                if action_type == 'TRUNCATE':
                    # If we are doing a full refresh, we shouldn't allow partial data
                    print(f"❌ Critical failure during Atomic Load: {e}")
                    raise e
                print(f"❌ Record failed: {e}")
                reject_count += 1

    return insert_count, update_count, reject_count