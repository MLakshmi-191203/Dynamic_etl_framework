# schema_validation.py

from schema_engine import (
    get_existing_metadata,
    detect_schema_changes,
    insert_metadata
)


def validate_or_capture_schema(conn, config, source_schema):

    print("🔎 Checking schema for:", config["source_table"])

    existing_meta = get_existing_metadata(
        conn,
        config["source_system"],
        config["source_table"]
    )

    actions = detect_schema_changes(source_schema, existing_meta)

    # 🟢 FIRST RUN
    if not existing_meta:
        print("🆕 First run → capturing metadata")

        insert_metadata(conn, config, actions)

        print("✅ Metadata stored")
        return

    # 🔴 NEXT RUN
    if actions:
        print("❌ Schema change detected:", actions)

        raise Exception(f"Schema mismatch: {actions}")

    print("✅ Schema validation passed")