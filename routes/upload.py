import os
import uuid
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from routes.store import session_store

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'pptx'}
MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload():
    try:
        from loaders.loader_manager import LoaderManager
        from loaders.youtube_loader import YoutubeLoader
        from processing.chunker import Chunker
        from processing.embedder import Embedder
        from retrieval.vector_store import VectorStore
        from processing.graph_extractor import extract_knowledge_graph
        from llm.generator import Generator
        from agents.prompts import NOTES_PROMPT, FLASHCARD_GENERATION_PROMPT, QUIZ_MCQ_PROMPT, QUIZ_SHORT_ANSWER_PROMPT
        
        session_id = str(uuid.uuid4())
        
        # We need an uploads folder
        os.makedirs('uploads', exist_ok=True)

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "upload_failed", "message": "No selected file"}), 400
            if not allowed_file(file.filename):
                return jsonify({"error": "upload_failed", "message": "Invalid file type"}), 400
            
            # Size check might be handled by Flask limits, but we can do it manually if needed
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "upload_failed", "message": "File too large"}), 400

            filename = secure_filename(file.filename)
            original_filename = file.filename
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            
            loader = LoaderManager()
            documents = loader.load(filepath)
            title = filename
            
        elif request.is_json and 'youtube_url' in request.json:
            url = request.json['youtube_url']
            if "youtube.com/watch" not in url and "youtu.be/" not in url:
                return jsonify({"error": "upload_failed", "message": "Invalid YouTube URL"}), 400
                
            loader = YoutubeLoader(url)
            documents = loader.load()
            title = f"YouTube Video ({url})"
            original_filename = title
        else:
            return jsonify({"error": "upload_failed", "message": "No file or youtube_url provided"}), 400

        # Chunking
        chunker = Chunker()
        chunks = chunker.split(documents)
        
        # Store to FAISS
        # We append session_id to metadata
        for chunk in chunks:
            chunk.metadata['session_id'] = session_id
            
        embedder = Embedder()
        vector_store = VectorStore()
        vector_store.add(embedder.model, chunks)
        vector_store.save()

        # Extract text for other generation
        full_text = "\n\n".join(doc.page_content for doc in chunks)
        
        session_store[session_id] = {
            "id": session_id,
            "title": title,
            "original_filename": original_filename,
            "created_at": datetime.now().isoformat(),
            "chunk_count": len(chunks),
            "full_text": full_text,
            "graph": None,
            "notes": None,
            "flashcards": None,
            "quiz": None
        }

        return jsonify({
            "session_id": session_id,
            "title": title,
            "chunk_count": len(chunks),
            "status": "ready"
        })

    except Exception as e:
        return jsonify({"error": "upload_failed", "message": str(e)}), 400
