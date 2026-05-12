from sqlalchemy import text

def apply_schema_changes(engine, config, changes_df):
    """
    Applies ALTER TABLE commands to the target system based on metadata changes.
    """
    dialect = engine.dialect.name
    target_table = config['target_table_name']
    target_schema = config.get('target_schema')
    if target_schema == "N/A": target_schema = None
    
    full_table_name = f"{target_schema}.{target_table}" if target_schema else target_table
    
    # Reflect current target table columns to avoid duplicate errors
    from sqlalchemy import inspect
    inspector = inspect(engine)
    try:
        existing_columns_real = [c['name'] for c in inspector.get_columns(target_table, schema=target_schema)]
    except Exception as e:
        print(f"⚠️ Could not inspect table {full_table_name}: {e}")
        existing_columns_real = []
        
    existing_columns_lower = [c.lower() for c in existing_columns_real]
    print(f"🔍 Existing columns in {full_table_name}: {existing_columns_lower}")
    
    with engine.begin() as conn:
        for _, row in changes_df.iterrows():
            change_event = row.get('change_event')
            change_type = row.get('change_type')
            
            if not change_event:
                continue
                
            sql = None
            if change_type == 'RENAME':
                old_col = row.get('old_target_value')
                new_col = row.get('target_column_name')
                
                # Case-insensitive check
                old_exists = old_col.lower() in existing_columns_lower
                new_exists = new_col.lower() in existing_columns_lower

                if old_exists and not new_exists:
                    # Get the REAL case of the old column from the DB
                    real_old_col = existing_columns_real[existing_columns_lower.index(old_col.lower())]
                    if dialect == 'postgresql':
                        sql = f'ALTER TABLE {full_table_name} RENAME COLUMN "{real_old_col}" TO "{new_col}"'
                    elif dialect == 'mysql':
                        sql = f"ALTER TABLE {full_table_name} RENAME COLUMN `{real_old_col}` TO `{new_col}`"
                    elif dialect == 'mssql':
                        sql = f"EXEC sp_rename '{full_table_name}.{real_old_col}', '{new_col}', 'COLUMN'"
                    elif dialect == 'sqlite':
                        sql = f'ALTER TABLE {full_table_name} RENAME COLUMN "{real_old_col}" TO "{new_col}"'
                else:
                    print(f"⏩ Skipping RENAME: {old_col} -> {new_col} (Old exists: {old_exists}, New exists: {new_exists})")

            elif change_type == 'NEW_COLUMN':
                col_name = row.get('target_column_name')
                col_type = row.get('target_data_type')
                
                if col_name.lower() not in existing_columns_lower:
                    sql = f"ALTER TABLE {full_table_name} ADD COLUMN {col_name} {col_type}"
                else:
                    print(f"⏩ Skipping ADD: {col_name} (Already exists in {existing_columns_lower})")
            
            elif change_type == 'DATATYPE_CHANGE':
                col_name = row.get('target_column_name')
                col_type = row.get('target_data_type')
                if dialect == 'postgresql':
                    sql = f'ALTER TABLE {full_table_name} ALTER COLUMN "{col_name}" TYPE {col_type}'
                elif dialect == 'mysql':
                    sql = f"ALTER TABLE {full_table_name} MODIFY COLUMN `{col_name}` {col_type}"
                else:
                    sql = f"ALTER TABLE {full_table_name} ALTER COLUMN {col_name} {col_type}"

            if sql:
                try:
                    print(f"🛠️ Executing: {sql}")
                    conn.execute(text(sql))
                except Exception as e:
                    if "Duplicate column" in str(e) or "1060" in str(e):
                        print(f"⚠️ Ignored duplicate column error for {col_name}")
                    else:
                        raise e
    
    return True
