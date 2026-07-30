import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GLOSSARY_DICTIONARY = {
    # ── Mathematics ───────────────────────────────────────────────────────────
    "mathematics": {
        "ta": "கணிதம்", "hi": "गणित", "te": "గణితం", "kn": "ಗಣಿತ", "ml": "ഗണിതം"
    },
    "algebra": {
        "ta": "இயற்கணிதம்", "hi": "बीजगणित", "te": "బీజగణితం", "kn": "ಬೀಜಗಣಿತ", "ml": "ബീജഗണിതം"
    },
    "equation": {
        "ta": "சமன்பாடு", "hi": "समीकरण", "te": "సమీకరణం", "kn": "ಸಮೀಕರಣ", "ml": "സമവാക്യം"
    },
    "geometry": {
        "ta": "வடிவியல்", "hi": "ज्यामिति", "te": "రేఖాగణితం", "kn": "ಜ್ಯಾಮಿತಿ", "ml": "ജ്യാമിതി"
    },
    "fraction": {
        "ta": "பின்னம்", "hi": "भिन्न", "te": "భిన్నం", "kn": "ಭಿನ್ನ", "ml": "ഭിന്നം"
    },
    "integer": {
        "ta": "முழு எண்", "hi": "पूर्णांक", "te": "పూర్ణాంకం", "kn": "ಪೂರ್ಣಾಂಕ", "ml": "പൂർണ്ണസംഖ്യ"
    },
    "arithmetic": {
        "ta": "எண்கணிதம்", "hi": "अंकगणित", "te": "అంకగణితం", "kn": "ಅಂಕಗಣಿತ", "ml": "ഗണിതം"
    },
    "ratio": {
        "ta": "விகிதம்", "hi": "अनुपात", "te": "నిష్పత్తి", "kn": "ಅನುಪಾತ", "ml": "അനുപാതം"
    },
    "percentage": {
        "ta": "சதவீதம்", "hi": "प्रतिशत", "te": "శాతం", "kn": "ಶೇಕಡಾ", "ml": "ശതമാനം"
    },
    "triangle": {
        "ta": "முக்கோணம்", "hi": "त्रिभुज", "te": "త్రిభుజం", "kn": "ತ್ರಿಭುಜ", "ml": "ത്രികോണം"
    },
    "circle": {
        "ta": "வட்டம்", "hi": "वृत्त", "te": "వృత్తం", "kn": "ವೃತ್ತ", "ml": "വൃത്തം"
    },
    "area": {
        "ta": "பரப்பளவு", "hi": "क्षेत्रफल", "te": "వైశాల్యం", "kn": "ವಿಸ್ತೀರ್ಣ", "ml": "വിസ്തീർണ്ണം"
    },
    "volume": {
        "ta": "கனவளவு", "hi": "आयतन", "te": "ఘనపరిమాణం", "kn": "ಘನಫಲ", "ml": "ആയതനം"
    },
    "probability": {
        "ta": "நிகழ்தகவு", "hi": "संभावना", "te": "సంభావ్యత", "kn": "ಸಂಭಾವ್ಯತೆ", "ml": "സംഭാവ്യത"
    },
    "statistics": {
        "ta": "புள்ளியியல்", "hi": "सांख्यिकी", "te": "గణాంకశాస్త్రం", "kn": "ಸಂಖ್ಯಾಶಾಸ್ತ್ರ", "ml": "സ്ഥിതിവിവരക്കണക്ക്"
    },
    "variable": {
        "ta": "மாறி", "hi": "चर", "te": "చరరాశి", "kn": "ಅಸ್ಥಿರ", "ml": "ചരം"
    },
    "coefficient": {
        "ta": "குணகம்", "hi": "गुणांक", "te": "గుణకం", "kn": "ಗುಣಾಂಕ", "ml": "ഗുണകം"
    },
    "polynomial": {
        "ta": "பல்லுறுப்புக்கோவை", "hi": "बहुपद", "te": "బహుపది", "kn": "ಬಹುಪದ", "ml": "ബഹുപദം"
    },
    "calculus": {
        "ta": "நுண்கணிதம்", "hi": "कलन", "te": "కాలిక్యులస్", "kn": "ಕಲನ", "ml": "കാൽക്കുലസ്"
    },
    "trigonometry": {
        "ta": "முக்கோணவியல்", "hi": "त्रिकोणमिति", "te": "త్రిభుజమితి", "kn": "ತ್ರಿಕೋಣಮಿತಿ", "ml": "ത്രികോണമിതി"
    },
    # ── Physics ───────────────────────────────────────────────────────────────
    "physics": {
        "ta": "இயற்பியல்", "hi": "भौतिकी", "te": "భౌతికశాస్త్రం", "kn": "ಭೌತಶಾಸ್ತ್ರ", "ml": "ഭൗതികശാസ്ത്രം"
    },
    "gravity": {
        "ta": "ஈர்ப்பு விசை", "hi": "गुरुत्वाकर्षण", "te": "గురుత్వాకర్షణ", "kn": "ಗುರುತ್ವಾಕರ್ಷಣೆ", "ml": "ഗുരുത്വാകർഷണം"
    },
    "friction": {
        "ta": "உராய்வு", "hi": "घर्षण", "te": "ఘర్షణ", "kn": "ಘರ್ಷಣೆ", "ml": "ഘർഷണം"
    },
    "energy": {
        "ta": "ஆற்றல்", "hi": "ऊर्जा", "te": "శక్తి", "kn": "ಶಕ್ತಿ", "ml": "ഊർജ്ജം"
    },
    "force": {
        "ta": "விசை", "hi": "बल", "te": "బలం", "kn": "ಬಲ", "ml": "ബലം"
    },
    "acceleration": {
        "ta": "முடுக்கம்", "hi": "त्वरण", "te": "త్వరణం", "kn": "ತ್ವರಣ", "ml": "ത്വരണം"
    },
    "velocity": {
        "ta": "திசைவேகம்", "hi": "वेग", "te": "వేగం", "kn": "ವೇಗ", "ml": "പ്രവേഗം"
    },
    "momentum": {
        "ta": "உந்தம்", "hi": "संवेग", "te": "ద్రవ్యవేగం", "kn": "ಆವೇಗ", "ml": "ആക്കം"
    },
    "pressure": {
        "ta": "அழுத்தம்", "hi": "दबाव", "te": "పీడనం", "kn": "ಒತ್ತಡ", "ml": "മർദ്ദം"
    },
    "density": {
        "ta": "அடர்த்தி", "hi": "घनत्व", "te": "సాంద్రత", "kn": "ಸಾಂದ್ರತೆ", "ml": "സാന്ദ്രത"
    },
    "wave": {
        "ta": "அலை", "hi": "तरंग", "te": "తరంగం", "kn": "ತರಂಗ", "ml": "തരംഗം"
    },
    "electricity": {
        "ta": "மின்சாரம்", "hi": "विद्युत", "te": "విద్యుత్తు", "kn": "ವಿದ್ಯುತ್", "ml": "വൈദ്യുതി"
    },
    "magnetism": {
        "ta": "காந்தவியல்", "hi": "चुम्बकत्व", "te": "అయస్కాంతత్వం", "kn": "ಚುಂಬಕತ್ವ", "ml": "കാന്തികത"
    },
    "motion": {
        "ta": "இயக்கம்", "hi": "गति", "te": "చలనం", "kn": "ಚಲನೆ", "ml": "ചലനം"
    },
    "optics": {
        "ta": "ஒளியியல்", "hi": "प्रकाशिकी", "te": "కాంతిశాస్త్రం", "kn": "ದ್ಯುತಿಶಾಸ್ತ್ರ", "ml": "പ്രകാശശാസ്ത്രം"
    },
    "refraction": {
        "ta": "ஒளிவிலகல்", "hi": "अपवर्तन", "te": "వక్రీభవనం", "kn": "ವಕ್ರೀಭವನ", "ml": "അപവർത്തനം"
    },
    "thermodynamics": {
        "ta": "வெப்பவியக்கவியல்", "hi": "ऊष्मागतिकी", "te": "ఉష్ణగతిశాస్త్రం", "kn": "ಉಷ್ಣಗತಿಶಾಸ್ತ್ರ", "ml": "താപഗതികം"
    },
    # ── Chemistry ─────────────────────────────────────────────────────────────
    "chemistry": {
        "ta": "வேதியியல்", "hi": "रसायन विज्ञान", "te": "రసాయనశాస్త్రం", "kn": "ರಸಾಯನಶಾಸ್ತ್ರ", "ml": "രസതന്ത്രം"
    },
    "atom": {
        "ta": "அணு", "hi": "परमाणु", "te": "పరమాణువు", "kn": "ಪರಮಾಣು", "ml": "ആറ്റം"
    },
    "molecule": {
        "ta": "மூலக்கூறு", "hi": "अणु", "te": "అణువు", "kn": "ಅಣು", "ml": "തന്മാത്ര"
    },
    "element": {
        "ta": "தனிமம்", "hi": "तत्व", "te": "మూలకం", "kn": "ಮೂಲಧಾತು", "ml": "മൂലകം"
    },
    "compound": {
        "ta": "சேர்மம்", "hi": "यौगिक", "te": "సమ్మేళనం", "kn": "ಸಂಯುಕ್ತ", "ml": "സംയൗഗികം"
    },
    "acid": {
        "ta": "அமிலம்", "hi": "अम्ल", "te": "ఆమ్లం", "kn": "ಆಮ್ಲ", "ml": "ആസിഡ്"
    },
    "base": {
        "ta": "காரம்", "hi": "क्षार", "te": "క్షారం", "kn": "ಕ್ಷಾರ", "ml": "ക്ഷാരം"
    },
    "reaction": {
        "ta": "வினை", "hi": "अभिक्रिया", "te": "చర్య", "kn": "ಪ್ರತಿಕ್ರಿಯೆ", "ml": "പ്രതിക്രിയ"
    },
    "oxidation": {
        "ta": "ஆக்சிஜனேற்றம்", "hi": "ऑक्सीकरण", "te": "ఆక్సీకరణం", "kn": "ಆಕ್ಸಿಡೀಕರಣ", "ml": "ഓക്സീകരണം"
    },
    "ion": {
        "ta": "அயனி", "hi": "आयन", "te": "అయాన్", "kn": "ಅಯಾನ್", "ml": "അയോൺ"
    },
    "bond": {
        "ta": "பிணைப்பு", "hi": "बंधन", "te": "బంధం", "kn": "ಬಂಧ", "ml": "ബന്ധം"
    },
    # ── Biology ───────────────────────────────────────────────────────────────
    "biology": {
        "ta": "உயிரியல்", "hi": "जीव विज्ञान", "te": "జీవశాస్త్రం", "kn": "ಜೀವಶಾಸ್ತ್ರ", "ml": "ജീവശാസ്ത്രം"
    },
    "cell": {
        "ta": "செல்", "hi": "कोशिका", "te": "కణం", "kn": "ಕೋಶ", "ml": "കോശം"
    },
    "photosynthesis": {
        "ta": "ஒளிச்சேர்க்கை", "hi": "प्रकाश संश्लेषण", "te": "కిరణజన్య సంయోగక్రియ", "kn": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ", "ml": "പ്രകാശസംശ്ലേഷണം"
    },
    "ecosystem": {
        "ta": "சூழ்நிலை மண்டலம்", "hi": "पारिस्थितिकी तंत्र", "te": "పర్యావరణ వ్యవస్థ", "kn": "ಪರಿಸರ ವ್ಯವಸ್ಥೆ", "ml": "ആവാസവ്യൂഹം"
    },
    "genetics": {
        "ta": "மரபியல்", "hi": "आनुवंशिकी", "te": "జన్యుశాస్త్రం", "kn": "ಆನುವಂಶಿಕಶಾಸ್ತ್ರ", "ml": "ജനിതകശാസ്ത്രം"
    },
    "evolution": {
        "ta": "பரிணாமம்", "hi": "विकास", "te": "పరిణామం", "kn": "ವಿಕಾಸ", "ml": "പരിണാമം"
    },
    "organism": {
        "ta": "உயிரினம்", "hi": "जीव", "te": "జీవి", "kn": "ಜೀವಿ", "ml": "ജീവി"
    },
    "mitosis": {
        "ta": "சம பிரிவு", "hi": "समसूत्रण", "te": "మైటోసిస్", "kn": "ಮೈಟೋಸಿಸ್", "ml": "മൈറ്റോസിസ്"
    },
    "chromosome": {
        "ta": "குரோமோசோம்", "hi": "गुणसूत्र", "te": "క్రోమోజోమ్", "kn": "ಕ್ರೊಮೋಸೋಮ್", "ml": "ക്രോമോസോം"
    },
    # ── English Grammar ───────────────────────────────────────────────────────
    "grammar": {
        "ta": "இலக்கணம்", "hi": "व्याकरण", "te": "వ్యాకరణం", "kn": "ವ್ಯಾಕರಣ", "ml": "വ്യാകരണം"
    },
    "noun": {
        "ta": "பெயர்ச்சொல்", "hi": "संज्ञा", "te": "నామవాచకం", "kn": "ನಾಮಪದ", "ml": "നാമം"
    },
    "verb": {
        "ta": "வினைச்சொல்", "hi": "क्रिया", "te": "క్రియ", "kn": "ಕ್ರಿಯಾಪದ", "ml": "ക്രിയ"
    },
    "adjective": {
        "ta": "உரிச்சொல்", "hi": "विशेषण", "te": "విశేషణం", "kn": "ವಿಶೇಷಣ", "ml": "വിശേഷണം"
    },
    "pronoun": {
        "ta": "பிரதிப்பெயர்", "hi": "सर्वनाम", "te": "సర్వనామం", "kn": "ಸರ್ವನಾಮ", "ml": "സർവ്വനാമം"
    },
    "adverb": {
        "ta": "வினையுரிச்சொல்", "hi": "क्रिया विशेषण", "te": "క్రియా విశేషణం", "kn": "ಕ್ರಿಯಾ ವಿಶೇಷಣ", "ml": "ക്രിയാവിശേഷണം"
    },
    "conjunction": {
        "ta": "இணைப்பிடை", "hi": "समुच्चयबोधक", "te": "సంయోజకం", "kn": "ಸಂಯೋಜಕ", "ml": "സംബന്ധകം"
    },
    "preposition": {
        "ta": "முன்னிலைச்சொல்", "hi": "पूर्वसर्ग", "te": "విభక్తి", "kn": "ಪೂರ್ವಪ್ರತ್ಯಯ", "ml": "പൂർവ്വകം"
    },
    "tense": {
        "ta": "காலம்", "hi": "काल", "te": "కాలం", "kn": "ಕಾಲ", "ml": "കാലം"
    },
    "syntax": {
        "ta": "தொடரியல்", "hi": "वाक्यविन्यास", "te": "వాక్యనిర్మాణం", "kn": "ವಾಕ್ಯರಚನೆ", "ml": "വാക്യഘടന"
    },
    "vocabulary": {
        "ta": "சொல்லகராதி", "hi": "शब्द भंडार", "te": "పదజాలం", "kn": "ಶಬ್ದಭಂಡಾರ", "ml": "പദശേഖരം"
    },
    # ── History & Social Science ───────────────────────────────────────────────
    "democracy": {
        "ta": "ஜனநாயகம்", "hi": "लोकतंत्र", "te": "ప్రజాస్వామ్యం", "kn": "ಪ್ರಜಾಪ್ರಭುತ್ವ", "ml": "ജനാധിപത്യം"
    },
    "constitution": {
        "ta": "அரசியலமைப்பு", "hi": "संविधान", "te": "రాజ్యాంగం", "kn": "ಸಂವಿಧಾನ", "ml": "ഭരണഘടന"
    },
    "civilization": {
        "ta": "நாகரிகம்", "hi": "सभ्यता", "te": "నాగరికత", "kn": "ನಾಗರಿಕತೆ", "ml": "നാഗരികത"
    },
    "revolution": {
        "ta": "புரட்சி", "hi": "क्रांति", "te": "విప్లవం", "kn": "ಕ್ರಾಂತಿ", "ml": "വിപ്ലവം"
    },
    # ── Geography ─────────────────────────────────────────────────────────────
    "latitude": {
        "ta": "அட்சரேகை", "hi": "अक्षांश", "te": "అక్షాంశం", "kn": "ಅಕ್ಷಾಂಶ", "ml": "അക്ഷാംശം"
    },
    "longitude": {
        "ta": "தீர்க்கரேகை", "hi": "देशांतर", "te": "రేఖాంశం", "kn": "ರೇಖಾಂಶ", "ml": "രേഖാംശം"
    },
    "erosion": {
        "ta": "அரிப்பு", "hi": "अपरदन", "te": "కోత", "kn": "ಸವೆತ", "ml": "ക്ഷയം"
    },
    "climate": {
        "ta": "காலநிலை", "hi": "जलवायु", "te": "వాతావరణం", "kn": "ಹವಾಮಾನ", "ml": "കാലാവസ്ഥ"
    },
    # ── Computer Science ─────────────────────────────────────────────────────
    "algorithm": {
        "ta": "வழிமுறை", "hi": "एल्गोरिदम", "te": "అల్గోరిథమ్", "kn": "ಅಲ್ಗಾರಿದಮ್", "ml": "അൽഗോരിതം"
    },
    "program": {
        "ta": "நிரல்", "hi": "प्रोग्राम", "te": "ప్రోగ్రామ్", "kn": "ಕಾರ್ಯಕ್ರಮ", "ml": "പ്രോഗ്രാം"
    },
    "database": {
        "ta": "தரவுத்தளம்", "hi": "डेटाबेस", "te": "డేటాబేస్", "kn": "ದತ್ತಾಂಶ", "ml": "ഡേറ്റാബേസ്"
    },
    "network": {
        "ta": "வலைப்பின்னல்", "hi": "नेटवर्क", "te": "నెట్వర్క్", "kn": "ಜಾಲ", "ml": "നെറ്റ്‌വർക്ക്"
    },
    # ── General Science ───────────────────────────────────────────────────────
    "science": {
        "ta": "அறிவியல்", "hi": "विज्ञान", "te": "శాస్త్రం", "kn": "ವಿಜ್ಞಾನ", "ml": "ശാസ്ത്രം"
    },
    "hypothesis": {
        "ta": "கருதுகோள்", "hi": "परिकल्पना", "te": "పరికల్పన", "kn": "ಊಹೆ", "ml": "പ്രകൽപ്പന"
    },
    "experiment": {
        "ta": "பரிசோதனை", "hi": "प्रयोग", "te": "ప్రయోగం", "kn": "ಪ್ರಯೋಗ", "ml": "പരീക്ഷണം"
    },
    "theory": {
        "ta": "கோட்பாடு", "hi": "सिद्धांत", "te": "సిద్ధాంతం", "kn": "ಸಿದ್ಧಾಂತ", "ml": "സിദ്ധാന്തം"
    },
}

