import os
import faiss
import pickle
import numpy as np


class VectorStore:

    def __init__(self, index_path="vector_store"):
        self.index_path = index_path
        self.index = None
        self.documents = []

        if not os.path.exists(index_path):
            os.makedirs(index_path)

    def create_index(self, dimension):
        self.index = faiss.IndexFlatL2(dimension)

    def add(self, embeddings, documents):

        index_file = os.path.join(self.index_path, "faiss.index")
        doc_file = os.path.join(self.index_path, "documents.pkl")

        if os.path.exists(index_file):
             self.load()
        else:
            # Create new index
            self.create_index(len(embeddings[0]))
            # self.documents = []

        # Add new data
        self.index.add(np.array(embeddings))
        self.documents.extend(documents)

    def save(self):
        faiss.write_index(self.index, os.path.join(self.index_path, "faiss.index"))

        with open(os.path.join(self.index_path, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)
    def load(self):
        self.index = faiss.read_index(os.path.join(self.index_path, "faiss.index"))

        with open(os.path.join(self.index_path, "documents.pkl"), "rb") as f:
            self.documents = pickle.load(f)

    def search(self, query_embedding, k=3):
        distances, indices = self.index.search(
            np.array([query_embedding]), k
        )

        results = []
        for idx in indices[0]:
            results.append(self.documents[idx])

        return results
