from db import get_pg_engine
from sqlalchemy import text
import pandas as pd

engine = get_pg_engine()
df = pd.read_sql(text("SELECT source_column_name, is_primary_key, mtd_type FROM dyn_etl.metadata WHERE source_table_name = 'sales'"), engine)
print(df.to_string())
