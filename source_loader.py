import pandas as pd
import os
from db import get_mysql_conn

# CSV Loader
def load_csv(config):
    path = config["file_path"]
    if not path:
        raise Exception("❌ file_path is missing in process_control table")

    if not os.path.exists(path):
        raise Exception(f"❌ File not found: {path}")

    print(f"📂 Loading file from: {path}")
    df = pd.read_csv(path)
    return df


# MySQL Loader
def load_mysql(config):
    conn = get_mysql_conn(config["source_database"])

    query = f"SELECT * FROM {config['source_table']}"
    df = pd.read_sql(query, conn)

    conn.close()
    return df


# Source detector
def load_source(config):

    if config["source_system"].upper() == "CSV":
        return load_csv(config)

    elif config["source_system"].upper() == "MYSQL":
        return load_mysql(config)

    else:
        raise Exception("Unsupported source system")