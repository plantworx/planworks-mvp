import sys
import os
import requests
import hmac
import hashlib
import httpx
from fastapi import Request, Header, HTTPException, Response
from dotenv import load_dotenv
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables
load_dotenv()

PAGE_ID = os.getenv("PAGE_ID")
APP_ID = os.getenv("APP_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_NAME = os.getenv("APP_NAME", "app")
ADK_API_BASE = os.getenv("ADK_API_BASE", "http://localhost:8000")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = BASE_DIR
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

# Create the app using ADK helper (provides all agent endpoints)
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    allow_origins=["*"],
    web=True,
)

# Messenger webhook endpoints only (do NOT redefine /run or /apps/.../sessions/...)
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return "Verification token mismatch", 403

def verify_signature(request_body: bytes, signature: str):
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        raise HTTPException(status_code=400, detail="Unknown signature format")
    mac = hmac.new(APP_SECRET.encode(), msg=request_body, digestmod=hashlib.sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

@app.post("/webhook")
async def messenger_webhook(request: Request, x_hub_signature: str = Header(None)):
    body = await request.body()
    verify_signature(body, x_hub_signature)
    data = await request.json()
    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            if "message" in messaging_event:
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event["message"].get("text")
                if message_text:
                    agent_response = await get_agent_response(message_text, sender_id)
                    send_message(sender_id, agent_response)
    return {"status": "ok"}

def extract_text_from_candidates(candidates):
    texts = []
    if not isinstance(candidates, list):
        print("DEBUG: candidates is not a list:", candidates)
        return None
    for candidate in candidates:
        if isinstance(candidate, dict):
            content = candidate.get("content", {})
            if isinstance(content, dict):
                parts = content.get("parts", [])
                if isinstance(parts, list):
                    for part in parts:
                        if isinstance(part, dict) and "text" in part:
                            texts.append(part["text"])
            elif isinstance(content, list):
                # If content is a list, iterate through it
                for item in content:
                    if isinstance(item, dict) and "parts" in item and isinstance(item["parts"], list):
                        for part in item["parts"]:
                            if isinstance(part, dict) and "text" in part:
                                texts.append(part["text"])
        elif isinstance(candidate, list):
            # If candidate is a list, recursively extract text
            texts.extend(extract_text_from_candidates(candidate))
    return "\n".join(texts) if texts else None

async def get_agent_response(user_message: str, user_id: str) -> str:
    session_id = user_id
    session_url = f"{ADK_API_BASE}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # 1. Ensure session exists (idempotent)
            session_resp = await client.post(session_url, headers={"Content-Type": "application/json"})
            if session_resp.status_code != 200:
                # Only treat as error if not "Session already exists"
                try:
                    detail = session_resp.json().get("detail", "")
                except Exception:
                    detail = ""
                if "Session already exists" not in detail:
                    print(f"[ERROR] Session creation failed: {session_resp.status_code} {session_resp.text}")
                    return "Sorry, I couldn't create a session."
                # else: session exists, proceed
            # 2. Send message to /run
            run_url = f"{ADK_API_BASE}/run"
            payload = {
                "appName": APP_NAME,
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": user_message}]
                }
            }
            response = await client.post(run_url, json=payload)
            response.raise_for_status()
            result = response.json()
            print("DEBUG: result =", result)
            text_result = extract_text_from_candidates(result)
            if text_result:
                return text_result
            print("[ERROR] Could not parse agent response:", result)
            return "Sorry, I couldn't understand that."
    except Exception as e:
        print(f"[ERROR] Exception in get_agent_response: {e}")
        return "Sorry, there was an error contacting the agent."

def send_message(recipient_id: str, message_text: str):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        requests.post(
            "https://graph.facebook.com/v17.0/me/messages",
            params=params, headers=headers, json=data
        )
    except Exception as e:
        print(f"[ERROR] Could not send message to Messenger: {e}")

if __name__ == "__main__":
    print("Starting FastAPI server on http://0.0.0.0:8000")
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
