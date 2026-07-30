import unicodedata
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def sanitize_tamil_text(text: str) -> str:
    if not text:
        return ""
    # 1. Canonical NFC composition
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Remove dotted circle placeholders (\u25cc, \u25cb, \u25ef, ○, ◌)
    normalized = re.sub(r'[\u25cc\u25cb\u25ef○◌]', '', normalized)
    
    # 3. Fix duplicate question prefixes like "Q3: Q3" or "[Tamil] Q3: Q3"
    normalized = re.sub(r'\[Tamil\]\s*Q(\d+):\s*Q\1', r'[Tamil] Q\1:', normalized)
    normalized = re.sub(r'Q(\d+):\s*Q\1', r'Q\1:', normalized)
    
    # 4. Fix repeated words like "செய்க செய்க", "நடைமுறை நடைமுறை"
    normalized = re.sub(r'\b(செய்க|நடைமுறை|முறிவு|விவரிப்பு)\s+\1\b', r'\1', normalized)
    
    # 5. Fix mistranslations & raw transliterations
    replacements = [
        (r'பகுப்பாய்வு செய்க சிந்தனை', 'பகுப்பாய்வு சிந்தனை'),
        (r'பகுப்பாய்வு செய்க முறிவு', 'பகுப்பாய்வு விளக்கம்'),
        (r'ஒருங்கிணைக்கப்பட்ட முறிவு', 'தொகுப்பு முடிவு'),
        (r'நடைமுறை நடைமுறை', 'நடைமுறை'),
        (r'வகைீம்', 'வேகம்'),
        (r'வகீம்', 'வேகம்'),
        (r'நரேம்', 'நேரம்'),
        (r'தூரம்', 'தொலைவு'),
        (r'ஆட்டோ', 'பாடப்பகுதி'),
        (r'ஆட்டோ', 'பாடப்பகுதி'),
        (r'விண்ணப்பம்', 'நடைமுறை பயன்பாடு'),
        (r'விண்ணப்பிக்கவும்', 'பயன்படுத்துக'),
        (r'ரீசனிங்', 'சிந்தனை'),
        (r'கரத்த', 'கருத்து'),
        (r'நினைவூட்டல்', 'நினைவுகூருதல்'),
        (r'நினைவுதூர்க', 'நினைவுகூர்க'),
        (r'நினைவுதுர்க', 'நினைவுகூர்க')
    ]
    for p, r in replacements:
        normalized = re.sub(p, r, normalized)
        
    return unicodedata.normalize("NFC", normalized)

test_q = '[Tamil] Q3: Q3 [பயன்படுத்துக] (பகுப்பாய்வு செய்க சிந்தனை): இதில் விவரிக்கப்பட்டுள்ள முக்கிய மாறிகள், உறவுகள் மற்றும் வழிமுறைகளை பகுப்பாய்வு செய்க செய்யவும்: "வேகம் (v) = தூரம் (d) ÷ நேரம் (t) சூத்திரத்தைப் பயன்படுத்தி, நாம் v = 12 ÷ 1 = 12 km/h கணக்கிடுகிறோம்.'
print("Original:", test_q)
print("Sanitized:", sanitize_tamil_text(test_q))
