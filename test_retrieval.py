from processing.embedder import Embedder
from retrieval.vector_store import VectorStore
from processing.graph import rag_graph

def test_retrieval_and_graph():
    # 1️⃣ Setup Components
    print("\n--- Initializing Components ---\n")
    embedder = Embedder()
    vs = VectorStore()
    
    try:
        vs.load(embedder.model)
        print("OK: Vector Store loaded successfully.")
    except Exception as e:
        print(f"Error: Error loading vector store: {e}")
        print("Ensure 'vector_store' directory exists and contains FAISS index.")
        return

    # 2️⃣ Take query input
    query = input("\nQuery: Enter your query: ")
    if not query.strip():
        print("Empty query. Exiting.")
        return

    # 3️⃣ Test Raw Retrieval (LangChain approach)
    print("\n--- Testing Raw Retrieval (direct search) ---\n")
    results = vs.search(query, k=3)
    
    if not results:
        print("No documents found.")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(doc.page_content[:400] + "...")
        print("-" * 50)

    # 4️⃣ Test LangGraph Workflow (Graph approach)
    print("\n--- Testing LangGraph Workflow ---\n")
    print("Involving graph.retrieve_node -> graph.generate_node...")
    
    # Define initial state
    initial_state = {
        "query": query,
        "context": [],
        "answer": ""
    }
    
    # Stream the graph execution
    try:
        for output in rag_graph.stream(initial_state):
            for node, state in output.items():
                print(f"\n[Node: {node}] completed.")
                if node == "generate":
                    print(f"\n✨ Final Answer:\n{state['answer']}")
    except Exception as e:
        print(f"❌ Error during graph execution: {e}")

if __name__ == "__main__":
    test_retrieval_and_graph()
