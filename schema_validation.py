print("schema_validation module loaded")

from schema_engine import (
    get_existing_metadata,
    detect_schema_changes,
    insert_metadata
)

from email_service import send_schema_alert


def validate_or_capture_schema(conn, config, source_schema):

    table = config.get("source_table_name")
    process = config.get("process_name")

    print(f"🔎 Checking schema for: {table}")

    try:
        existing = get_existing_metadata(conn, config) or []
    except Exception as e:
        print(f"❌ Failed to fetch existing metadata: {e}")
        existing = []

    # =========================
    # 🆕 FIRST RUN
    # =========================
    if not existing:
        print("🆕 First run → capturing schema")

        try:
            insert_metadata(conn, config, source_schema, existing_schema=[])
            print("✅ Initial schema captured")
        except Exception as e:
            print(f"❌ Metadata insert failed: {e}")
            return False

        return True

    # =========================
    # ⛔ CHECK PENDING APPROVAL
    # =========================
    try:
        pending_changes = [
            c.get('column_name')
            for c in existing
            if isinstance(c, dict) and c.get('change_event')
        ]
    except Exception:
        pending_changes = []

    if pending_changes:
        print(f"⚠️ PENDING APPROVAL for columns: {pending_changes}")
        print("⛔ Pipeline stopped until approval")
        return False

    # =========================
    # 🔍 DETECT CHANGES
    # =========================
    try:
        changes = detect_schema_changes(source_schema, existing)
    except Exception as e:
        print(f"❌ Schema comparison failed: {e}")
        return False

    # =========================
    # ⚠️ CHANGES FOUND
    # =========================
    if changes:

        print("⚠️ Changes detected:", changes)

        # 🔄 Update metadata tracking
        try:
            insert_metadata(conn, config, source_schema, existing_schema=existing)
            print("🔄 Metadata updated")
        except Exception as e:
            print(f"❌ Metadata update failed: {e}")

        # =========================
        # 📧 SEND EMAIL ALERT
        # =========================
        admin_email = config.get("admin_email")
        target_table = f"{config.get('target_schema')}.{config.get('target_table_name')}"
        dialect = config.get("target_system") or "postgresql"

        if admin_email:
            try:
                email_sent = send_schema_alert(
                    admin_email,
                    process,
                    changes,
                    target_table,
                    dialect
                )

                if email_sent:
                    print(f"📧 Alert sent to {admin_email}")
                else:
                    print("❌ Email sending failed")

            except Exception as e:
                print(f"❌ Email error: {e}")

        else:
            print("⚠️ No admin_email configured → skipping email")

        print("⛔ Pipeline stopped due to schema change")
        return False

    # =========================
    # ✅ NO CHANGES
    # =========================
    print("✅ Schema OK")
    return True