def validate_schema_or_fail(actions):

    if not actions:
        return  # ✅ no change

    error_msg = "\n🚨 SCHEMA CHANGE DETECTED:\n"

    for act in actions:

        if act["action_type"] == "ADD":
            error_msg += f"➕ New column added: {act['column']['column_name']}\n"

        elif act["action_type"] == "REMOVE":
            error_msg += f"➖ Column removed: {act['column_name']}\n"

        elif act["action_type"] == "MODIFY":
            error_msg += f"✏️ Data type changed: {act['column']['column_name']}\n"

    error_msg += "\n❌ Pipeline stopped due to schema change."

    raise Exception(error_msg)