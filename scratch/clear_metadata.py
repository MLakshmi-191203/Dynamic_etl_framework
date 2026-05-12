from db import get_pg_engine
from sqlalchemy import text

engine = get_pg_engine()
with engine.connect() as conn:
    conn.execute(text("DELETE FROM dyn_etl.metadata"))
    conn.commit()
engine.dispose()
print("Metadata cleared.")
