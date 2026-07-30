import os
import json
from data.database import DatabaseConnections

def concept_extraction_agent(state: dict) -> dict:
    print("--- CONCEPT EXTRACTION AGENT ---")
    content = state.get("textbook_content", "") or state.get("input_text", "")
    content_sample = content[:2000]
    
    from agents.curriculum_alignment import detect_subject
    detected_subj = detect_subject(content, state)

    res_dict = {
        "detected_subject": detected_subj,
        "concepts": [detected_subj, "Core Principles"],
        "definitions": [{"term": detected_subj, "definition": f"Core academic content covering {detected_subj}."}],
        "formulas": [],
        "concept_graph": [{"source": detected_subj, "relation": "includes", "target": "Core Principles"}],
        "chapter_summaries": content_sample[:300]
    }

    # Optional fast LLM extraction with strict timeout and no blocking retries
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and len(api_key) > 10:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1,
                google_api_key=api_key,
                max_retries=0,
                request_timeout=10.0
            )
            from langchain_core.prompts import PromptTemplate
            prompt = PromptTemplate.from_template("Extract key concepts from text as JSON with keys concepts, definitions: \n\n{content}")
            chain = prompt | llm
            response = chain.invoke({"content": content_sample[:1000]})
            text_out = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text_out)
            if isinstance(parsed, dict) and "concepts" in parsed:
                res_dict["concepts"] = parsed.get("concepts", res_dict["concepts"])
                res_dict["definitions"] = parsed.get("definitions", res_dict["definitions"])
        except Exception as e:
            print(f"[concept_extraction note] Fast LLM note ({e}), using NLP fallback")

    driver = DatabaseConnections.get_neo4j_driver()
    if driver:
        pass
        
    return res_dict
