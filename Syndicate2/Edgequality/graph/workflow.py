from langgraph.graph import StateGraph, END
from .state import GraphState
from agents.ingestion import ingestion_agent
from agents.concept_extraction import concept_extraction_agent
from agents.cultural_translation import cultural_translation_agent
from agents.curriculum_alignment import curriculum_alignment_agent
from agents.verification import verification_agent
from agents.workbook_generation import workbook_generation_agent

from langgraph.checkpoint.memory import MemorySaver

def build_workflow():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("ingestion", ingestion_agent)
    workflow.add_node("concept_extraction", concept_extraction_agent)
    workflow.add_node("cultural_translation", cultural_translation_agent)
    workflow.add_node("curriculum_alignment", curriculum_alignment_agent)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("workbook_generation", workbook_generation_agent)
    
    # Define edges
    workflow.set_entry_point("ingestion")
    workflow.add_edge("ingestion", "concept_extraction")
    workflow.add_edge("concept_extraction", "cultural_translation")
    workflow.add_edge("cultural_translation", "curriculum_alignment")
    workflow.add_edge("curriculum_alignment", "verification")
    workflow.add_edge("verification", "workbook_generation")
    workflow.add_edge("workbook_generation", END)
    
    # Add checkpointer
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory, interrupt_before=["workbook_generation"])

# Global compiled graph
app_workflow = build_workflow()