def preserve_and_protect_equations(text: str) -> tuple:
    """Extracts genuine mathematical/scientific equations, formulas, and reactions while leaving natural prose 100% intact."""
    eq_patterns = [
        # 1. LaTeX delimiters
        r'\$\$.*?\$\$',
        r'\$.*?\$',
        r'\\\[.*?\\\]',
        r'\\\([^\)]+?\\\)',
        
        # 2. Chemical Equations & Reactions (e.g., 6CO2 + 6H2O -> C6H12O6 + 6O2)
        r'\b(?:\d*[ \t]*[A-Z][a-z]?\d*(?:₀|₁|₂|₃|₄|₅|₆|₇|₈|₉)*[ \t]*(?:[\+\-\=]|->|-->|→|=>|⇒)[ \t]*)+\d*[ \t]*[A-Z][a-z]?\d*(?:₀|₁|₂|₃|₄|₅|₆|₇|₈|₉)*\b',
        
        # 3. Single-Line Formulas & Parenthesized Equations (e.g. F = ma, F = 50 × 2, E = mc^2)
        r'(?<=\()\s*[A-Za-z0-9_\+\-\*\/\^ \t]+\s*=\s*[A-Za-z0-9_\+\-\*\/\^\(\) \t\.\,×÷²³°Nkgm]+\s*(?=\))',
        r'^[ \t]*[A-Za-z0-9_\(\)\^\²\³]+[ \t]*=[ \t]*[A-Za-z0-9_\+\-\*\/\^\(\) \t\.\,×÷²³°Nkgm]+$',

        # 4. Standalone Science Formulas (e.g. D = M / V, v = d / t, F = ma)
        r'\b[A-Z]\s*=\s*[A-Za-z0-9_\+\-\*\/\^ \t\.\,×÷]+\b',
        r'\b[a-z]\s*=\s*[A-Za-z0-9_\+\-\*\/\^ \t\.\,×÷]+\b',

        # 5. Units & Standalone Formulas (e.g., 2 m/s², 9.8 m/s^2, CO2, H2O)
        r'\b\d+(?:\.\d+)?[ \t]*(?:m/s²|m/s\^2|km/h|g/cm³|g/cm3|kg/m³|kg/m3)\b',
        r'\b[A-Z][a-z]?\d+(?:[A-Z][a-z]?\d*)+\b'
    ]

    equations = []
    protected_text = text

    def replacer(match):
        idx = len(equations)
        eq_str = match.group(0).strip()
        equations.append(eq_str)
        return f" ___EQP_{idx}___ "

    for pattern in eq_patterns:
        protected_text = re.sub(pattern, replacer, protected_text, flags=re.MULTILINE)

    return protected_text, equations

