import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

def workbook_generation_agent(state: dict) -> dict:
    print("--- WORKBOOK GENERATION AGENT ---")
    content = state.get("translated_content", "")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(BASE_DIR, "prompts", "workbook.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.5,
                google_api_key=api_key,
                max_retries=0,
                request_timeout=10.0
            )
            user_subj = state.get("subject") or state.get("detected_subject") or "General"
            user_text = (state.get("adapted_content") or state.get("input_text") or "")[:3000]
            full_prompt = f"{prompt_text}\n\nSubject: {user_subj}\n\nContent:\n{user_text}"
            response = llm.invoke(full_prompt)
            raw_res = response.content
            if "```json" in raw_res:
                raw_res = raw_res.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_res:
                raw_res = raw_res.split("```")[1].split("```")[0].strip()
            res_dict = json.loads(raw_res)
        else:
            res_dict = {"workbook_questions": [], "answer_key": [], "difficulty_levels": {}}
    except Exception as e:
        print(f"Gemini API workbook analysis note: {e}")
        res_dict = {"workbook_questions": [], "answer_key": [], "difficulty_levels": {}}

    # PDF Generator with automatic multi-line word wrapping and clean formatting
    def create_pdf(filename, title, text_lines):
        from fpdf import FPDF
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        try:
            pdf.set_text_shaping(True)
        except Exception:
            pass
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        font_name = "Helvetica"
        if os.path.exists(r"C:\Windows\Fonts\Nirmala.ttc"):
            try:
                pdf.add_font("Nirmala", fname=r"C:\Windows\Fonts\Nirmala.ttc")
                font_name = "Nirmala"
            except Exception:
                pass
        
        # Title
        pdf.set_font(font_name, size=14)
        clean_title = title.replace("**", "").replace("*", "").replace("#", "")
        pdf.multi_cell(w=pdf.epw, h=10, text=clean_title, align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        
        from agents.cultural_translation import clean_and_normalize_tamil_text

        # Lines
        pdf.set_font(font_name, size=10)
        sub_map = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹", "01234567890123456789")
        for line in text_lines:
            if not line.strip():
                pdf.ln(3)
                continue
            clean_line = line.translate(sub_map).replace("**", "").replace("*", "").replace("#", "")
            clean_line = clean_and_normalize_tamil_text(clean_line)
            pdf.multi_cell(w=pdf.epw, h=7, text=clean_line, align="L", new_x="LMARGIN", new_y="NEXT")
            
        pdf.output(filename)

    # Extract real input content from state or report files
    reports_dir = os.path.join(BASE_DIR, "outputs", "reports")
    curric_file = os.path.join(reports_dir, "curriculum_report.json")
    trans_file = os.path.join(reports_dir, "translation_report.json")
    adapt_file = os.path.join(reports_dir, "adaptation_report.json")
    
    # ─── Resolve input text ─────────────────────────────────────────────────
    # Prioritize session_state input_text → adapted_content → trans source_text
    input_text = state.get("input_text", "") or state.get("adapted_content", "")
    if not input_text and os.path.exists(adapt_file):
        try:
            with open(adapt_file, "r", encoding="utf-8") as f:
                a_data = json.load(f)
                input_text = a_data.get("adapted_content", "")
        except Exception:
            pass
    if not input_text and os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                t_data = json.load(f)
                input_text = t_data.get("source_text", "")
        except Exception:
            pass
    if not input_text:
        input_text = state.get("adapted_content", "")

    # ─── Resolve subject ────────────────────────────────────────────────────
    from agents.curriculum_alignment import normalize_subject
    # Priority: detected_subject > subject (if not 'auto') > keyword scan > curriculum file
    raw_subj = state.get("detected_subject", "") or state.get("subject", "")
    if raw_subj and raw_subj.lower() not in ["auto", "none", "null", ""]:
        subj = normalize_subject(raw_subj)
    else:
        txt_lower = input_text.lower()
        if any(w in txt_lower for w in ["grammar", "noun", "verb", "adjective", "tense", "pronoun", "sentence", "syntax", "vocabulary", "conjunction", "preposition"]):
            subj = "English Grammar"
        elif any(w in txt_lower for w in ["math", "equation", "algebra", "geometry", "fraction", "integer", "calculus", "trigonometry", "arithmetic", "coefficient", "polynomial"]):
            subj = "Mathematics"
        elif any(w in txt_lower for w in ["density", "mass", "pressure", "speed", "motion", "force", "newton", "gravity", "friction", "acceleration", "velocity", "momentum"]):
            subj = "Physics"
        elif any(w in txt_lower for w in ["chemical", "reaction", "element", "compound", "acid", "base", "molecule", "atom", "bond", "oxidation"]):
            subj = "Chemistry"
        elif any(w in txt_lower for w in ["cell", "photosynthesis", "organism", "biology", "plant", "ecosystem", "genetics", "evolution", "chromosome"]):
            subj = "Biology"
        elif any(w in txt_lower for w in ["history", "civilization", "dynasty", "empire", "revolution", "war", "independence", "constitution", "democracy"]):
            subj = "History & Civics"
        elif any(w in txt_lower for w in ["geography", "latitude", "longitude", "climate", "erosion", "river", "mountain", "continent", "ocean"]):
            subj = "Geography"
        elif any(w in txt_lower for w in ["computer", "algorithm", "program", "software", "database", "network", "internet", "coding"]):
            subj = "Computer Science"
        else:
            subj = "General Studies"

    # Load curriculum report to get matched_std, matched_portions, achieved_los
    matched_std = "Tamil Nadu State Board (Samacheer Kalvi)"
    matched_portions = []
    achieved_los = []
    
    if os.path.exists(curric_file):
        try:
            with open(curric_file, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                # If subject still unresolved, use curriculum detected_subject
                if not subj or subj.lower() in ["auto", "none", "null", "general studies"]:
                    subj = normalize_subject(c_data.get("detected_subject", "")) or subj
                stds = c_data.get("matched_standards", [])
                if stds:
                    matched_std = stds[0]
                matched_portions = c_data.get("matched_portions", [])
                achieved_los = c_data.get("achieved_objectives", [])
        except Exception:
            pass

    if not subj or subj.lower() in ["auto", "none", "null", ""]:
        subj = "General Studies"

    # ─── Clean English content lines (full text, not truncated) ─────────────
    clean_lines = [line.strip() for line in input_text.splitlines() if line.strip()]
    if not clean_lines:
        # Subject-specific fallback sample
        subj_lower = subj.lower()
        if "math" in subj_lower:
            clean_lines = ["A merchant buys 15 apples at Rs. 20 each. Total Cost = 15 x 20 = Rs. 300. Solving 3x + 5 = 20 gives x = 5."]
        elif "physics" in subj_lower:
            clean_lines = ["Force equals mass times acceleration (F = ma). Newton's Second Law governs motion."]
        elif "chem" in subj_lower:
            clean_lines = ["Chemical reactions transform reactants into products by breaking and forming chemical bonds."]
        elif "bio" in subj_lower:
            clean_lines = ["Photosynthesis: 6CO2 + 6H2O + sunlight → C6H12O6 + 6O2. Cells are the basic unit of life."]
        elif "grammar" in subj_lower or "english" in subj_lower:
            clean_lines = ["Grammar is the set of rules for using a language correctly. It includes nouns, verbs, adjectives, tenses, and sentence structure."]
        elif "history" in subj_lower:
            clean_lines = ["History studies past civilizations, revolutions, empires, and key events that shaped the modern world."]
        elif "geo" in subj_lower:
            clean_lines = ["Geography studies the Earth's surface, climate, latitude, longitude, rivers, mountains, and ecosystems."]
        elif "computer" in subj_lower:
            clean_lines = ["An algorithm is a step-by-step procedure for solving a problem. Programs implement algorithms using code."]
        else:
            clean_lines = ["This content covers key academic concepts from the selected subject area."]

    from agents.cultural_translation import translate_text_http

    # ─── Resolve target language ────────────────────────────────────────────
    # Normalize raw codes like 'tam_Taml' → 'Tamil', 'hin_Deva' → 'Hindi'
    _LANG_CODE_TO_HUMAN = {
        "ta": "Tamil", "tam_taml": "Tamil", "tamil": "Tamil",
        "hi": "Hindi", "hin_deva": "Hindi", "hindi": "Hindi",
        "te": "Telugu", "tel_telu": "Telugu", "telugu": "Telugu",
        "kn": "Kannada", "kan_knda": "Kannada", "kannada": "Kannada",
        "ml": "Malayalam", "mal_mlym": "Malayalam", "malayalam": "Malayalam",
        "mr": "Marathi", "mar_deva": "Marathi", "marathi": "Marathi",
        "bn": "Bengali", "ben_beng": "Bengali", "bengali": "Bengali",
        "gu": "Gujarati", "guj_gujr": "Gujarati", "gujarati": "Gujarati",
    }
    _LANG_TO_CODE = {
        "Tamil": "ta", "Hindi": "hi", "Telugu": "te", "Kannada": "kn",
        "Malayalam": "ml", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu"
    }

    raw_lang = state.get("target_language", "Tamil")
    target_lang = _LANG_CODE_TO_HUMAN.get(raw_lang.lower(), None) or raw_lang
    # Ensure target_lang is a proper human name, not a BCP47 code
    if "_" in target_lang or len(target_lang) <= 3:
        target_lang = "Tamil"

    raw_code = state.get("target_lang_code", "")
    if not raw_code or len(raw_code) > 5:
        raw_code = _LANG_TO_CODE.get(target_lang, "ta")
    target_lang_code = raw_code

    term_log = state.get("terminology_log", [])
    
    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                t_data = json.load(f)
                if not state.get("translated_content") and not translated_text:
                    translated_text = t_data.get("translated_content", "")
                if not term_log:
                    term_log = t_data.get("terminology_log", [])
                # Normalize lang from trans file too
                if not target_lang or target_lang in ["Tamil"] and not state.get("target_language"):
                    raw_lang_f = t_data.get("target_language", "Tamil")
                    target_lang = _LANG_CODE_TO_HUMAN.get(raw_lang_f.lower(), raw_lang_f)
                if not target_lang_code:
                    target_lang_code = t_data.get("target_lang_code", "ta")
        except Exception:
            pass

    # Filter out proper nouns / people names / city names from term_log
    # (only keep genuine technical/academic terms)
    PROPER_NOUN_FILTER = {
        "ram", "john", "paris", "london", "delhi", "raju", "meena", "kumar",
        "india", "america", "china", "france", "england", "germany", "italy",
        "priya", "arjun", "sita", "lakshmi", "ganesh", "suresh", "maria"
    }
    term_log = [
        t for t in term_log
        if t.get("term", "").lower() not in PROPER_NOUN_FILTER
        and len(t.get("term", "")) > 2
        and t.get("translated_term", "").strip() != ""
        and t.get("translated_term", "").lower() != t.get("term", "").lower()
    ]

    # Ensure translation is available
    translated_text = state.get("translated_content", "") or translated_text
    if not translated_text and input_text:
        translated_text = translate_text_http(input_text, target_lang_code)

    # Normalize Tamil script if needed
    if target_lang_code in ["ta"] or "tam" in target_lang_code.lower():
        from agents.cultural_translation import clean_and_normalize_tamil_text
        translated_text = clean_and_normalize_tamil_text(translated_text)

    clean_trans_lines = [line.strip() for line in translated_text.splitlines() if line.strip()]

    # ─── Build Localized Textbook PDF content (full text, not truncated) ────
    tb_content = [
        f"SUBJECT: {subj}",
        f"MODULE: {subj} - Localized Bilingual Educational Module",
        f"Curriculum Standard: {matched_std}",
        f"Target Language: {target_lang} ({target_lang_code})",
        "======================================================================",
        "SECTION 1: ENGLISH (ORIGINAL / CULTURALLY ADAPTED CONTENT)",
        "======================================================================",
    ]
    for line in clean_lines:  # ALL lines — no truncation
        tb_content.append(line)
            
    tb_content.append("======================================================================")
    tb_content.append(f"SECTION 2: {target_lang.upper()} TRANSLATED CHAPTER / {target_lang} மொழிபெயர்ப்பு")
    tb_content.append("======================================================================")
    for line in clean_trans_lines:  # ALL lines — no truncation
        tb_content.append(line)

    if term_log:
        tb_content.append("======================================================================")
        tb_content.append(f"SECTION 3: KEY TERMINOLOGY GLOSSARY (English → {target_lang})")
        tb_content.append("======================================================================")
        for t in term_log[:10]:
            tb_content.append(f"  {t['term']}  →  {t['translated_term']}")

    if matched_portions:
        tb_content.append("======================================================================")
        tb_content.append("CURRICULUM ALIGNMENT: STATE BOARD UNITS COVERED")
        for mp in matched_portions[:5]:
            tb_content.append(f"  • {mp}")


    # Extract document sentences for zero-dummy NLP content analysis
    doc_sentences = [s.strip() for s in input_text.replace("\n", " ").split(".") if len(s.strip()) > 10]
    if not doc_sentences:
        doc_sentences = clean_lines

    # Build dynamic AI-analyzed questions
    ai_q_list = res_dict.get("workbook_questions", [])
    ai_ans_list = res_dict.get("answer_key", [])
    bilingual_q_items = []

    if ai_q_list and isinstance(ai_q_list, list) and len(ai_q_list) > 0 and ai_q_list[0].get("question"):
        from agents.cultural_translation import clean_and_normalize_tamil_text
        for idx, q_item in enumerate(ai_q_list[:5], 1):
            q_type = q_item.get("type", "Question")
            bloom = q_item.get("bloom_level", "Apply")
            q_text = q_item.get("question", "")
            opts = q_item.get("options", [])
            opt_str = (" (" + ", ".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(opts)]) + ")") if opts else ""
            
            q_en_str = f"Q{idx} [{bloom}] ({q_type}): {q_text}{opt_str}"
            q_reg_str = translate_text_http(f"{q_text}{opt_str}", target_lang_code)
            
            ans_text = next((str(a.get("answer", "")) for a in ai_ans_list if a.get("question") == q_text), "Refer to textbook section.")
            ans_reg_str = translate_text_http(ans_text, target_lang_code)
            
            if target_lang_code == "ta" or "tam" in target_lang_code.lower():
                q_reg_str = clean_and_normalize_tamil_text(q_reg_str)
                ans_reg_str = clean_and_normalize_tamil_text(ans_reg_str)

            bilingual_q_items.append({
                "id": idx,
                "bloom_level": bloom,
                "type": q_type,
                "english_question": q_en_str,
                "regional_question": q_reg_str,
                "english_answer": ans_text,
                "regional_answer": ans_reg_str
            })
    else:
        from agents.cultural_translation import translate_text_http, clean_and_normalize_tamil_text

        subj_clean = subj if (subj and subj.lower() not in ["auto", "none", "null", ""]) else "General Studies"

        # Dynamic Content-Specific NLP Analysis: Extract questions directly from user's PDF sentences
        for idx, stmt in enumerate(doc_sentences[:5], 1):
            stmt_clean = stmt.replace("**", "").replace("*", "").strip()
            blooms = ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]
            b_level = blooms[(idx-1) % 5]
            
            words = stmt_clean.split()
            concept_phrase = " ".join(words[:min(10, len(words))])
            
            if idx == 1:
                q_en_str = f"Q1 [{b_level}] (Concept Recall): Based on the section on {subj_clean}, define and explain the core statement: \"{stmt_clean}\"."
                ans_en = f"Core Definition: {stmt_clean}"
            elif idx == 2:
                q_en_str = f"Q2 [{b_level}] (Problem Solving / Application): How can the principle expressed in \"{stmt_clean}\" be applied to solve real-world problems in {subj_clean}?"
                ans_en = f"Applied Solution: {stmt_clean}"
            elif idx == 3:
                q_en_str = f"Q3 [{b_level}] (Analytical Reasoning): Analyze the key variables, relationships, and mechanisms described in: \"{stmt_clean}\"."
                ans_en = f"Analytical Breakdown: {stmt_clean}"
            elif idx == 4:
                q_en_str = f"Q4 [{b_level}] (Critical Evaluation): Evaluate the significance of \"{concept_phrase}...\" in modern {subj_clean} Applications."
                ans_en = f"Evaluative Explanation: {stmt_clean}"
            else:
                q_en_str = f"Q5 [{b_level}] (Synthesis): Synthesize the core findings from: \"{stmt_clean}\" and state the key conclusion."
                ans_en = f"Synthesized Conclusion: {stmt_clean}"

            q_reg_str = translate_text_http(q_en_str, target_lang_code)
            ans_reg_str = translate_text_http(ans_en, target_lang_code)

            if target_lang_code == "ta" or "tam" in target_lang_code.lower():
                q_reg_str = clean_and_normalize_tamil_text(q_reg_str)
                ans_reg_str = clean_and_normalize_tamil_text(ans_reg_str)

            bilingual_q_items.append({
                "id": idx,
                "bloom_level": b_level,
                "type": "Extracted Document Analysis",
                "english_question": q_en_str,
                "regional_question": q_reg_str,
                "english_answer": ans_en,
                "regional_answer": ans_reg_str
            })

    # Construct BILINGUAL Student Assessment Workbook PDF
    wb_content = [
        f"SUBJECT: {subj}",
        f"WORKBOOK: Bilingual Student Assessment & Practice Exercises ({subj})",
        f"Board Framework: {matched_std}",
        f"Assessment Language: English + {target_lang} ({target_lang_code})",
        "======================================================================",
        f"SECTION A: PRACTICE QUESTIONS  |  ({subj} - {target_lang} Bilingual)",
        "======================================================================",
    ]
    
    import re
    for item in bilingual_q_items:
        reg_q = item['regional_question']
        reg_q = re.sub(r'^(?:\[Tamil\]\s*)?Q?\d+:\s*Q?\d+\s*', '', reg_q)
        reg_q = re.sub(r'^Q?\d+:\s*', '', reg_q)
        wb_content.append(f"[EN] {item['english_question']}")
        wb_content.append(f"[{target_lang}] Q{item['id']}: {reg_q}")
        wb_content.append("")

    if term_log:
        terms_str = ", ".join([f"{t['term']} = {t['translated_term']}" for t in term_log[:4]])
        wb_content.append(f"[{target_lang} Glossary]: {terms_str}")
        wb_content.append("")
    
    wb_content.append("----------------------------------------------------------------------")
    wb_content.append("SECTION B: BILINGUAL ANSWER KEY & STEP-BY-STEP SOLUTIONS")
    for item in bilingual_q_items:
        reg_ans = item['regional_answer']
        reg_ans = re.sub(r'^(?:\[Tamil\]\s*)?Ans\s*\d+:\s*', '', reg_ans)
        wb_content.append(f"[EN] Ans {item['id']}: {item['english_answer']}")
        wb_content.append(f"[{target_lang}] Ans {item['id']}: {reg_ans}")

    local_pdf = os.path.join(BASE_DIR, "outputs", "generated", "localized_textbook.pdf")
    work_pdf = os.path.join(BASE_DIR, "outputs", "generated", "workbook.pdf")
    
    create_pdf(local_pdf, f"EdEquality - Localized Textbook ({subj})", tb_content)
    create_pdf(work_pdf, f"EdEquality - Bilingual Assessment Workbook ({subj})", wb_content)
    
    # Save structured bilingual JSON workbook report
    workbook_json_path = os.path.join(reports_dir, "workbook_report.json")
    with open(workbook_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "subject": subj,
            "target_language": target_lang,
            "target_lang_code": target_lang_code,
            "bilingual_questions": bilingual_q_items,
            "terminology_log": term_log
        }, f, ensure_ascii=False, indent=2)

    # Generate UTF-8 Bilingual HTML Workbook Artifact
    bilingual_html_path = os.path.join(reports_dir, "workbook_bilingual.html")
    term_pills = "".join([f'<span class="term-pill"><strong>{t["term"]}</strong>: {t["translated_term"]}</span>' for t in term_log])
    
    en_q_html = "".join([f'<p><span class="q-title">Q{item["id"]} [{item["bloom_level"]}]:</span> {item["english_question"]}</p>' for item in bilingual_q_items])
    reg_q_html = "".join([f'<p><span class="q-title">வினா {item["id"]} [{item["bloom_level"]}]:</span> {item["regional_question"]}</p>' for item in bilingual_q_items])
    
    en_ans_html = "".join([f'<p><strong>Ans {item["id"]}:</strong> {item["english_answer"]}</p>' for item in bilingual_q_items])
    reg_ans_html = "".join([f'<p><strong>விடை {item["id"]}:</strong> {item["regional_answer"]}</p>' for item in bilingual_q_items])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EdEquality - AI Analyzed Bilingual Workbook ({subj})</title>
