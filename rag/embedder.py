import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

def get_embedding(text):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": text
        }
    )

    return response.json()["embedding"]