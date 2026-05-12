from db import get_pg_engine
from sqlalchemy import text

engine = get_pg_engine()
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE dyn_etl.process_control ADD COLUMN admin_email VARCHAR(255)"))
        conn.commit()
        print("Added admin_email")
    except Exception as e:
        conn.rollback()
        print("admin_email might exist:", str(e))
