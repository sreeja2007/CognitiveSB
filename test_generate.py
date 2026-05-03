import os
import json
from dotenv import load_dotenv

# Load env before importing other things
load_dotenv()

from llm.generator import Generator
from agents.prompts import NOTES_PROMPT, FLASHCARD_GENERATION_PROMPT, QUIZ_MCQ_PROMPT
from utils.json_helper import extract_json

def test_generation():
    print("Initializing Generator...")
    try:
        generator = Generator(json_mode=True)
    except Exception as e:
        print(f"Failed to initialize generator: {e}")
        return

    # A short text to avoid rate limits
    sample_text = """
    Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. Some of this chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water – hence the name photosynthesis, from the Greek phōs, "light", and sunthesis, "putting together".
    """

    print("\n--- Testing NOTES Generation ---")
    try:
        prompt = NOTES_PROMPT
        print("Prompt compiled successfully.")
        
        print("Sending request to LLM...")
        raw_res = generator.chain.invoke({"context": sample_text, "question": prompt})
        
        print("\nRAW LLM OUTPUT:")
        print("-" * 40)
        print(raw_res.encode('ascii', 'replace').decode('ascii'))
        print("-" * 40)
        
        print("\nAttempting JSON Extraction...")
        extracted = extract_json(raw_res)
        print(json.dumps(extracted, indent=2))
        
    except Exception as e:
        print(f"EXCEPTION OCCURRED: {e}")

    print("\n--- Testing FLASHCARDS Generation ---")
    try:
        prompt = FLASHCARD_GENERATION_PROMPT
        print("Sending request to LLM...")
        raw_res = generator.chain.invoke({"context": sample_text, "question": prompt})
        print("\nRAW LLM OUTPUT:")
        print(raw_res.encode('ascii', 'replace').decode('ascii'))
        print("\nAttempting JSON Extraction...")
        print(json.dumps(extract_json(raw_res), indent=2))
    except Exception as e:
        print(f"EXCEPTION OCCURRED: {e}")

    print("\n--- Testing QUIZ Generation ---")
    try:
        prompt = QUIZ_MCQ_PROMPT
        print("Sending request to LLM...")
        raw_res = generator.chain.invoke({"context": sample_text, "question": prompt})
        print("\nRAW LLM OUTPUT:")
        print(raw_res.encode('ascii', 'replace').decode('ascii'))
        print("\nAttempting JSON Extraction...")
        print(json.dumps(extract_json(raw_res), indent=2))
    except Exception as e:
        print(f"EXCEPTION OCCURRED: {e}")

if __name__ == "__main__":
    test_generation()
