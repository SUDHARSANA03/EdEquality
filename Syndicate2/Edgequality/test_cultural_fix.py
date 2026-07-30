import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from agents.cultural_translation import perform_cultural_adaptation, translate_text_http, clean_and_normalize_tamil_text

# Test with the ACTUAL source text from adaptation_report.json
source = (
    "Science Concept: Cost Calculation and Multiplication\n\n"
    "John goes to a grocery store and buys 8 apples. Each apple costs $0.75. "
    "To find the total cost, we use the formula:\n\n"
    "Total Cost = Number of Apples x Cost per Apple\n"
    "Total Cost = 8 x $0.75 = $6.00\n\n"
    "Therefore, John pays $6.00 for the apples. This simple calculation uses mathematics "
    "to help us determine the cost of items we buy every day. Multiplication is commonly "
    "used in shopping, budgeting, and business to calculate totals quickly and accurately."
)

print("=== CULTURAL ADAPTATION RESULT ===")
adapted, log, score = perform_cultural_adaptation(source)
print(adapted)
print()
print("=== ADAPTATION LOG ===")
for entry in log:
    print(f"  {entry['original']} -> {entry['adapted']}")
print(f"\nScore: {score}")
print()

print("=== TAMIL TRANSLATION TEST ===")
tamil = translate_text_http(adapted, "ta")
print(tamil)
print()

print("=== TAMIL CORRECTIONS TEST ===")
raw_with_shopping = "ஷாப்பிங், பட்ஜெட் மற்றும் வணிகத்தில் பெருக்கல் பொதுவாகப் பயன்படுத்தப்படுகிறது."
raw_with_breakdown = "பகுப்பாய்வு முறிவு: அடர்த்திக்கான சூத்திரம்"
corrected_shopping = clean_and_normalize_tamil_text(raw_with_shopping)
corrected_breakdown = clean_and_normalize_tamil_text(raw_with_breakdown)
print(f"  Input:  {raw_with_shopping}")
print(f"  Fixed:  {corrected_shopping}")
print()
print(f"  Input:  {raw_with_breakdown}")
print(f"  Fixed:  {corrected_breakdown}")
