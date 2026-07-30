from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    # Inputs
    pdf_path: str
    target_language: str
    input_text: Optional[str]
    subject: Optional[str]
    
    # Agent 1 - Ingestion
    textbook_content: str
    chapters: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    figures: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    chunks: List[str]
    
    # Agent 2 - Concept Extraction
    concepts: List[str]
    definitions: List[Dict[str, str]]
    formulas: List[str]
    concept_graph: List[Dict[str, str]]
    chapter_summaries: str
    
    # Agent 3 - Cultural Adaptation
    adapted_content: str
    adaptation_log: List[Dict[str, str]]
    cultural_score: float
    
    # Agent 4 - Translation
    translated_content: str
    terminology_log: List[Dict[str, str]]
    translation_score: float
    
    # Agent 5 - Curriculum Alignment
    match_score: float
    portions_score: float
    objectives_score: float
    detected_subject: str
    matched_standards: List[str]
    matched_portions: List[str]
    uncovered_portions: List[str]
    achieved_objectives: List[str]
    unfulfilled_objectives: List[str]
    missing_topics: List[str]
    improvement_suggestions: List[str]
    curriculum_report: str
    
    # Agent 6 - Verification
    accuracy_score: float
    confidence_score: float
    verification_report: str
    detected_errors: List[Dict[str, str]]
    
    # Agent 7 - Workbook Generation
    workbook_questions: List[Dict[str, Any]]
    answer_key: List[Dict[str, Any]]
    difficulty_levels: Dict[str, int]
    
    # Final Output Paths
    localized_textbook_pdf: str
    workbook_pdf: str
