from processing.embedder import Embedder
from retrieval.vector_store import VectorStore

# 1️⃣ Load vector store
vs = VectorStore()
vs.load()

print("Total chunks in store:", len(vs.documents))

# 2️⃣ Take query input
query = input("Enter your query: ")

# 3️⃣ Embed query
embedder = Embedder()
query_embedding = embedder.embed_documents([query])[0]

# 4️⃣ Search
results = vs.search(query_embedding, k=3)

print("\n--- Retrieved Chunks ---\n")

for i, doc in enumerate(results):
    print(f"\nResult {i+1}:\n")
    print(doc.page_content[:600])
    print("\n" + "="*70)
