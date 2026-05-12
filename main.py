from datetime import datetime

from db import get_pg_conn, get_engine_from_details
from config_reader import get_active_configs
from source_loader import load_source, get_connection_details
from target_loader import create_table_if_not_exists, upsert_data, get_target_connection
from audit import log_run

from schema_engine import get_csv_schema, get_db_schema

import mysql.connector
import psycopg2


# =========================
# 🚀 MAIN PIPELINE
# =========================
def run_pipeline(process_name=None):

    # ✅ Import INSIDE function (fixes your error)
    from schema_validation import validate_or_capture_schema

    configs = get_active_configs(process_name)

    if not configs:
        raise Exception(f"No active configs found for process: {process_name}")

    print(f"🚀 Running Process: {process_name}")

    configs = sorted(configs, key=lambda x: x.get("run_seq", 1))

    for config in configs:

        start_time = datetime.now()

        # 🔹 Metadata DB (Postgres)
        pg_conn = get_pg_conn()

        # 🔹 Target connection (dynamic)
        target_conn = get_target_connection(config)

        try:
            print(f"🚀 Running pipeline for {config['source_table_name']}")

            # =========================
            # 🔹 LOAD SOURCE
            # =========================
            df = load_source(config)

            # =========================
            # 🔹 SOURCE CONNECTION
            # =========================
            source_conn = get_connection_details(config["source_connection_name"])
            system = source_conn["system"].upper()
            config["source_system"] = system 
            
            # ✅ Populate missing metadata fields if available in connection details
            if not config.get("source_database"):
                config["source_database"] = source_conn.get("database")
            if not config.get("source_schema") or config.get("source_schema") == "N/A":
                if system in ["CSV", "SQLITE"]:
                    config["source_schema"] = "N/A"
                elif system == "MYSQL":
                    config["source_schema"] = source_conn.get("database")
                else:
                    config["source_schema"] = "public"

            # =========================
            # 🔥 SCHEMA EXTRACTION (Generic)
            # =========================
            if system == "CSV":
                source_schema = get_csv_schema(df)
            else:
                source_engine = get_engine_from_details(source_conn)
                source_schema = get_db_schema(
                    source_engine,
                    config["source_table_name"],
                    schema_name=config.get("source_schema") if config.get("source_schema") != "N/A" else None
                )
                source_engine.dispose()

            # =========================
            # 🔥 PREPARE TARGET METADATA
            # =========================
            tgt_details = get_connection_details(config["target_connection_name"])
            target_system = tgt_details["system"].upper()
            config["target_system"] = target_system
            if not config.get("target_database"):
                config["target_database"] = tgt_details.get("database")
            if not config.get("target_schema") or config.get("target_schema") == "N/A":
                if target_system in ["CSV", "SQLITE"]:
                    config["target_schema"] = "N/A"
                elif target_system == "MYSQL":
                    config["target_schema"] = tgt_details.get("database")
                else:
                    config["target_schema"] = "public"

            # =========================
            # 🔥 SCHEMA VALIDATION
            # =========================
            schema_ok = validate_or_capture_schema(pg_conn, config, source_schema)

            if not schema_ok:
                log_run(
                    pg_conn,
                    config,
                    start_time,
                    datetime.now(),
                    0, 0, 0,
                    "AWAITING APPROVAL",
                    "Schema drift detected. Alert sent to admin."
                )
                print(f"⏸️ Pipeline paused for {config['source_table_name']} until schema changes are approved.")
                continue

            # =========================
            # 🔹 TARGET TABLE
            # =========================
            target_table = f"{config['target_schema']}.{config['target_table_name']}"
            pk = config["primary_key"]

            # =========================
            # 🔹 CREATE TABLE
            # =========================
            create_table_if_not_exists(target_conn, config, df, pk)

            # =========================
            # 🔹 UPSERT
            # =========================
            ins, upd, rej = upsert_data(target_conn, config, df, pk)

            # =========================
            # 🔹 AUDIT
            # =========================
            log_run(
                pg_conn,
                config,
                start_time,
                datetime.now(),
                ins,
                upd,
                rej,
                "SUCCESS",
                None
            )

            print(f"✅ Completed {target_table}")

        except Exception as e:

            print(f"❌ Failed: {e}")

            pg_conn.rollback()

            log_run(
                pg_conn,
                config,
                start_time,
                datetime.now(),
                0, 0, 0,
                "FAILED",
                str(e)
            )

        finally:
            pg_conn.close()
            if target_conn:
                target_conn.dispose()


# =========================
# 🔥 ENTRY POINT
# =========================
if __name__ == "__main__":
    run_pipeline()