from db import get_pg_engine
import pandas as pd

engine = get_pg_engine()
try:
    df = pd.read_sql("SELECT * FROM dyn_etl.metadata", engine)
    print("Metadata Table Content:")
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
