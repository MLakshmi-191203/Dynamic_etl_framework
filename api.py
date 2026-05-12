from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime

from db import get_pg_conn, get_pg_engine
from airflow_service import airflow_api
from main import run_pipeline as local_run_pipeline

app = FastAPI(title="Dynamic ETL API")

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class PipelineTrigger(BaseModel):
    process_name: str
    mode: str = "manual" # manual, scheduled, immediate
    connection_override: Optional[str] = None

# --- Endpoints ---

@app.get("/api/pipelines")
def list_pipelines():
    engine = get_pg_engine()
    df = pd.read_sql("SELECT process_name, source_table_name, target_table_name, load_type, active_flag, frequency FROM dyn_etl.process_control ORDER BY run_seq", engine)
    engine.dispose()
    return df.to_dict(orient="records")

@app.get("/api/connections")
def list_connections():
    engine = get_pg_engine()
    df = pd.read_sql("SELECT connection_name, source_system, host, database_name FROM dyn_etl.connection_parameters", engine)
    engine.dispose()
    return df.to_dict(orient="records")

@app.post("/api/pipelines/run")
def trigger_pipeline(trigger: PipelineTrigger, background_tasks: BackgroundTasks):
    """
    Triggers a pipeline execution. 
    If Airflow is available, it triggers the DAG. 
    Otherwise, it runs locally in the background.
    """
    process_name = trigger.process_name
    
    # Check Airflow first
    try:
        success, info = airflow_api.trigger_dag(process_name)
        if success:
            return {"status": "SUCCESS", "mode": "airflow", "details": info}
    except Exception as e:
        print(f"Airflow trigger failed, falling back to local: {e}")

    # Fallback to local background execution
    background_tasks.add_task(local_run_pipeline, process_name)
    return {"status": "QUEUED", "mode": "local", "details": f"Local background task started for {process_name}"}

@app.get("/api/executions")
def get_execution_history():
    engine = get_pg_engine()
    # Fetching from audit logs
    query = """
        SELECT 
            PROCESS_NAME, 
            PIPELINE_STARTTIME as start_time, 
            PIPELINE_ENDTIME as end_time, 
            STATUS, 
            INSERT_COUNT as inserted, 
            UPDATE_COUNT as updated, 
            REJECT_COUNT as rejected,
            ERROR_MESSAGE as error
        FROM dyn_etl.process_control_details 
        ORDER BY PIPELINE_STARTTIME DESC 
        LIMIT 50
    """
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df.to_dict(orient="records")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
