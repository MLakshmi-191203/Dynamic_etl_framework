from embedder import get_embedding
from vector_store import VectorStore
import psycopg2
from collections import defaultdict


def fetch_metadata():

    conn = psycopg2.connect(
        host="localhost",
        database="etl_db",
        user="postgres",
        password="Postgre@2000"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT source_table, column_name, data_type
        FROM dyn_etl.metadata
    """)

    rows = cur.fetchall()
    conn.close()

    # 🔥 GROUP BY TABLE
    table_map = defaultdict(list)

    for r in rows:
        table = r[0]
        column = r[1]
        dtype = r[2]

        table_map[table].append(f"{column} ({dtype})")

    texts = []

    # 🔥 Create ONE embedding per table
    for table, cols in table_map.items():

        text = f"""
        Table: {table}
        Columns: {", ".join(cols)}
        """

        texts.append(text)

    return texts


def build_vector_store():

    texts = fetch_metadata()

    embeddings = []
    for t in texts:
        emb = get_embedding(t)
        embeddings.append(emb)

    vs = VectorStore()
    vs.add(embeddings, texts)
    vs.save()

    print("✅ FAISS index created (TABLE LEVEL)")


if __name__ == "__main__":
    build_vector_store()