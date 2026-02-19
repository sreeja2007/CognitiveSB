from retrieval.vector_store import VectorStore

vs = VectorStore()
vs.load()

print("Total stored chunks:", len(vs.documents))

print("\n--- Sample Chunks ---\n")

for i, doc in enumerate(vs.documents[:5]):
    print(f"\nChunk {i+1}:\n")
    print(doc.page_content[:500])
    print("\n" + "-"*50)
