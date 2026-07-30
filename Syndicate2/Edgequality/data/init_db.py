import os
import json
import chromadb

def init_chroma():
    print("Initializing ChromaDB...")
    # Initialize Chroma client
    client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(__file__), "chromadb"))
    
    # 1. Initialize Curriculum Collection
    curriculum_collection = client.get_or_create_collection(name="curriculum")
    curriculum_file = os.path.join(os.path.dirname(__file__), "curriculum", "sample_standards.json")
    
    if os.path.exists(curriculum_file):
        with open(curriculum_file, "r", encoding="utf-8") as f:
            standards = json.load(f)
            
        ids = [std["id"] for std in standards]
        documents = [f"[{std.get('state_board', 'General State Board')}] {std['subject']} Grade {std['grade']} - {std['domain']}: {std['description']} (Keywords: {', '.join(std.get('keywords', []))})" for std in standards]
        metadatas = [{
            "state_board": std.get("state_board", "General State Board"),
            "subject": std["subject"],
            "grade": std["grade"],
            "domain": std["domain"]
        } for std in standards]
        
        curriculum_collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Inserted {len(standards)} standards into 'curriculum' collection.")
    else:
        print(f"Curriculum file not found: {curriculum_file}")

    # 2. Initialize Glossary Collection
    glossary_collection = client.get_or_create_collection(name="glossary")
    glossary_file = os.path.join(os.path.dirname(__file__), "glossary", "sample_glossary.json")
    
    if os.path.exists(glossary_file):
        with open(glossary_file, "r", encoding="utf-8") as f:
            glossary = json.load(f)
            
        ids = list(glossary.keys())
        documents = [f"{term}: {definition}" for term, definition in glossary.items()]
        
        glossary_collection.upsert(
            documents=documents,
            ids=ids
        )
        print(f"Inserted {len(glossary)} terms into 'glossary' collection.")
    else:
        print(f"Glossary file not found: {glossary_file}")
        
    print("ChromaDB initialization complete.")

if __name__ == "__main__":
    init_chroma()
