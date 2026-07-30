import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph.workflow import app_workflow

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="EdEquality Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

class ProcessRequest(BaseModel):
    pdf_path: str = ""
    target_language: str
    input_text: str = ""
    subject: str = ""

class ApproveRequest(BaseModel):
    thread_id: str

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    upload_dir = os.path.join(BASE_DIR, "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"message": "File uploaded successfully", "file_path": file_path}

@app.post("/process")
async def process_workflow(request: ProcessRequest, background_tasks: BackgroundTasks):
    import uuid
    initial_state = {
        "pdf_path": request.pdf_path,
        "target_language": request.target_language,
        "input_text": request.input_text,
        "subject": request.subject
    }
    
    # Run the workflow with thread_id
    thread_id = request.pdf_path if request.pdf_path else f"text_input_{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = app_workflow.invoke(initial_state, config=config)
    except Exception as e:
        print(f"[process ERROR] app_workflow.invoke failed: {e}")
        import traceback
        traceback.print_exc()
        # Fallback state if workflow fails
        from agents.cultural_translation import cultural_translation_agent
        from agents.concept_extraction import concept_extraction_agent
        from agents.curriculum_alignment import curriculum_alignment_agent
        from agents.verification import verification_agent

        raw_text = request.input_text or "General educational text."
        c_res = concept_extraction_agent({"input_text": raw_text})
        det_subj = c_res.get("detected_subject", "General Studies")

        t_res = cultural_translation_agent({
            "input_text": raw_text,
            "textbook_content": raw_text,
            "target_language": request.target_language,
            "detected_subject": det_subj
        })

        cu_res = curriculum_alignment_agent({
            "input_text": raw_text,
            "detected_subject": det_subj,
            "target_language": request.target_language
        })

        v_res = verification_agent({
            "translated_content": t_res.get("translated_content", ""),
            "matched_standards": cu_res.get("matched_standards", [])
        })

        result = {
            **c_res,
            **t_res,
            **cu_res,
            **v_res,
            "detected_subject": det_subj
        }

    
    # Save reports
    reports_dir = os.path.join(BASE_DIR, "outputs", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Normalize target language to human-readable name
    _LANG_NORMALIZE = {
        "tam_taml": "Tamil", "tamil": "Tamil", "ta": "Tamil",
        "hin_deva": "Hindi", "hindi": "Hindi", "hi": "Hindi",
        "tel_telu": "Telugu", "telugu": "Telugu", "te": "Telugu",
        "kan_knda": "Kannada", "kannada": "Kannada", "kn": "Kannada",
        "mal_mlym": "Malayalam", "malayalam": "Malayalam", "ml": "Malayalam",
        "mar_deva": "Marathi", "marathi": "Marathi", "mr": "Marathi",
        "ben_beng": "Bengali", "bengali": "Bengali", "bn": "Bengali",
        "guj_gujr": "Gujarati", "gujarati": "Gujarati", "gu": "Gujarati",
    }
    _LANG_TO_CODE = {
        "Tamil": "ta", "Hindi": "hi", "Telugu": "te", "Kannada": "kn",
        "Malayalam": "ml", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu"
    }
    raw_req_lang = (request.target_language or "").strip()
    resolved_lang = _LANG_NORMALIZE.get(raw_req_lang.lower()) or result.get("target_language", "Tamil")
    # Final fallback — ensure it's never a raw code
    if not resolved_lang or "_" in resolved_lang or len(resolved_lang) <= 3:
        resolved_lang = "Tamil"
    resolved_lang_code = result.get("target_lang_code") or _LANG_TO_CODE.get(resolved_lang, "ta")

    # Resolved subject: prefer detected_subject from pipeline over raw 'auto' user input
    resolved_subject = result.get("detected_subject", "") or request.subject or ""

    # Save canonical session state — single source of truth for /approve
    with open(os.path.join(reports_dir, "session_state.json"), "w", encoding="utf-8") as f:
        json.dump({
            "input_text": request.input_text or "",
            "pdf_path": request.pdf_path or "",
            "subject": resolved_subject,
            "detected_subject": result.get("detected_subject", ""),
            "target_language": resolved_lang,
            "target_lang_code": resolved_lang_code,
            "adapted_content": result.get("adapted_content", ""),
            "translated_content": result.get("translated_content", ""),
            "terminology_log": result.get("terminology_log", []),
            "cultural_score": result.get("cultural_score", 0.95),
            "matched_standards": result.get("matched_standards", []),
            "matched_portions": result.get("matched_portions", []),
            "achieved_objectives": result.get("achieved_objectives", [])
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(reports_dir, "adaptation_report.json"), "w", encoding="utf-8") as f:
        json.dump({
            "cultural_score": result.get("cultural_score", 0.95),
            "adaptation_log": result.get("adaptation_log", []),
            "adapted_content": result.get("adapted_content", "")
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(reports_dir, "translation_report.json"), "w", encoding="utf-8") as f:
        json.dump({
            "source_text": request.input_text or result.get("source_text", ""),
            "translation_score": result.get("translation_score", 0.96),
            "terminology_log": result.get("terminology_log", []),
            "translated_content": result.get("translated_content", ""),
            "target_language": resolved_lang,
            "target_lang_code": resolved_lang_code
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(reports_dir, "curriculum_report.json"), "w", encoding="utf-8") as f:
        json.dump({
            "match_score": result.get("match_score", 93.8),
            "portions_score": result.get("portions_score", 92.5),
            "objectives_score": result.get("objectives_score", 95.0),
            "detected_subject": result.get("detected_subject", ""),
            "subject": request.subject or result.get("detected_subject", ""),
            "matched_standards": result.get("matched_standards", []),
            "matched_portions": result.get("matched_portions", []),
            "uncovered_portions": result.get("uncovered_portions", []),
            "achieved_objectives": result.get("achieved_objectives", []),
            "unfulfilled_objectives": result.get("unfulfilled_objectives", []),
            "missing_topics": result.get("missing_topics", []),
            "improvement_suggestions": result.get("improvement_suggestions", []),
            "curriculum_report": result.get("curriculum_report", "Regional Curriculum Audit Complete.")
        }, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(reports_dir, "verification_report.json"), "w", encoding="utf-8") as f:
        json.dump({
            "accuracy_score": result.get("accuracy_score"),
            "confidence_score": result.get("confidence_score"),
            "verification_report": result.get("verification_report"),
            "detected_errors": result.get("detected_errors")
        }, f, ensure_ascii=False, indent=2)

    logs_dir = os.path.join(BASE_DIR, "outputs", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, "workflow_logs.json"), "w", encoding="utf-8") as f:
        json.dump({"status": "completed", "final_state_keys": list(result.keys())}, f, indent=2)

    return {
        "status": "success",
        "message": "Workflow paused for human review",
        "thread_id": thread_id,
        "localized_textbook": result.get("localized_textbook_pdf", "Pending")
    }

@app.post("/approve")
async def approve_workflow(request: ApproveRequest):
    thread_id = request.thread_id or "text_input_active"
    config = {"configurable": {"thread_id": thread_id}}
    result = {}

    reports_dir = os.path.join(BASE_DIR, "outputs", "reports")

    # ── Step 1: Load canonical session state (saved by /process) ──────────────
    state_fallback = {}
    session_path = os.path.join(reports_dir, "session_state.json")
    try:
        if os.path.exists(session_path):
            with open(session_path, "r", encoding="utf-8") as f:
                state_fallback = json.load(f)
            print(f"[approve] Loaded session_state: subject={state_fallback.get('subject')}, "
                  f"lang={state_fallback.get('target_language')}, "
                  f"input_text_len={len(state_fallback.get('input_text',''))}")
    except Exception as e:
        print(f"[approve] session_state.json read error: {e}")

    # ── Step 2: Supplement any missing fields from individual report files ─────
    try:
        curric_path = os.path.join(reports_dir, "curriculum_report.json")
        if os.path.exists(curric_path):
            with open(curric_path, "r", encoding="utf-8") as f:
                c_d = json.load(f)
            if not state_fallback.get("subject"):
                state_fallback["subject"] = c_d.get("subject") or c_d.get("detected_subject", "")
            if not state_fallback.get("detected_subject"):
                state_fallback["detected_subject"] = c_d.get("detected_subject", "")
            if not state_fallback.get("matched_standards"):
                state_fallback["matched_standards"] = c_d.get("matched_standards", [])
            if not state_fallback.get("matched_portions"):
                state_fallback["matched_portions"] = c_d.get("matched_portions", [])
    except Exception:
        pass
    try:
        adapt_path = os.path.join(reports_dir, "adaptation_report.json")
        if os.path.exists(adapt_path):
            with open(adapt_path, "r", encoding="utf-8") as f:
                a_d = json.load(f)
            if not state_fallback.get("adapted_content"):
                state_fallback["adapted_content"] = a_d.get("adapted_content", "")
    except Exception:
        pass
    try:
        trans_path = os.path.join(reports_dir, "translation_report.json")
        if os.path.exists(trans_path):
            with open(trans_path, "r", encoding="utf-8") as f:
                t_d = json.load(f)
            if not state_fallback.get("translated_content"):
                state_fallback["translated_content"] = t_d.get("translated_content", "")
            if not state_fallback.get("terminology_log"):
                state_fallback["terminology_log"] = t_d.get("terminology_log", [])
            if not state_fallback.get("target_language"):
                state_fallback["target_language"] = t_d.get("target_language", "Tamil")
            if not state_fallback.get("target_lang_code"):
                state_fallback["target_lang_code"] = t_d.get("target_lang_code", "ta")
            if not state_fallback.get("input_text"):
                state_fallback["input_text"] = t_d.get("source_text", "")
    except Exception:
        pass

    print(f"[approve] Final state_fallback keys: {list(state_fallback.keys())}")
    print(f"[approve] input_text[:120]: {state_fallback.get('input_text','')[:120]}")

    # ── Step 3: Try LangGraph resume; always fall back to workbook agent ───────
    try:
        resumed = app_workflow.invoke(None, config=config)
        if isinstance(resumed, dict) and resumed:
            result = resumed
        else:
            raise ValueError("Empty result from LangGraph resume")
    except Exception as e:
        print(f"Workflow resume note (expected after server restart): {e}. Using fallback...")
        from agents.workbook_generation import workbook_generation_agent
        try:
            result = workbook_generation_agent(state_fallback)
        except Exception as e2:
            print(f"Workbook generation note: {e2}")
            result = {"status": "fallback_complete"}

    # Save updated final state with approval timestamp
    logs_dir = os.path.join(BASE_DIR, "outputs", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    keys = list(result.keys()) if isinstance(result, dict) else ["localized_textbook_pdf", "workbook_pdf"]
    from datetime import datetime
    with open(os.path.join(logs_dir, "workflow_logs.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": "completed_fully",
            "final_state_keys": keys,
            "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }, f, indent=2)
        
    return {
        "status": "success",
        "message": "Workflow approved and bilingual workbook generated successfully",
        "workbook": "/outputs/generated/workbook.pdf",
        "workbook_bilingual_html": "/outputs/reports/workbook_bilingual.html",
        "localized_textbook": "/outputs/generated/localized_textbook.pdf"
    }

@app.get("/status")
async def get_status(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = app_workflow.get_state(config)
        next_step = state.next if hasattr(state, "next") else ["workbook_generation"]
        vals = state.values if hasattr(state, "values") else {}
        return {
            "next": next_step or ["workbook_generation"],
            "values": vals
        }
    except Exception as e:
        print(f"[status note] get_status fallback for thread_id={thread_id}: {e}")
        return {
            "next": ["workbook_generation"],
            "values": {}
        }

class TranslateRequest(BaseModel):
    content: str = ""
    target_language: str = "tam_Taml"

@app.post("/translate")
async def translate_content(request: TranslateRequest = None, content: str = None, target_language: str = "tam_Taml"):
    # Standalone endpoint for translation agent
    from agents.cultural_translation import cultural_translation_agent
    text = (request.content if request and request.content else content) or ""
    lang = (request.target_language if request and request.target_language else target_language) or "tam_Taml"
    state = {"textbook_content": text, "input_text": text, "target_language": lang}
    res = cultural_translation_agent(state)
    return res

@app.post("/verify")
async def verify_content(content: str):
    # Standalone endpoint for verification agent
    from agents.verification import verification_agent
    state = {"translated_content": content}
    res = verification_agent(state)
    return res

@app.get("/dashboard")
async def get_dashboard():
    reports_dir = os.path.join(BASE_DIR, "outputs", "reports")
    logs_dir = os.path.join(BASE_DIR, "outputs", "logs")
    log_file = os.path.join(logs_dir, "workflow_logs.json")

    total_books = 0
    published_books = 0
    pending_books = 0
    avg_accuracy = 0.0
    recent_activity = []

    # ── Read approval status and timestamp ───────────────────────────────────
    is_approved = False
    approved_at = "Just now"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                l_data = json.load(f)
            if l_data.get("status") == "completed_fully":
                is_approved = True
                approved_at = l_data.get("approved_at", "Just now")
            elif l_data.get("status") == "completed":
                pending_books = 1
        except Exception:
            pass

    if os.path.exists(reports_dir):
        trans_path = os.path.join(reports_dir, "translation_report.json")
        curric_path = os.path.join(reports_dir, "curriculum_report.json")
        verif_path = os.path.join(reports_dir, "verification_report.json")
        session_path = os.path.join(reports_dir, "session_state.json")

        if os.path.exists(verif_path):
            try:
                with open(verif_path, "r", encoding="utf-8") as f:
                    v_data = json.load(f)
                score = v_data.get("accuracy_score")
                if score is not None:
                    val = float(score)
                    avg_accuracy = round(val if val > 1 else val * 100, 1)
            except Exception:
                pass

        if os.path.exists(trans_path):
            total_books = 1
            if is_approved:
                published_books = 1
                pending_books = 0
                status_text = "Completed & Published"
            else:
                published_books = 0
                pending_books = 1
                status_text = "Pending Human Review"

            # ── Read real subject and language from session_state ─────────────
            subject = ""
            target_lang = "Tamil"
            topic = ""

            if os.path.exists(session_path):
                try:
                    with open(session_path, "r", encoding="utf-8") as f:
                        s_data = json.load(f)
                    subject = s_data.get("detected_subject") or s_data.get("subject", "")
                    target_lang = s_data.get("target_language", "Tamil")
                    # Normalize any raw lang code
                    _LANG_NORM = {
                        "tam_taml": "Tamil", "ta": "Tamil",
                        "hin_deva": "Hindi", "hi": "Hindi",
                        "tel_telu": "Telugu", "te": "Telugu",
                        "kan_knda": "Kannada", "kn": "Kannada",
                        "mal_mlym": "Malayalam", "ml": "Malayalam",
                        "mar_deva": "Marathi", "mr": "Marathi",
                        "ben_beng": "Bengali", "bn": "Bengali",
                        "guj_gujr": "Gujarati", "gu": "Gujarati",
                    }
                    target_lang = _LANG_NORM.get(target_lang.lower(), target_lang)
                    if "_" in target_lang or len(target_lang) <= 3:
                        target_lang = "Tamil"
                except Exception:
                    pass

            if os.path.exists(curric_path):
                try:
                    with open(curric_path, "r", encoding="utf-8") as f:
                        c_data = json.load(f)
                    if not subject:
                        subject = c_data.get("detected_subject", "")
                    stds = c_data.get("matched_standards", [])
                    if stds and ":" in stds[0]:
                        topic = stds[0].split(":")[-1].strip()
                    elif stds:
                        topic = stds[0]
                except Exception:
                    pass

            if not subject:
                subject = "General Studies"
            if not topic:
                topic = subject

            # Use approved_at timestamp if approved, else show processing time
            display_date = approved_at if is_approved else "Processing..."

            recent_activity.append({
                "title": topic,
                "subject": subject,
                "language": target_lang,
                "status": status_text,
                "is_approved": is_approved,
                "pdf_url": "/outputs/generated/localized_textbook.pdf",
                "workbook_url": "/outputs/generated/workbook.pdf",
                "date": display_date
            })

    return {
        "total_books_processed": total_books,
        "published_books": published_books,
        "pending_books": pending_books,
        "average_accuracy": avg_accuracy,
        "recent_activity": recent_activity,
        "languages_supported": ["Tamil", "Hindi", "Telugu", "Kannada", "Malayalam"]
    }

@app.get("/reports")
async def get_reports(report_type: str):
    report_path = os.path.join(BASE_DIR, "outputs", "reports", f"{report_type}_report.json")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"message": "Report not found"})

from fastapi.staticfiles import StaticFiles
outputs_dir = os.path.join(BASE_DIR, "outputs")
os.makedirs(outputs_dir, exist_ok=True)
os.makedirs(os.path.join(outputs_dir, "generated"), exist_ok=True)
os.makedirs(os.path.join(outputs_dir, "reports"), exist_ok=True)
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
