from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

# =====================================
# ADD PROJECT PATH
# =====================================

PROJECT_PATH = "/opt/airflow/project"

sys.path.append(PROJECT_PATH)

# =====================================
# IMPORT YOUR ETL RUNNER
# =====================================

from main import run_pipeline
from db import get_pg_engine
import pandas as pd

# =====================================
# FETCH ACTIVE PIPELINES
# =====================================

engine = get_pg_engine()

df = pd.read_sql("""
SELECT process_name
FROM dyn_etl.process_control
WHERE active_flag = TRUE
""", engine)

engine.dispose()

processes = df["process_name"].tolist()

# =====================================
# DAG DEFAULTS
# =====================================

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1
}

# =====================================
# CREATE DAG
# =====================================

dag = DAG(
    dag_id="dynamic_etl_framework",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)

# =====================================
# CREATE TASKS DYNAMICALLY
# =====================================

for proc in processes:

    task = PythonOperator(
        task_id=f"run_{proc}",
        python_callable=run_pipeline,
        op_args=[proc],
        dag=dag
    )