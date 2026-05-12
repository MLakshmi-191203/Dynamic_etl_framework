from db import get_pg_engine
from sqlalchemy import text

engine = get_pg_engine()
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE dyn_etl.metadata ADD COLUMN mtd_type VARCHAR(50) DEFAULT 'DYNAMIC'"))
        conn.commit()
        print("Added mtd_type")
    except Exception as e:
        conn.rollback()
        print("mtd_type might exist")

    try:
        conn.execute(text("ALTER TABLE dyn_etl.metadata ADD COLUMN is_primary_key VARCHAR(1) DEFAULT 'N'"))
        conn.commit()
        print("Added is_primary_key")
    except Exception as e:
        conn.rollback()
        print("is_primary_key might exist")