def restore_preserved_equations(translated_text: str, equations: list) -> str:
    """Restores exact original mathematical and scientific equations after translation."""
    restored = translated_text
    for idx, eq in enumerate(equations):
        placeholder_regex = re.compile(rf'___EQP_{idx}___|\bEQPLACEHOLDER{idx}\b|EQPLACEHOLDER{idx}', re.IGNORECASE)
        restored = placeholder_regex.sub(eq, restored)
    return restored

LOCAL_TRANSLATION_FALLBACKS = {
    "ta": {
        "addition": "கூட்டல்", "two": "இரண்டு", "numbers": "எண்கள்", "number": "எண்",
        "force": "விசை", "motion": "இயக்கம்", "laws": "விதிகள்", "law": "விதி",
        "chola": "சோழர்", "dynasty": "வம்சம்", "temple": "கோவில்", "architecture": "கட்டடக்கலை",
        "kudavolai": "குடவோலை", "election": "தேர்தல்", "system": "முறை",
        "photosynthesis": "ஒளிச்சேர்க்கை", "plant": "தாவரம்", "leaves": "இலைகள்",
        "algebra": "இயற்கணிதம்", "equation": "சமன்பாடு", "equations": "சமன்பாடுகள்",
        "biology": "உயிரியல்", "physics": "இயற்பியல்", "chemistry": "வேதியியல்",
        "mathematics": "கணிதம்", "social": "சமூகவியல்", "science": "அறிவியல்",
        "water": "நீர்", "pressure": "அழுத்தம்", "gravity": "ஈர்ப்பு", "energy": "ஆற்றல்",
        "is": "ஆகும்", "and": "மற்றும்", "of": "இன்", "the": ""
    },
    "hi": {
        "addition": "जोड़", "two": "दो", "numbers": "संख्याएं", "number": "संख्या",
        "force": "बल", "motion": "गति", "laws": "नियम", "law": "नियम",
        "chola": "चोल", "dynasty": "राजवंश", "temple": "मंदिर", "architecture": "वास्तुकला",
        "photosynthesis": "प्रकाश संश्लेषण", "plant": "पौधा", "algebra": "बीजगणित", "equation": "समीकरण"
    },
    "te": {
        "addition": "కూడిక", "two": "రెండు", "numbers": "సంఖ్యలు", "force": "బలం", "motion": "చలనం",
        "photosynthesis": "కిరణజన్య సంయోగక్రియ", "algebra": "బీజగణితం", "equation": "సమీకరణం"
    },
    "kn": {
        "addition": "ಸಂಕಲನ", "two": "ಎರಡು", "numbers": "ಸಂಖ್ಯೆಗಳು", "force": "ಬಲ", "motion": "ಚಲನೆ",
        "photosynthesis": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ", "algebra": "ಬೀಜಗಣಿತಂ", "equation": "ಸಮೀಕರಣ"
    },
    "ml": {
        "addition": "കൂട്ടൽ", "two": "രണ്ട്", "numbers": "സംഖ്യകൾ", "force": "ബലം", "motion": "ചലനം",
        "photosynthesis": "പ്രകാശസംശ്ലേഷണം", "algebra": "ബീജഗണിതം", "equation": "സമവാക്യം"
    }
}

