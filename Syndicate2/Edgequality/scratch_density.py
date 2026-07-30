import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from agents.cultural_translation import cultural_translation_agent
from agents.workbook_generation import workbook_generation_agent

text = """Science Concept: Density

Density is the amount of mass present in a given volume of a substance. It helps us understand why some objects float while others sink. The formula for density is:

Density = Mass / Volume
D = M / V

For example, a metal block has a mass of 200 g and a volume of 50 cm3. Using the formula:

D = 200 / 50 = 4 g/cm3

This means the density of the metal block is 4 g/cm3. Materials with higher density are generally heavier for their size, while materials with lower density are lighter. Scientists use density to identify substances and study the properties of different materials."""

state = cultural_translation_agent({'input_text': text, 'subject': 'Physics', 'target_language': 'tam_Taml'})
print("=== TRANSLATED TAMIL TEXT ===")
print(state['translated_content'])

res = workbook_generation_agent(state)
print("\n=== BILINGUAL WORKBOOK QUESTIONS ===")
questions = res.get('bilingual_questions') or res.get('workbook_questions') or []
if not questions:
    import json
    report_path = 'outputs/reports/workbook_report.json'
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    questions = report.get('bilingual_questions', [])
for q in questions:
    print(f"EN Q{q['id']}: {q['english_question']}")
    print(f"TA Q{q['id']}: {q['regional_question']}\n")
