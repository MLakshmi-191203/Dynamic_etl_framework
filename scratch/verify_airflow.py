import requests
from requests.auth import HTTPBasicAuth

def verify_airflow_api():
    base_url = "http://localhost:8080/api/v1"
    auth = HTTPBasicAuth("airflow", "airflow")
    
    try:
        print(f"Connecting to {base_url}/health...")
        response = requests.get("http://localhost:8080/health")
        print(f"Health check status: {response.status_code}")
        
        print(f"Fetching DAGs from {base_url}/dags...")
        response = requests.get(f"{base_url}/dags", auth=auth)
        if response.status_code == 200:
            dags = response.json().get("dags", [])
            print(f"Success! Found {len(dags)} DAGs.")
            for dag in dags:
                print(f" - {dag['dag_id']} (Paused: {dag['is_paused']})")
        else:
            print(f"Failed to fetch DAGs. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error connecting to Airflow: {e}")

if __name__ == "__main__":
    verify_airflow_api()
