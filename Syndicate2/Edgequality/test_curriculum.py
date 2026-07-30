import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.curriculum_alignment import curriculum_alignment_agent

test_cases = [
    {
        "subject_name": "Mathematics",
        "subject_input": "Mathematics",
        "input_text": "Unit 4: Algebra & Linear Equations. Solve 3x + 7 = 22 and factorise quadratic expressions (a+b)^2."
    },
    {
        "subject_name": "Mathematics",
        "subject_input": "Math",
        "input_text": "Practical Geometry & Mensuration: Pythagoras theorem, triangles, area and perimeter of rhombus."
    },
    {
        "subject_name": "Mathematics",
        "subject_input": "Arithmetic",
        "input_text": "Commercial Mathematics: Calculate profit, loss, simple interest, compound interest and percentage discount."
    },
    {
        "subject_name": "Physics",
        "subject_input": "Physics",
        "input_text": "Unit 2: Force, Pressure & Newton's Laws of Motion. Calculate acceleration F=ma and atmospheric pressure."
    },
    {
        "subject_name": "Biology",
        "subject_input": "Biology",
        "input_text": "Unit 1: Leaf Anatomy and Chloroplast Structure. Light and dark reactions of photosynthesis."
    },
    {
        "subject_name": "Chemistry",
        "subject_input": "Chemistry",
        "input_text": "Unit 1: Synthetic Fibres and Polymerization. Properties of thermoplastics and thermosetting plastics."
    },
    {
        "subject_name": "Environmental Science",
        "subject_input": "Environmental Science",
        "input_text": "Unit 1: Ecosystems & Western Ghats Biodiversity Hotspot. Wetland conservation and rainwater harvesting."
    },
    {
        "subject_name": "Social Studies",
        "subject_input": "Social Studies",
        "input_text": "Unit 5: Imperial Cholas and Tanjore Big Temple Architecture. Kudavolai village administration system."
    },
    {
        "subject_name": "English Grammar",
        "subject_input": "English Grammar",
        "input_text": "Unit 1: Parts of Speech, Tenses, Active & Passive Voice, and Direct & Indirect Speech."
    }
]

print("=== RUNNING CURRICULUM ALIGNMENT SUITE ===")
all_passed = True
for tc in test_cases:
    expected = tc["subject_name"]
    res = curriculum_alignment_agent({"input_text": tc["input_text"], "subject": tc.get("subject_input", "auto")})
    detected = res.get("detected_subject")
    standards = res.get("matched_standards", [])
    portions = res.get("matched_portions", [])
    objectives = res.get("achieved_objectives", [])
    
    success = (detected == expected)
    if not success:
        all_passed = False
    
    status = "PASSED" if success else "FAILED"
    print(f"[{status}] Input Subj: {tc.get('subject_input')} | Expected: {expected} | Detected: {detected}")
    print(f"   -> Top Standard: {standards[0] if standards else 'None'}")
    print(f"   -> Covered Portions: {len(portions)} | Achieved LOs: {len(objectives)}")
    print("-" * 60)

if all_passed:
    print("SUCCESS: All curriculum alignment tests passed clean!")
else:
    print("WARNING: Some test cases failed.")
