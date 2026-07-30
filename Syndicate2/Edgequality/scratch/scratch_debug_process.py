import requests, json

url = "http://127.0.0.1:8000/process"
payload = {
    "pdf_path": "",
    "target_language": "tam_Taml",
    "input_text": "One of the most famous stories in social science history is the story of the Indus Valley Civilization. Around 2500 BCE, people lived in well-planned cities such as Harappa and Mohenjo-Daro.",
    "subject": "auto"
}

try:
    r = requests.post(url, json=payload, timeout=10)
    print("STATUS:", r.status_code)
    print("RESPONSE:", json.dumps(r.json(), indent=2)[:500])
except Exception as e:
    print("ERROR:", e)
