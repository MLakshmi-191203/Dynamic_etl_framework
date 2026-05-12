import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

class AirflowService:
    def __init__(self, base_url="http://localhost:8080/api/v1", username="airflow", password="airflow"):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)

    def get_dags(self):
        """Fetches all DAGs from Airflow."""
        try:
            response = requests.get(f"{self.base_url}/dags", auth=self.auth, timeout=3)
            response.raise_for_status()
            return response.json().get("dags", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching DAGs (Airflow might be down): {e}")
            return []

    def get_dag_details(self, dag_id):
        """Fetches details for a specific DAG."""
        try:
            response = requests.get(f"{self.base_url}/dags/{dag_id}", auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching DAG details for {dag_id}: {e}")
            return {}

    def get_last_run(self, dag_id):
        """Fetches the latest run for a specific DAG."""
        try:
            # We want the most recent run
            params = {"limit": 1, "order_by": "-execution_date"}
            response = requests.get(f"{self.base_url}/dags/{dag_id}/dagRuns", auth=self.auth, params=params)
            response.raise_for_status()
            runs = response.json().get("dag_runs", [])
            return runs[0] if runs else None
        except Exception as e:
            print(f"Error fetching last run for {dag_id}: {e}")
            return None

    def trigger_dag(self, dag_id):
        """Triggers a new run for a DAG."""
        try:
            # Airflow 2.0+ requires an empty JSON body for the trigger endpoint
            response = requests.post(f"{self.base_url}/dags/{dag_id}/dagRuns", auth=self.auth, json={})
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            return False, str(e)

    def update_dag_state(self, dag_id, is_paused):
        """Pauses or unpauses a DAG."""
        try:
            data = {"is_paused": is_paused}
            response = requests.patch(f"{self.base_url}/dags/{dag_id}", auth=self.auth, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error updating DAG state for {dag_id}: {e}")
            return False

# Singleton instance
airflow_api = AirflowService()
