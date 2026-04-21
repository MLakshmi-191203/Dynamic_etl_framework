from datetime import datetime

from db import get_pg_conn, get_mysql_conn
from config_reader import get_active_configs
from source_loader import load_source
from target_loader import create_table_if_not_exists, upsert_data
from audit import log_run

# 🔥 Schema
from schema_validation import validate_or_capture_schema
from schema_engine import get_csv_schema, get_mysql_schema


def run_pipeline():

    configs = get_active_configs()
    print("🔍 Config:", configs)

    for config in configs:

        start_time = datetime.now()
        pg_conn = get_pg_conn()

        try:
            print(f"🚀 Running pipeline for {config['source_table']}")

            # 🔹 Load source data
            df = load_source(config)

            # =========================
            # 🔥 SCHEMA EXTRACTION
            # =========================
            if config["source_system"] == "CSV":
                source_schema = get_csv_schema(df)

            elif config["source_system"] == "MYSQL":
                mysql_conn = get_mysql_conn(config["source_database"])
                source_schema = get_mysql_schema(mysql_conn, config["source_table"])
                mysql_conn.close()

            else:
                raise Exception("Unsupported source system")

            # =========================
            # 🔥 SCHEMA VALIDATION / CAPTURE
            # =========================
            validate_or_capture_schema(pg_conn, config, source_schema)

            # =========================
            # 🔹 TARGET DETAILS
            # =========================
            target_table = f"{config['target_schema']}.{config['target_table']}"
            pk = config["primary_key"]

            # 🔹 Create table
            create_table_if_not_exists(pg_conn, target_table, df, pk)

            # 🔹 Load data
            ins, upd, rej = upsert_data(pg_conn, target_table, df, pk)

            # 🔹 Audit log
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

            # 🔴 VERY IMPORTANT FIX
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


if __name__ == "__main__":
    run_pipeline()