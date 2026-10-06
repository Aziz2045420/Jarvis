import os
import secrets
import threading
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request
from google import genai

import main
import safety

HOST = "127.0.0.1"  # localhost only. NEVER change this to 0.0.0.0
PORT = 5000
CONFIRM_TIMEOUT = 120
MAX_TEXT = 4000
TOKEN = secrets.token_urlsafe(24)
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
PAGE = Path(__file__).with_name("static") / "index.html"

app = Flask(__name__)
lock = threading.Lock()
job = {"status": "idle", "reply": "", "pending": None}
chat_state = {"chat": None}
client = None


def web_confirm(question):
    """Called by safety.confirm from the worker thread. Waits for the page's answer."""
    pending = {
        "id": uuid.uuid4().hex,
        "question": question,
        "event": threading.Event(),
        "approved": False,
    }
    with lock:
        job["pending"] = pending
    answered = pending["event"].wait(CONFIRM_TIMEOUT)
    with lock:
        job["pending"] = None
    return bool(answered and pending["approved"])


def run_job(text):
    try:
        reply = main.ask(client, chat_state, text)
    except Exception as e:
        reply = f"Error: {e}"
    with lock:
        job["reply"] = reply
        job["status"] = "done"


@app.before_request
def guard():
    if request.host not in ALLOWED_HOSTS:
        abort(403)
    if request.path.startswith("/api/"):
        sent = request.headers.get("X-Token", "")
        if not secrets.compare_digest(sent.encode("utf-8"), TOKEN.encode("utf-8")):
            abort(401)


@app.get("/")
def index():
    html = PAGE.read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
    return Response(html, mimetype="text/html", headers={"Cache-Control": "no-store"})


@app.post("/api/chat")
def api_chat():
    text = str((request.get_json(silent=True) or {}).get("text", "")).strip()
    if not text or len(text) > MAX_TEXT:
        return jsonify(error="bad message"), 400
    with lock:
        if job["status"] == "working":
            return jsonify(error="busy"), 409
        job.update(status="working", reply="", pending=None)
    threading.Thread(target=run_job, args=(text,), daemon=True).start()
    return jsonify(ok=True)


@app.get("/api/poll")
def api_poll():
    with lock:
        p = job["pending"]
        pending = {"id": p["id"], "question": p["question"]} if p else None
        status = job["status"]
        reply = job["reply"]
        if status == "done":
            job.update(status="idle", reply="")
    return jsonify(status=status, reply=reply, pending=pending)


@app.post("/api/confirm")
def api_confirm():
    data = request.get_json(silent=True) or {}
    with lock:
        p = job["pending"]
        if not p or p["id"] != data.get("id"):
            return jsonify(error="no such request"), 404
        p["approved"] = data.get("approve") is True
    p["event"].set()
    return jsonify(ok=True)


@app.post("/api/reset")
def api_reset():
    with lock:
        if job["status"] == "working":
            return jsonify(error="busy"), 409
        chat_state["chat"] = None
    return jsonify(ok=True)


if __name__ == "__main__":
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set in this session")
    client = genai.Client(api_key=key)
    safety.set_handler(web_confirm)
    url = f"http://localhost:{PORT}"
    print(f"JARVIS web UI running at {url}  (Ctrl+C to stop)")
    threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    app.run(host=HOST, port=PORT, threaded=True, debug=False)