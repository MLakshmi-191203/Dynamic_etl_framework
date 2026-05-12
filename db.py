import psycopg2
from sqlalchemy import create_engine
import urllib.parse

def get_pg_conn():
    return psycopg2.connect(
        host="host.docker.internal",
        database="etl_db",
        user="postgres",          # ✅ FIX
        password="Postgre@2000"
    )

def get_pg_engine():
    # Central metadata engine
    pwd = urllib.parse.quote_plus("Postgre@2000")
    return create_engine(f"postgresql+psycopg2://postgres:{pwd}@host.docker.internal:5432/etl_db")

def get_engine_from_details(details):
    """
    Returns a SQLAlchemy engine based on connection details.
    Supports: POSTGRES, MYSQL, SQLITE, SQL_SERVER
    """
    system = details.get("system", "").upper()
    user = details.get("username", "")
    pwd = urllib.parse.quote_plus(details.get("password", ""))
    host = details.get("host", "")
    port = details.get("port", "")
    db = details.get("database", "")
    file_path = details.get("file_path", "")

    if system == "POSTGRES":
        return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")
    
    elif system == "MYSQL":
        return create_engine(f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{db}")
    
    elif system == "SQLITE":
        # SQLite uses file path. If empty, uses in-memory.
        path = file_path if file_path else ":memory:"
        return create_engine(f"sqlite:///{path}")
    
    elif system == "SQL_SERVER":
        # Requires pyodbc and a driver name like 'ODBC Driver 17 for SQL Server'
        # This is a template; driver may vary.
        params = urllib.parse.quote_plus(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={db};UID={user};PWD={details.get('password', '')}"
        )
        return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    
    else:
        raise Exception(f"Unsupported system for engine creation: {system}")