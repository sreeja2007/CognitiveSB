from flask import Blueprint, jsonify
from routes.store import session_store

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graph/<session_id>', methods=['GET'])
def get_graph(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    graph_data = session_store[session_id].get("graph")
    if not graph_data:
        return jsonify({"nodes": [], "links": []})
        
    return jsonify(graph_data)

@graph_bp.route('/graph/generate/<session_id>', methods=['POST'])
def generate_graph(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    try:
        from processing.graph_extractor import extract_knowledge_graph
        from langchain_core.documents import Document
        from processing.chunker import Chunker
        full_text = session_store[session_id].get("full_text", "")
        if not full_text:
            return jsonify({"error": "no_text"}), 400
            
        chunks = Chunker().split([Document(page_content=full_text)])
        graph_data = extract_knowledge_graph(chunks) 
        
        # Map edges to links for frontend
        if "edges" in graph_data:
            graph_data["links"] = graph_data.pop("edges")
            
        session_data = session_store[session_id]
        session_data["graph"] = graph_data
        session_store[session_id] = session_data
        return jsonify(graph_data)
    except Exception as e:
        print("Graph generation error:", e)
        return jsonify({"nodes": [], "links": []})
