import re
from sqlalchemy import inspect

def get_csv_schema(df):
    return [
        {
            "column_name": col, 
            "data_type": str(df[col].dtype),
            "is_primary_key": False
        }
        for col in df.columns
    ]

def get_db_schema(engine, table_name, schema_name=None):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name, schema=schema_name)
    
    pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
    pk_cols = pk_constraint.get('constrained_columns', []) if pk_constraint else []
    
    return [
        {
            "column_name": col["name"],
            "data_type": str(col["type"]),
            "is_primary_key": col["name"] in pk_cols
        }
        for col in columns
    ]

def get_existing_metadata(conn, config):
    cur = conn.cursor()
    cur.execute('''
        SELECT SOURCE_COLUMN_NAME, SOURCE_DATA_TYPE, SOURCE_LENGTH, SOURCE_ORDINAL_POSITION, IS_PRIMARY_KEY, MTD_TYPE, CHANGE_EVENT
        FROM dyn_etl.metadata
        WHERE SOURCE_TABLE_NAME = %s
    ''', (config["source_table_name"],))
    
    existing = []
    for r in cur.fetchall():
        col_name = r[0]
        base_type = r[1]
        length = r[2]
        ord_pos = r[3]
        is_pk = r[4] == 'Y'
        mtd_type = r[5]
        change_event = r[6]
        
        # Reconstruct the full data type (e.g., VARCHAR(255)) for accurate comparison
        full_type = f"{base_type}({length})" if length else base_type
        
        existing.append({
            "column_name": col_name, 
            "data_type": full_type, 
            "ordinal_position": ord_pos, 
            "is_primary_key": is_pk, 
            "mtd_type": mtd_type, 
            "change_event": change_event
        })
    return existing

def detect_schema_changes(source_schema, existing_schema):
    changes = []
    src = {c["column_name"]: c for c in source_schema}
    tgt = {c["column_name"]: c for c in existing_schema}
    src_lower = {c["column_name"].lower(): c for c in source_schema}
    tgt_lower = {c["column_name"].lower(): c for c in existing_schema}
    tgt_by_pos = {c["ordinal_position"]: c for c in existing_schema}

    for i, col in enumerate(source_schema):
        col_name = col["column_name"]
        col_name_lower = col_name.lower()
        ord_pos = i + 1
        
        if col_name_lower not in tgt_lower:
            old_col = tgt_by_pos.get(ord_pos)
            # If there's a column at this position in the target that isn't in the source, it's a rename
            if old_col and old_col["column_name"].lower() not in src_lower:
                col["change_event"] = "ALTER"
                col["change_type"] = "RENAME"
                col["old_target_value"] = old_col["column_name"]
                changes.append(f"RENAME: {old_col['column_name']} -> {col_name}")
            else:
                col["change_event"] = "ADD"
                col["change_type"] = "NEW_COLUMN"
                col["old_target_value"] = None
                changes.append(f"NEW COLUMN: {col_name}")
        else:
            old_data = tgt_lower[col_name_lower]
            
            # Use the existing target column name case if they matched case-insensitively
            # This prevents unnecessary ALTERs just for case changes (unless desired)
            # col["column_name"] = old_data["column_name"] 
            
            # If manual, we don't automatically override PK or type if it differs, but we let it pass through
            if old_data.get("mtd_type") == "MANUAL":
                col["is_primary_key"] = old_data.get("is_primary_key")
            
            col_changed = False
            
            if col["data_type"].lower() != str(old_data["data_type"]).lower():
                col["change_event"] = "ALTER"
                col["change_type"] = "DATATYPE_CHANGE"
                col["old_target_value"] = old_data["data_type"]
                col_changed = True
                changes.append(f"TYPE CHANGE: {col_name}")
            
            # PK change check
            if not col_changed and col.get("is_primary_key", False) != old_data.get("is_primary_key", False):
                col["change_event"] = "ALTER"
                col["change_type"] = "PK_CHANGE"
                col["old_target_value"] = "PK" if old_data.get("is_primary_key") else "NON_PK"
                col_changed = True
                changes.append(f"PK CHANGE: {col_name}")
                
            if not col_changed and ord_pos != old_data["ordinal_position"]:
                col["change_event"] = "ALTER"
                col["change_type"] = "POSITION_CHANGE"
                col["old_target_value"] = str(old_data["ordinal_position"])
                col_changed = True
                changes.append(f"POSITION CHANGE: {col_name}")

            if not col_changed:
                col["change_event"] = None
                col["change_type"] = None
                col["old_target_value"] = None

    for col_name in tgt:
        if col_name not in src:
            old_ord = tgt[col_name]["ordinal_position"]
            if old_ord <= len(source_schema):
                new_col_at_pos = source_schema[old_ord - 1]["column_name"]
                if new_col_at_pos not in tgt:
                    continue
            changes.append(f"REMOVED COLUMN: {col_name}")

    return changes

def parse_type_length(raw_type):
    match = re.match(r'^([A-Za-z0-9_]+)(?:\((\d+)\))?', str(raw_type).upper())
    if match:
        return match.group(1), match.group(2)
    return str(raw_type).upper(), None

