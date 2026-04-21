import requests
from rag.retriever import retrieve

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_answer(query, vector_store):

    context = retrieve(query, vector_store)

    prompt = f"""
You are a data engineer assistant.

Use the below metadata context to answer.

Context:
{context}

Question:
{query}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]