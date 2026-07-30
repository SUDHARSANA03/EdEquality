import unicodedata
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_and_normalize_tamil_text(text: str) -> str:
    if not text:
        return ""
    
    # 1. Canonical NFC Composition
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Fix Bloom's Taxonomy English-to-Tamil Translation Mappings
    blooms_map = [
        (r'\[நினைவில் க[\u25cc\u25cb\u25ef○◌]*ாள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[நினைவில் கொள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[நினைவில் கொள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[புரிந்த க[\u25cc\u25cb\u25ef○◌]*ாள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்த கொள்ளுங்கள்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்த கொள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்துகொள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[பயன்படுத்தக\]', '[பயன்படுத்துக]'),
        (r'\[பகுப்பாய்வு செய்க\]', '[பகுப்பாய்வு]'),
        (r'\[மதிப்பீடு\]', '[மதிப்பிடுக]'),
    ]
    for p, r in blooms_map:
        normalized = re.sub(p, r, normalized)

    # 3. Clean up bad machine translation jargon & repetitive phrases
    corrections = [
        (r'(நடைமுறை\s*){2,}', 'நடைமுறை '),
        (r'(செய்க\s*){2,}', 'செய்க '),
        (r'வேக\s+வேகம்', 'வேகம்'),
        (r'வேகம்\s+வேகம்', 'வேகம்'),
        (r'கரத்த நினைவூதுரதல்', 'கருத்து நினைவுகூருதல்'),
        (r'கரத்த நினைவுகூர்தல்', 'கருத்து நினைவுகூருதல்'),
        (r'கருத்த நினைவுகூர்தல்', 'கருத்து நினைவுகூருதல்'),
        (r'நினைவூட்டல்', 'நினைவுகூருதல்'),
        (r'பிரச்சினையைத் தீர்ப்பத', 'பிரச்சினையைத் தீர்த்தல்'),
        (r'பிரச்சனைகளைத் தீர்க்க', 'சிக்கல்களைத் தீர்த்தல்'),
        (r'பகுப்பாய்வு செய்க சிந்தனை', 'பகுப்பாய்வு சிந்தனை'),
        (r'ஒருங்கிணைக்கப்பட்ட முறிவு', 'தொகுப்பு முடிவு'),
        (r'விமர்சன ரீதியான மதிப்பீடு', 'விமர்சன மதிப்பீடு'),
        (r'டிக்கிய', 'முக்கிய'),
        (r'டிாிவு', 'தீர்வு'),
        (r'டிடிவு', 'முடிவு'),
    ]
    for p, r in corrections:
        normalized = re.sub(p, r, normalized)

    # 4. Remove lingering dotted circle placeholders (\u25cc, \u25cb, \u25ef, ○, ◌)
    normalized = re.sub(r'[\u25cc\u25cb\u25ef○◌]', '', normalized)

    # 5. Two-part Indic Vowel Sign Decomposition to prevent FPDF2 dotted-circle glyph artifacts
    normalized = normalized.replace('\u0bca', '\u0bc6\u0bbe')  # ொ -> ெ + ா
    normalized = normalized.replace('\u0bcb', '\u0bc7\u0bbe')  # ோ -> ே + ா
    normalized = normalized.replace('\u0bcc', '\u0bc6\u0bd7')  # ௌ -> ெ + ௗ

    return unicodedata.normalize("NFC", normalized)

test_q1 = '[Tamil] Q1: [நினைவில் க○ாள்ளுங்கள்] (கரத்த நினைவூதுரதல்): இயற்பியல் பிரிவின் அடிப்படையில், முக்கிய அறிக்கையை வரையறுத்து விளக்கவும்: "அறிவியல் கருத்து: வேக வேகம் என்பது ஒரு குறிப்பிட்ட நேரத்தில் ஒரு பொருள் பயணிக்கும் தொலைவு".'
test_q4 = '[Tamil] Q4: [பகுப்பாய்வு] (விமர்சன ரீதியான மதிப்பீடு): நவீன இயற்பியல் நடைமுறை நடைமுறை நடைமுறை பயன்பாடுகளில் "சூத்திரத்தைப் பயன்படுத்துதல்: v = 240 ÷ 4 = 60..." என்பதன் முக்கியத்துவத்தை மதிப்பிடவும்.'

print("SAN Q1:", clean_and_normalize_tamil_text(test_q1))
print("SAN Q4:", clean_and_normalize_tamil_text(test_q4))