def insert_metadata(conn, config, schema, existing_schema=[]):
    cur = conn.cursor()
    
    handled_existing = set()

    for i, col in enumerate(schema, start=1):
        if isinstance(col, dict):
            column_name = col.get("column_name")
            raw_data_type = col.get("data_type", "TEXT")
            change_event = col.get("change_event", "ADD")
            change_type = col.get("change_type", "NEW_COLUMN")
            old_target_value = col.get("old_target_value")
            is_pk = col.get("is_primary_key", False)
        elif isinstance(col, str):
            column_name = col
            raw_data_type = "TEXT"
            change_event = "ADD"
            change_type = "NEW_COLUMN"
            old_target_value = None
            is_pk = False
        else:
            continue
            
        if change_event is None:
            handled_existing.add(column_name)
            continue

        src_type, src_length = parse_type_length(raw_data_type)

        dtype_lower = raw_data_type.lower()
        if "int" in dtype_lower:
            tgt_raw_type = "INT"
        elif "float" in dtype_lower:
            tgt_raw_type = "DOUBLE"
        elif "datetime" in dtype_lower:
            tgt_raw_type = "DATETIME"
        else:
            tgt_raw_type = "VARCHAR(255)"

        tgt_type, tgt_length = parse_type_length(tgt_raw_type)

        target_system_name = config.get("target_system", "UNKNOWN")
        target_database = config.get("target_database")
        target_schema = config.get("target_schema")
        target_table_name = config.get("target_table_name")
        pk_val = 'Y' if is_pk else 'N'

        if change_event == "ADD":
            cur.execute('''
                INSERT INTO dyn_etl.metadata (
                    SOURCE_SYSTEM,
                    SOURCE_TABLE_NAME,
                    SOURCE_ORDINAL_POSITION,
                    SOURCE_COLUMN_NAME,
                    SOURCE_DATA_TYPE,
                    SOURCE_LENGTH,
                    SOURCE_DATABASE,
                    SOURCE_SCHEMA,
                    TARGET_SYSTEM_NAME,
                    TARGET_DATABASE,
                    TARGET_SCHEMA,
                    TARGET_TABLE_NAME,
                    TARGET_ORDINAL_POSITION,
                    TARGET_COLUMN_NAME,
                    TARGET_DATA_TYPE,
                    TARGET_LENGTH,
                    CHANGE_EVENT,
                    CHANGE_TYPE,
                    OLD_TARGET_VALUE,
                    UPDATE_FLAG,
                    IS_PRIMARY_KEY,
                    MTD_TYPE,
                    EL_CREATED_DATE_TIME,
                    EL_UPDATED_DATE_TIME
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'DYNAMIC',NOW(),NOW())
            ''', (
                config.get("source_system"),
                config.get("source_table_name"),
                i,
                column_name,
                src_type,
                src_length,
                config.get("source_database"),
                config.get("source_schema"),
                target_system_name,
                target_database,
                target_schema,
                target_table_name,
                i,
                column_name,
                tgt_type,
                tgt_length,
                change_event,
                change_type,
                old_target_value,
                'Y',
                pk_val
            ))
        elif change_event == "ALTER":
            update_match_column = old_target_value if change_type == "RENAME" else column_name
            
            cur.execute('''
                UPDATE dyn_etl.metadata SET
                    SOURCE_ORDINAL_POSITION = %s,
                    SOURCE_COLUMN_NAME = %s,
                    SOURCE_DATA_TYPE = %s,
                    SOURCE_LENGTH = %s,
                    TARGET_ORDINAL_POSITION = %s,
                    TARGET_COLUMN_NAME = %s,
                    TARGET_DATA_TYPE = %s,
                    TARGET_LENGTH = %s,
                    CHANGE_EVENT = %s,
                    CHANGE_TYPE = %s,
                    OLD_TARGET_VALUE = %s,
                    IS_PRIMARY_KEY = %s,
                    EL_UPDATED_DATE_TIME = NOW()
                WHERE SOURCE_TABLE_NAME = %s AND SOURCE_COLUMN_NAME = %s
            ''', (
                i,
                column_name,
                src_type,
                src_length,
                i,
                column_name,
                tgt_type,
                tgt_length,
                change_event,
                change_type,
                old_target_value,
                pk_val,
                config.get("source_table_name"),
                update_match_column
            ))
            handled_existing.add(update_match_column)

    src_col_names = {c.get("column_name") if isinstance(c, dict) else c for c in schema}
    for ext_col in existing_schema:
        ext_name = ext_col["column_name"]
        if ext_name not in src_col_names and ext_name not in handled_existing:
            cur.execute('''
                UPDATE dyn_etl.metadata SET
                    CHANGE_EVENT = 'ALTER',
                    CHANGE_TYPE = 'DROP',
                    UPDATE_FLAG = 'N',
                    EL_UPDATED_DATE_TIME = NOW()
                WHERE SOURCE_TABLE_NAME = %s AND SOURCE_COLUMN_NAME = %s
            ''', (config.get("source_table_name"), ext_name))

    conn.commit()
