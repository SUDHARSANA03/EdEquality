import os
import pdfplumber
import pytesseract
from typing import Dict, Any

def ingestion_agent(state: dict) -> dict:
    print("--- INGESTION AGENT ---")
    pdf_path = state.get("pdf_path")
    input_text = state.get("input_text")
    
    # Mocking PDF Parcel functionality with pdfplumber and tesseract
    textbook_content = ""
    chunks = []
    
    if input_text and input_text.strip():
        textbook_content = input_text
        chunks = [input_text[i:i+1000] for i in range(0, len(input_text), 1000)] if len(input_text) > 1000 else [input_text]
    elif pdf_path and os.path.exists(pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        textbook_content += text + "\n"
                        chunks.append(text)
                    else:
                        # Fallback to OCR if scanned
                        pass
        except Exception as e:
            textbook_content = f"Error parsing PDF: {e}"
    else:
        textbook_content = "Mock extracted content for testing."
        chunks = ["Mock chunk 1", "Mock chunk 2"]
        
    return {
        "textbook_content": textbook_content,
        "chapters": [{"title": "Chapter 1: Intro"}],
        "sections": [{"title": "1.1 Overview"}],
        "figures": [],
        "tables": [],
        "metadata": {"pages": len(chunks) if chunks else 1},
        "chunks": chunks
    }
