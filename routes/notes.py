from flask import Blueprint, jsonify, request
import json
from routes.store import session_store
from llm.generator import Generator
from agents.prompts import NOTES_PROMPT

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/notes/<session_id>', methods=['GET'])
def get_notes(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    notes = session_store[session_id].get("notes")
    if not notes:
        return jsonify({"points": []})
    return jsonify(notes)

@notes_bp.route('/notes/generate/<session_id>', methods=['POST'])
def generate_notes(session_id):
    if session_id not in session_store:
        return jsonify({"error": "not_found"}), 404
        
    full_text = session_store[session_id].get("full_text", "")[:6000]
    if not full_text:
        return jsonify({"error": "no_text"}), 400
        
    generator = Generator(json_mode=True)
    try:
        res = generator.chain.invoke({"context": full_text, "question": NOTES_PROMPT})
        from utils.json_helper import extract_json
        notes = extract_json(res)
        if notes:
            session_data = session_store[session_id]
            session_data["notes"] = notes
            session_store[session_id] = session_data
            return jsonify(notes)
    except Exception as e:
        return jsonify({"error": "generation_failed", "message": str(e)}), 500
        
    return jsonify({"points": []})
