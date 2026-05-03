import os
from langchain_community.vectorstores import FAISS

class VectorStore:

    def __init__(self, index_path="vector_store"):
        self.index_path = index_path
        self.vector_store = None

    def add(self, embeddings_model, documents):
        if not os.path.exists(self.index_path) or not os.path.exists(os.path.join(self.index_path, "index.faiss")):
            # Create new vector store
            self.vector_store = FAISS.from_documents(documents, embeddings_model)
        else:
            # Load existing and format new documents
            self.load(embeddings_model)
            self.vector_store.add_documents(documents)

    def save(self):
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)

    def load(self, embeddings_model):
        self.vector_store = FAISS.load_local(self.index_path, embeddings_model, allow_dangerous_deserialization=True)

    def search(self, query, k=3, session_id=None):
        if self.vector_store is None:
            return []
        # Return LangChain Document objects
        if session_id:
            try:
                return self.vector_store.max_marginal_relevance_search(
                    query,
                    k=k,
                    fetch_k=max(10, k * 4),
                    filter={"session_id": session_id}
                )
            except TypeError:
                docs = self.vector_store.max_marginal_relevance_search(query, k=max(k * 4, 10), fetch_k=max(k * 8, 20))
                return [doc for doc in docs if doc.metadata.get("session_id") == session_id][:k]
        return self.vector_store.max_marginal_relevance_search(query, k=k, fetch_k=10)