import unicodedata

def clean_and_normalize_tamil_text(text: str) -> str:
    """Normalizes Tamil Unicode text into canonical NFC form, removes dotted circle glyphs (\u25cc, \u25cb, \u25ef),
    decomposes two-part Tamil vowel signs to prevent FPDF2 rendering artifacts, and cleans up mistranslated
    terminology into standard Samacheer Kalvi educational Tamil."""
    if not text:
        return ""
    
    # 1. Unicode NFC Canonical Composition
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Fix Bloom's Taxonomy English-to-Tamil Translation Mappings into Standard Samacheer Kalvi Terms
    blooms_map = [
        (r'\[நினைவில் க[\u25cc\u25cb\u25ef○◌]*ாள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[நினைவில் கொள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[நினைவில் கொள்ளுங்கள்\]', '[நினைவுகூர்க]'),
        (r'\[புரிந்த க[\u25cc\u25cb\u25ef○◌]*ாள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்த கொள்ளுங்கள்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்த கொள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்துகொள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[புரிந்து கொள்ளுதல்\]', '[புரிந்துகொள்க]'),
        (r'\[பயன்படுத்தக\]', '[பயன்படுத்துக]'),
        (r'\[பகுப்பாய்வு செய்க\]', '[பகுப்பாய்வு செய்க]'),
        (r'\[பகுப்பாய்வு\]', '[பகுப்பாய்வு செய்க]'),
        (r'\[மதிப்பீடு\]', '[மதிப்பிடுக]'),

        # Sub-type translations
        (r'\(கருத்து நினைவூதுரதல்\)', '(கருத்து நினைவுகூருதல்)'),
        (r'\(பிரச்சினையைத் தீர்த்தல்ு / நடைமுறை பயன்பாடு\)', '(சிக்கலைத் தீர்த்தல் / பயன்பாடு)'),
        (r'\(பிரச்சினையைத் தீர்ப்பத / நடைமுறை பயன்பாடு\)', '(சிக்கலைத் தீர்த்தல் / பயன்பாடு)'),
        (r'\(பகுப்பாய்வு ரீசனிங்\)', '(பகுப்பாய்வு சிந்தனை)'),
        (r'\(முக்கியமான மதிப்பீடு\)', '(விமர்சன மதிப்பீடு)'),
        (r'\(தொகுப்பு\)', '(தொகுத்து அமைத்தல்)'),
    ]
    for p, r in blooms_map:
        normalized = re.sub(p, r, normalized)

    # 3. Clean up Duplicate Words & Bad Machine Translations into Proper Educational Tamil
    tamil_corrections = [
        # Remove repeated words created by translation / regex replacements
        (r'(நடைமுறை\s*){2,}', 'நடைமுறை '),
        (r'(செய்க\s*){2,}', 'செய்க '),
        (r'வேக\s+வேகம்', 'வேகம்'),
        (r'வேகம்\s+வேகம்', 'வேகம்'),
        (r'அடர்த்தி\s+அடர்த்தி', 'அடர்த்தி'),
        
        # Science & Physics Technical Term Corrections (Density, Mass, Volume)
        (r'வெகுஜனத்தின்', 'நிறையின்'),
        (r'வெகுஜனம்', 'நிறை'),
        (r'கொடுக்கப்பட்ட தொகுதியில்', 'கொடுக்கப்பட்ட கனஅளவில்'),
        # Careful: only replace தொகுதி when clearly meaning Volume (inside formula context), not when it means 'block' (உலோகத் தொகுதி)
        (r'நிறை ÷ தொகுதி', 'நிறை ÷ கனஅளவு'),
        (r'நிறை / தொகுதி', 'நிறை / கனஅளவு'),
        (r'அடர்த்தி = நிறை ÷ தொகுதி', 'அடர்த்தி = நிறை ÷ கனஅளவு'),
        (r'அடர்த்தி = நிறை / தொகுதி', 'அடர்த்தி = நிறை ÷ கனஅளவு'),
        (r'அடர்த்தி\s+அடர்த்தி', 'அடர்த்தி'),
        
        # Fix single-letter variable translation: V→வி, T→டி (variables never translate)
        # Note: \b word boundaries don't work with Tamil Unicode; use lookahead for whitespace/EOS instead
        (r'/ வி(?=\s|$|[\.,;\?!"\)])', '/ V'),
        (r'÷ வி(?=\s|$|[\.,;\?!"\)])', '÷ V'),
        (r'/ டி(?=\s|$|[\.,;\?!"\)])', '/ T'),
        (r'÷ டி(?=\s|$|[\.,;\?!"\)])', '÷ T'),
        (r'(?<=\s)வி /\s', 'V / '),
        (r'(?<=\s)டி /\s', 'T / '),
        # Direct string fixes for common formula patterns
        (r'M / வி', 'M / V'),
        (r'M ÷ வி', 'M ÷ V'),
        (r'நிறை / வி', 'நிறை / V'),
        (r'நிறை ÷ வி', 'நிறை ÷ V'),
        
        # Fix ரீசனிங் and other transliterated English words
        (r'பகுப்பாய்வு ரீசனிங்', 'பகுப்பாய்வு சிந்தனை'),
        (r'ரீசனிங்', 'சிந்தனை'),
        (r'முக்கியமான மதிப்பீடு', 'விமர்சன மதிப்பீடு'),
        
        # Fix transliterated English words in Tamil context
        (r'ஷாப்பிங்', 'கடைவீதி'),           # "shopping" -> proper Tamil
        (r'பட்ஜெட்', 'நிதி திட்டமிடல்'),     # "budget" -> proper Tamil
        (r'காஷியர்', 'காசாளர்'),              # "cashier" -> proper Tamil
        (r'இன்வென்டரி', 'சரக்கு பட்டியல்'),  # "inventory" -> proper Tamil
        
        # Spelling & Terminology Corrections
        (r'கரத்த நினைவூதுரதல்', 'கருத்து நினைவுகூருதல்'),
        (r'கரத்த நினைவுகூர்தல்', 'கருத்து நினைவுகூருதல்'),
        (r'கருத்த நினைவுகூர்தல்', 'கருத்து நினைவுகூருதல்'),
        (r'நினைவூட்டல்', 'நினைவுகூருதல்'),
        (r'பிரச்சினையைத் தீர்ப்பத', 'பிரச்சினையைத் தீர்த்தல்'),
        (r'பிரச்சனைகளைத் தீர்க்க', 'சிக்கல்களைத் தீர்த்தல்'),
        (r'பகுப்பாய்வு செய்க சிந்தனை', 'பகுப்பாய்வு சிந்தனை'),
        (r'பகுப்பாய்வு செய்க முறிவு', 'பகுப்பாய்வு விளக்கம்'),
        (r'பகுப்பாய்வு முறிவு', 'பகுப்பாய்வு விளக்கம்'),  # catch standalone "Analytical Breakdown" mistranslation
        (r'ஒருங்கிணைக்கப்பட்ட முறிவு', 'தொகுப்பு முடிவு'),
        (r'விமர்சன ரீதியான மதிப்பீடு', 'விமர்சன மதிப்பீடு'),
        (r'டிக்கிய', 'முக்கிய'),
        (r'டிாிவு', 'தீர்வு'),
        (r'டிடிவு', 'முடிவு'),

        # Incorrect literal translations of "auto" / "automatic" -> "ஆட்டோ"
        (r'\bஆட்டோ\b', 'பாடப்பகுதி'),
        (r'\bஆட்டோ\b', 'பாடப்பகுதி'),
        (r'ஆட்டோ பற்றிய', 'பாடப்பகுதி பற்றிய'),
        (r'ஆட்டோ பற்றிய', 'பாடப்பகுதி பற்றிய'),
        (r'ஆட்டோவில்', 'இப்பாடப்பகுதியில்'),
        (r'ஆட்டோவில்', 'இப்பாடப்பகுதியில்'),
        (r'நவீன ஆட்டோ', 'நவீன கற்றல்'),
        (r'நவீன ஆட்டோ', 'நவீன கற்றல்'),
        
        # Incorrect "Application" -> "விண்ணப்பம்" (job application)
        (r'விண்ணப்பம்', 'நடைமுறை பயன்பாடு'),
        (r'விண்ணப்பிக்கவும்', 'பயன்படுத்துக'),
        (r'விண்ணப்பங்கள்', 'பயன்பாடுகள்'),
        
        # Fix spacing around punctuation
        (r'\s+([,\.\?\:])', r'\1'),
        (r'\(\s+', '('),
        (r'\s+\)', ')')
    ]

    for pattern, replacement in tamil_corrections:
        normalized = re.sub(pattern, replacement, normalized)

    # 4. Remove lingering dotted circle placeholders (\u25cc, \u25cb, \u25ef, ○, ◌)
    normalized = re.sub(r'[\u25cc\u25cb\u25ef○◌]', '', normalized)

    # 5. Two-part Indic Vowel Sign Decomposition to guarantee zero dotted-circle artifacts in PDF renderers
    normalized = normalized.replace('\u0bca', '\u0bc6\u0bbe')  # ொ -> ெ + ா
    normalized = normalized.replace('\u0bcb', '\u0bc7\u0bbe')  # ோ -> ே + ா
    normalized = normalized.replace('\u0bcc', '\u0bc6\u0bd7')  # ௌ -> ெ + ௗ

    # Final NFC re-normalization
    return unicodedata.normalize("NFC", normalized)

