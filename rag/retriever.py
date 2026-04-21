from rag.embedder import get_embedding

def retrieve(query, vector_store):

    query_embedding = get_embedding(query)

    results = vector_store.search(query_embedding, k=3)

    return results