import faiss
import numpy as np
import pickle
import os

class VectorStore:

    def __init__(self, dim=768):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.texts.extend(texts)

    def save(self, path=None):

        if path is None:
            path = os.path.join(os.path.dirname(__file__), "faiss_index.pkl")

        with open(path, "wb") as f:
            pickle.dump((self.index, self.texts), f)

    def load(self, path=None):

        if path is None:
            path = os.path.join(os.path.dirname(__file__), "faiss_index.pkl")

        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ FAISS file not found at: {path}")

        with open(path, "rb") as f:
            self.index, self.texts = pickle.load(f)

    def search(self, query_embedding, k=25):
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )
        return [self.texts[i] for i in I[0]]