def translate_text_http(text: str, target_lang_code: str = "ta") -> str:
    """Translates text using free translation endpoint in 1 fast batched request while keeping equations 100% untouched."""
    if not text.strip():
        return ""
    
    protected_text, equations = preserve_and_protect_equations(text)
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang_code,
            "dt": "t",
            "q": protected_text
        }
        res = requests.get(url, params=params, timeout=3.0)
        if res.status_code == 200:
            result_json = res.json()
            translated_parts = [segment[0] for segment in result_json[0] if segment and segment[0]]
            raw_translation = "".join(translated_parts)
            final_text = restore_preserved_equations(raw_translation, equations)
        else:
            final_text = protected_text
    except Exception as e:
        print(f"HTTP Translation warning (using dictionary fallback): {e}")
        dict_map = LOCAL_TRANSLATION_FALLBACKS.get(target_lang_code, LOCAL_TRANSLATION_FALLBACKS["ta"])
        words = protected_text.split()
        final_text = " ".join([dict_map.get(w.lower().strip(".,!?"), w) for w in words])
        final_text = restore_preserved_equations(final_text, equations)
    if target_lang_code == "ta" or "tam" in target_lang_code.lower():
        final_text = clean_and_normalize_tamil_text(final_text)

    return final_text

def perform_cultural_adaptation(content: str, convert_numerical_currency: bool = False) -> tuple:
    """Applies comprehensive cultural adaptation rules (including currency-to-rupee conversion) and generates logs."""
    if not content:
        return "", [], 1.0

    adapted = content
    adaptation_log = []

    # 1. Currency to Rupee Conversion
    try:
        from currency_converter import convert_text_currency_to_rupee
        adapted, curr_log = convert_text_currency_to_rupee(adapted, convert_numerical=convert_numerical_currency)
        adaptation_log.extend(curr_log)
    except Exception as e:
        print(f"Currency conversion fallback notice: {e}")

    # 2. General Cultural Adaptation Rules (Names, Locations, Stores, Sports, Festivals, Foods)
    replacements = [
        # Names
        (r"\bJohn\b", "Arul", "Replaced foreign name 'John' with regional name 'Arul'"),
        (r"\bMary\b", "Priya", "Replaced foreign name 'Mary' with regional name 'Priya'"),
        (r"\bDavid\b", "Suresh", "Replaced foreign name 'David' with regional name 'Suresh'"),
        (r"\bAlice\b", "Anita", "Replaced foreign name 'Alice' with regional name 'Anita'"),
        (r"\bBob\b", "Ramu", "Replaced foreign name 'Bob' with regional name 'Ramu'"),
        (r"\bSmith\b", "Kumar", "Replaced foreign surname 'Smith' with regional name 'Kumar'"),
        (r"\bJack\b", "Karthik", "Replaced foreign name 'Jack' with regional name 'Karthik'"),
        (r"\bEmily\b", "Deepa", "Replaced foreign name 'Emily' with regional name 'Deepa'"),
        (r"\bMichael\b", "Vijay", "Replaced foreign name 'Michael' with regional name 'Vijay'"),
        (r"\bSarah\b", "Lakshmi", "Replaced foreign name 'Sarah' with regional name 'Lakshmi'"),
        (r"\bJames\b", "Rajesh", "Replaced foreign name 'James' with regional name 'Rajesh'"),
        (r"\bPeter\b", "Ganesh", "Replaced foreign name 'Peter' with regional name 'Ganesh'"),
        
        # Locations / Cities / Countries
        (r"\bNew York\b", "Chennai", "Localized city 'New York' to 'Chennai'"),
        (r"\bLondon\b", "Mumbai", "Localized city 'London' to 'Mumbai'"),
        (r"\bWashington\b", "New Delhi", "Localized city 'Washington' to 'New Delhi'"),
        (r"\bCalifornia\b", "Bengaluru", "Localized location 'California' to 'Bengaluru'"),
        (r"\bChicago\b", "Hyderabad", "Localized location 'Chicago' to 'Hyderabad'"),
        (r"\bParis\b", "Kolkata", "Localized location 'Paris' to 'Kolkata'"),
        (r"\bTexas\b", "Kerala", "Localized location 'Texas' to 'Kerala'"),
        
        # Stores & Brands
        (r"\bgrocery store\b", "கிராமத்து கடை (local village store)", "Localized 'grocery store' to regional village store"),
        (r"\bsupermarket\b", "பொது சந்தை (local market)", "Localized 'supermarket' to local market"),
        (r"\bWalmart\b", "Local Supermarket", "Localized store name 'Walmart' to 'Local Supermarket'"),
        (r"\bTarget\b", "Departmental Store", "Localized store name 'Target' to 'Departmental Store'"),
        (r"\bCostco\b", "Wholesale Bazaar", "Localized store name 'Costco' to 'Wholesale Bazaar'"),
        (r"\bStarbucks\b", "Tea Stall", "Localized cafe reference 'Starbucks' to 'Tea Stall'"),
        (r"\bMcDonald's\b", "Local Eatery", "Localized restaurant reference"),
        
        # Currency — comprehensive dollar/USD/Euro/Pound → Rupee/₹ conversion
        # Symbol-first: $X.XX and $X patterns (must run before word patterns)
        (r"\$(?=\d)", "₹", "Converted '$' before amount to '₹'"),
        (r"\b\$\b", "₹", "Converted standalone '$' to '₹'"),
        # Word forms — case-insensitive via both cases
        (r"\bDollars\b", "Rupees", "Converted 'Dollars' to 'Rupees'"),
        (r"\bdollars\b", "rupees", "Converted 'dollars' to 'rupees'"),
        (r"\bDollar\b", "Rupee", "Converted 'Dollar' to 'Rupee'"),
        (r"\bdollar\b", "rupee", "Converted 'dollar' to 'rupee'"),
        # USD / EUR / GBP codes
        (r"\bUSD\b", "INR", "Converted currency code 'USD' to 'INR'"),
        (r"\bEUR\b", "INR", "Converted currency code 'EUR' to 'INR'"),
        (r"\bGBP\b", "INR", "Converted currency code 'GBP' to 'INR'"),
        # Cents → Paise
        (r"\bcents\b", "paise", "Converted 'cents' to 'paise'"),
        (r"\bcent\b", "paisa", "Converted 'cent' to 'paisa'"),
        # Euro / Pound word forms
        (r"\bEuros\b", "Rupees", "Converted 'Euros' to 'Rupees'"),
        (r"\beuros\b", "rupees", "Converted 'euros' to 'rupees'"),
        (r"\bEuro\b", "Rupee", "Converted 'Euro' to 'Rupee'"),
        (r"\beuro\b", "rupee", "Converted 'euro' to 'rupee'"),
        (r"\bPounds\b", "Rupees", "Converted 'Pounds' to 'Rupees'"),
        (r"\bpounds\b", "rupees", "Converted 'pounds' to 'rupees'"),
        (r"\bPound\b", "Rupee", "Converted 'Pound' to 'Rupee'"),
        (r"\bpound\b", "rupee", "Converted 'pound' to 'rupee'"),
        # Currency symbols
        (r"€", "₹", "Converted '€' to '₹'"),
        (r"£", "₹", "Converted '£' to '₹'"),
        
        # Sports
        (r"\bBaseball\b", "Cricket", "Adapted sports context from 'Baseball' to 'Cricket'"),
        (r"\bFootball\b", "Kabaddi", "Adapted sports context from 'Football' to 'Kabaddi'"),
        (r"\bRugby\b", "Badminton", "Adapted sports context to regional game"),
        
        # Holidays & Festivals
        (r"\bThanksgiving Day Parade\b", "Pongal Festival Procession", "Adapted western parade reference to regional festival procession 'Pongal Festival Procession'"),
        (r"\bThanksgiving Parade\b", "Diwali Festival Procession", "Adapted festival parade reference"),
        (r"\bThanksgiving\b", "Pongal", "Adapted holiday context to local festival 'Pongal'"),
        (r"\bChristmas\b", "Diwali", "Adapted holiday context to local festival 'Diwali'"),
        (r"\bHalloween\b", "Dussehra", "Adapted holiday context to local festival 'Dussehra'"),
        
        # Food & Attire
        (r"\bHot dog\b", "Samosa", "Adapted food item 'Hot dog' to 'Samosa'"),
        (r"\bBurger\b", "Vada Pav", "Adapted food item 'Burger' to 'Vada Pav'"),
        (r"\bPizza\b", "Roti", "Adapted food item 'Pizza' to 'Roti'"),
        (r"\bLemonade\b", "Tender Coconut", "Adapted beverage context to 'Tender Coconut'"),
        (r"\bYellow Bus\b", "School Bus", "Localized transport reference"),
        (r"\btshirt\b", "shirt", "Localized clothing reference"),
        (r"\bT-shirt\b", "Shirt", "Localized clothing reference"),
    ]
    
    adapted = content
    adaptation_log = []
    
    for pattern, repl, reason in replacements:
        if re.search(pattern, adapted, re.IGNORECASE):
            match = re.search(pattern, adapted, re.IGNORECASE)
            orig_match = match.group(0) if match else pattern
            adapted = re.sub(pattern, repl, adapted, flags=re.IGNORECASE)
            adaptation_log.append({
                "original": orig_match,
                "adapted": repl,
                "reason": reason
            })
            
    score = 0.95 if adaptation_log else 1.0
    return adapted, adaptation_log, score

