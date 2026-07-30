import sys
import json
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'c:/Syndicate2/Edgequality')

from graph.workflow import app_workflow

def run_full_pipeline():
    print("=== STARTING FULL PIPELINE TEST ===")
    
    input_text = (
        "Science Concept: Cost Calculation and Multiplication\n\n"
        "John goes to a grocery store and buys 8 apples. Each apple costs $0.75. "
        "To find the total cost, we use the formula:\n\n"
        "Total Cost = Number of Apples x Cost per Apple\n"
        "Total Cost = 8 x $0.75 = $6.00\n\n"
        "Therefore, John pays $6.00 for the apples. This simple calculation uses mathematics "
        "to help us determine the cost of items we buy every day. Multiplication is commonly "
        "used in shopping, budgeting, and business to calculate totals quickly and accurately."
    )
    
    initial_state = {
        "pdf_path": "",
        "input_text": input_text,
        "target_language": "tam_Taml",
        "subject": "Mathematics",
        "textbook_content": "",
        "concepts": [],
        "adapted_content": "",
        "adaptation_log": [],
        "cultural_score": 0.0,
        "translated_content": "",
        "curriculum_alignment": {},
        "verification_result": {},
        "approved": False,
        "workbook_data": {},
        "pdf_bytes": b"",
        "output_pdf_path": ""
    }

    thread_id = "test_full_thread_001"
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. First Pass (Runs up to interrupt before workbook_generation)
    print("\n--- Running Stage 1 (Ingestion to Verification) ---")
    state_stage1 = app_workflow.invoke(initial_state, config=config)
    print(f"Cultural Adaptation Score: {state_stage1.get('cultural_score')}")
    print(f"Adaptation Log Entries: {len(state_stage1.get('adaptation_log', []))}")
    for item in state_stage1.get('adaptation_log', []):
        print(f"  - {item['original']} -> {item['adapted']}")
    print(f"\nAdapted Content Preview:\n{state_stage1.get('adapted_content')[:200]}...")
    print(f"\nTranslated Content Preview:\n{state_stage1.get('translated_content')[:200]}...")

    # 2. Approve and resume workflow for Workbook & PDF generation
    print("\n--- Approving and Resuming Stage 2 (Workbook & PDF Generation) ---")
    app_workflow.update_state(config, {"approved": True})
    final_state = app_workflow.invoke(None, config=config)

    print("\n=== PIPELINE EXECUTION COMPLETE ===")
    print(f"Output PDF Path: {final_state.get('output_pdf_path')}")
    if final_state.get("output_pdf_path") and os.path.exists(final_state.get("output_pdf_path")):
        print(f"PDF Size: {os.path.getsize(final_state.get('output_pdf_path'))} bytes")
    
    return final_state

if __name__ == "__main__":
    run_full_pipeline()