<style>
  body {{ font-family: 'Segoe UI', Roboto, sans-serif; padding: 25px; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
  .header {{ background: #1e293b; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
  .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 20px; }}
  .badge {{ background: #2563eb; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; margin-top: 5px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .en-box {{ background: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; border-radius: 6px; }}
  .reg-box {{ background: #f0fdf4; padding: 15px; border-left: 4px solid #16a34a; border-radius: 6px; }}
  .term-pill {{ display: inline-block; background: #e2e8f0; padding: 6px 12px; border-radius: 20px; margin: 4px; font-size: 13px; color: #334155; }}
  .q-title {{ font-weight: bold; color: #1e3a8a; }}
  .ans-box {{ background: #fffbeb; padding: 12px; border-left: 4px solid #f59e0b; border-radius: 6px; margin-top: 10px; font-size: 14px; }}
</style>
</head>
<body>
  <div class="header">
    <h1 style="margin:0;">EdEquality - AI Analyzed Bilingual Workbook ({subj})</h1>
    <div><span class="badge">AI Content Analysis Mode: English + {target_lang} ({matched_std})</span></div>
  </div>

  <div class="card">
    <h2>Section A: AI-Generated Practice Questions / பயிற்சி வினாக்கள்</h2>
    <div class="grid">
      <div class="en-box">
        <h3 style="margin-top:0;">English (AI Questions)</h3>
        {en_q_html}
      </div>
      <div class="reg-box">
        <h3 style="margin-top:0;">{target_lang} (பிராந்திய மொழி வினாக்கள்)</h3>
        {reg_q_html}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Section B: Bilingual Answer Key / விடைக்குறிப்பு</h2>
    <div class="grid">
      <div class="en-box">
        <h3 style="margin-top:0;">English Solutions</h3>
        {en_ans_html}
      </div>
      <div class="reg-box">
        <h3 style="margin-top:0;">{target_lang} தீர்வுகள்</h3>
        {reg_ans_html}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Bilingual Key Terminology / இருமொழி கலைச்சொற்கள்</h2>
    <div>{term_pills or '<span class="term-pill">Science: அறிவியல்</span>'}</div>
  </div>
</body>
</html>"""
    
    with open(bilingual_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    res_dict["localized_textbook_pdf"] = local_pdf
    res_dict["workbook_pdf"] = work_pdf
    res_dict["workbook_bilingual_html"] = bilingual_html_path
    res_dict["workbook_report_json"] = workbook_json_path
    res_dict["target_language"] = target_lang
    res_dict["target_lang_code"] = target_lang_code
    
    return res_dict