def cultural_translation_agent(state: dict) -> dict:
    print("--- CULTURAL ADAPTATION & TRANSLATION AGENT ---")
    
    # 1. Get input text or textbook content
    content = state.get("input_text", "") or state.get("textbook_content", "") or "Sample educational content."
    
    target_language = str(state.get("target_language", "tam_Taml")).lower().strip()
    lang_map = {
        "tam_taml": ("Tamil", "ta"), "tamil": ("Tamil", "ta"), "ta": ("Tamil", "ta"),
        "hin_deva": ("Hindi", "hi"), "hindi": ("Hindi", "hi"), "hi": ("Hindi", "hi"),
        "tel_telu": ("Telugu", "te"), "telugu": ("Telugu", "te"), "te": ("Telugu", "te"),
        "kan_knda": ("Kannada", "kn"), "kannada": ("Kannada", "kn"), "kn": ("Kannada", "kn"),
        "mal_mlym": ("Malayalam", "ml"), "malayalam": ("Malayalam", "ml"), "ml": ("Malayalam", "ml")
    }
    readable_lang, lang_code = lang_map.get(target_language, ("Tamil", "ta"))
    
    # 2. Extract terminology log — multi-pass NLP extraction from actual input text
    terminology_log = []
    content_lower = content.lower()
    content_words = set(re.findall(r'[a-z]+', content_lower))

    # Pass 1: Match against GLOSSARY_DICTIONARY (single-word and compound checks)
    found_terms = set()
    for term, translations in GLOSSARY_DICTIONARY.items():
        # Check for the word boundary presence of the term in the content
        term_words = term.split()
        if len(term_words) == 1:
            if term in content_words:
                found_terms.add(term)
        else:
            # multi-word glossary term (e.g. "linear equation")
            if term in content_lower:
                found_terms.add(term)
    
    # Pass 2: Look for multi-word technical phrases (subject-specific compound terms not in glossary)
    MULTI_WORD_TERMS = [
        ("linear equation", {"ta": "நேர்கோட்டு சமன்பாடு", "hi": "रैखिक समीकरण", "te": "రేఖీయ సమీకరణం", "kn": "ರೇಖೀಯ ಸಮೀಕರಣ", "ml": "രേഖീയ സമവാക്യം"}),
        ("quadratic equation", {"ta": "இருமடி சமன்பாடு", "hi": "द्विघात समीकरण", "te": "వర్గ సమీకరణం", "kn": "ವರ್ಗ ಸಮೀಕರಣ", "ml": "വർഗ്ഗ സമവാക്യം"}),
        ("natural selection", {"ta": "இயற்கைத் தேர்வு", "hi": "प्राकृतिक चयन", "te": "సహజ వరణం", "kn": "ನೈಸರ್ಗಿಕ ಆಯ್ಕೆ", "ml": "പ്രകൃതി നിർദ്ധാരണം"}),
        ("chemical reaction", {"ta": "வேதி வினை", "hi": "रासायनिक अभिक्रिया", "te": "రసాయన చర్య", "kn": "ರಾಸಾಯನಿಕ ಪ್ರತಿಕ್ರಿಯೆ", "ml": "രാസ പ്രതിക്രിയ"}),
        ("kinetic energy", {"ta": "இயக்க ஆற்றல்", "hi": "गतिज ऊर्जा", "te": "చలన శక్తి", "kn": "ಚಲನ ಶಕ್ತಿ", "ml": "ഗതികോർജ്ജം"}),
        ("potential energy", {"ta": "நிலை ஆற்றல்", "hi": "स्थितिज ऊर्जा", "te": "స్థితిశక్తి", "kn": "ಸ್ಥಿತಿ ಶಕ್ತಿ", "ml": "സ്ഥിതിക ഊർജ്ജം"}),
        ("electric current", {"ta": "மின்னோட்டம்", "hi": "विद्युत धारा", "te": "విద్యుత్ ప్రవాహం", "kn": "ವಿದ್ಯುತ್ ಪ್ರವಾಹ", "ml": "വൈദ്യുത പ്രവാഹം"}),
        ("active voice", {"ta": "கர்த்தரி வாக்கியம்", "hi": "कर्तृवाच्य", "te": "కర్తరి ప్రయోగం", "kn": "ಕರ್ತೃ ವಾಚ್ಯ", "ml": "കർതൃ വാച്യം"}),
        ("passive voice", {"ta": "கர்மணி வாக்கியம்", "hi": "कर्मवाच्य", "te": "కర్మణి ప్రయోగం", "kn": "ಕರ್ಮ ವಾಚ್ಯ", "ml": "കർമ്മ വാച്യം"}),
        ("direct speech", {"ta": "நேரடி உரை", "hi": "प्रत्यक्ष कथन", "te": "ప్రత్యక్ష కథనం", "kn": "ನೇರ ಮಾತು", "ml": "നേരിട്ടുള്ള ഉദ്ധരണം"}),
        ("indirect speech", {"ta": "மறைமுக உரை", "hi": "अप्रत्यक्ष कथन", "te": "పరోక్ష కథనం", "kn": "ಪರೋಕ್ಷ ಮಾತು", "ml": "പരോക്ഷ ഉദ്ധരണം"}),
        ("cell division", {"ta": "செல் பகுப்பு", "hi": "कोशिका विभाजन", "te": "కణ విభజన", "kn": "ಕೋಶ ವಿಭಜನೆ", "ml": "കോശ വിഭജനം"}),
        ("food chain", {"ta": "உணவு சங்கிலி", "hi": "खाद्य श्रृंखला", "te": "ఆహార గొలుసు", "kn": "ಆಹಾರ ಸರಪಳಿ", "ml": "ഭക്ഷ്യ ശൃംഖല"}),
        ("total cost", {"ta": "மொத்த செலவு", "hi": "कुल लागत", "te": "మొత్తం వ్యయం", "kn": "ಒಟ್ಟು ವೆಚ್ಚ", "ml": "ആകെ ചെലവ്"}),
        ("newton's law", {"ta": "நியூட்டன் விதி", "hi": "न्यूटन का नियम", "te": "న్యూటన్ నియమం", "kn": "ನ್ಯೂಟನ್ ನಿಯಮ", "ml": "ന്യൂട്ടൺ നിയമം"}),
    ]
    for phrase, translations in MULTI_WORD_TERMS:
        if phrase in content_lower:
            trans_term = translations.get(lang_code, translations.get("ta", phrase))
            terminology_log.append({"term": phrase.title(), "translated_term": trans_term})
            found_terms.add(phrase)  # mark as handled

    # Now add single-word glossary terms found in Pass 1
    for term in found_terms:
        # Skip if already added by multi-word pass
        if any(t["term"].lower() == term.lower() for t in terminology_log):
            continue
        translations = GLOSSARY_DICTIONARY.get(term)
        if translations:
            trans_term = translations.get(lang_code, translations.get("ta", term))
            terminology_log.append({"term": term.capitalize(), "translated_term": trans_term})

    # Pass 3: Extract capitalized domain-specific nouns from input (not common words)
    STOP_CAPS = {
        "The", "A", "An", "In", "For", "Of", "To", "And", "Or", "By", "On",
        "At", "Is", "Are", "Was", "Were", "Be", "Been", "Being", "It", "He",
        "She", "We", "They", "This", "That", "These", "Those", "With", "From",
        "As", "But", "Not", "So", "If", "When", "Where", "What", "How", "Which",
        "Each", "Both", "All", "Any", "Such", "Its", "Our", "Their"
    }
    # Get first-word-in-sentence caps (exclude those)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    sentence_starts = set()
    for sent in sentences:
        first = sent.strip().split()[0] if sent.strip().split() else ""
        sentence_starts.add(first)
    
    cap_words = re.findall(r'\b[A-Z][a-z]{2,}\b', content)
    for cap in cap_words:
        if (cap not in STOP_CAPS
                and cap not in sentence_starts
                and len(terminology_log) < 12
                and not any(t["term"].lower() == cap.lower() for t in terminology_log)):
            # Translate via glossary or HTTP
            cap_lower = cap.lower()
            if cap_lower in GLOSSARY_DICTIONARY:
                trans_term = GLOSSARY_DICTIONARY[cap_lower].get(lang_code, cap)
            else:
                trans_term = translate_text_http(cap, lang_code)
            if trans_term and trans_term.strip() and trans_term.strip().lower() != cap.lower():
                terminology_log.append({"term": cap, "translated_term": trans_term})

    # Pass 4: Subject-based fallback if nothing was found
    if not terminology_log:
        subject_hint = (state.get("subject") or state.get("detected_subject") or "").lower()
        fallback_map = {
            "mathematics": ("Mathematics", GLOSSARY_DICTIONARY["mathematics"].get(lang_code, "கணிதம்")),
            "physics":     ("Physics",     GLOSSARY_DICTIONARY["physics"].get(lang_code, "இயற்பியல்")),
            "chemistry":   ("Chemistry",   GLOSSARY_DICTIONARY["chemistry"].get(lang_code, "வேதியியல்")),
            "biology":     ("Biology",     GLOSSARY_DICTIONARY["biology"].get(lang_code, "உயிரியல்")),
            "grammar":     ("Grammar",     GLOSSARY_DICTIONARY["grammar"].get(lang_code, "இலக்கணம்")),
            "history":     ("Revolution",  GLOSSARY_DICTIONARY["revolution"].get(lang_code, "புரட்சி")),
            "geography":   ("Climate",     GLOSSARY_DICTIONARY["climate"].get(lang_code, "காலநிலை")),
            "computer":    ("Algorithm",   GLOSSARY_DICTIONARY["algorithm"].get(lang_code, "வழிமுறை")),
        }
        matched_fallback = None
        for key, val in fallback_map.items():
            if key in subject_hint or key in content_lower:
                matched_fallback = val
                break
        if not matched_fallback:
            matched_fallback = ("Science", GLOSSARY_DICTIONARY["science"].get(lang_code, "அறிவியல்"))
        terminology_log = [{"term": matched_fallback[0], "translated_term": matched_fallback[1]}]

    # 3. Perform Cultural Adaptation
    adapted_content, adaptation_log, cultural_score = perform_cultural_adaptation(content)
    
    # 4. Perform Translation
    translated_content = translate_text_http(adapted_content, lang_code)
        
    return {
        "source_text": content,
        "adapted_content": adapted_content,
        "adaptation_log": adaptation_log,
        "cultural_score": cultural_score,
        "translated_content": translated_content,
        "target_language": readable_lang,
        "target_lang_code": lang_code,
        "terminology_log": terminology_log,
        "cultural_note": f"Cultural adaptation and translation complete for target language: {readable_lang} ({lang_code}). Replaced {len(adaptation_log)} regional entities."
    }
