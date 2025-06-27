from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Set, Dict
import os
import datetime
import json
from api_client import RasaClient
from fastapi import FastAPI 
from fir_api import router as fir_router
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import urllib.parse
import logging


app = FastAPI()

# Configure CORS
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Rasa client
rasa_client = RasaClient()

# Get the absolute path to the static directory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount FIR API routes under /api
app.include_router(fir_router, prefix="/api")

# Templates
templates = Jinja2Templates(directory=static_dir)

# Simple user database
users = {
    "admin": "admin123",
    "user": "user123"
}

# Store active WebSocket connections and their session IDs
active_connections: Dict[WebSocket, str] = {}

# --- Chat History Database Setup (MySQL) ---
CHAT_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pass',
    'database': 'legal_ai'
}
def get_chat_db():
    conn = mysql.connector.connect(**CHAT_DB_CONFIG)
    return conn

@app.get('/api/chat/history')
async def get_chat_history():
    conn = get_chat_db()
    c = conn.cursor(dictionary=True)
    c.execute('''SELECT s.id, s.session_name, s.created_at, COUNT(m.id) as message_count
                 FROM chat_sessions s LEFT JOIN chat_messages m ON s.id = m.session_id
                 GROUP BY s.id ORDER BY s.created_at DESC''')
    sessions = c.fetchall()
    conn.close()
    return sessions

@app.delete('/api/chat/history/{session_id}')
async def delete_chat_history(session_id: int):
    conn = get_chat_db()
    c = conn.cursor()
    c.execute('DELETE FROM chat_sessions WHERE id = %s', (session_id,))
    conn.commit()
    c.close()
    conn.close()
    return {'status': 'success'}

@app.get("/api/chat/history/{session_id}/messages")
async def get_chat_messages(session_id: int):
    conn = get_chat_db()
    c = conn.cursor(dictionary=True)
    c.execute(
        "SELECT sender, content, timestamp FROM chat_messages WHERE session_id = %s ORDER BY timestamp ASC",
        (session_id,)
    )
    messages = c.fetchall()
    conn.close()
    return messages

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        return RedirectResponse(url="/chat", status_code=303)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/fir", response_class=HTMLResponse)
async def fir_page(request: Request):
    return templates.TemplateResponse("fir.html", {"request": request})

@app.get("/fir/admin", response_class=HTMLResponse)
async def fir_admin_page(request: Request):
    return templates.TemplateResponse("fir_admin.html", {"request": request})

@app.get("/ipc/admin", response_class=HTMLResponse)
async def ipc_admin_page(request: Request):
    return templates.TemplateResponse("ipc_admin.html", {"request": request})

@app.get("/fir/{fir_id}", response_class=HTMLResponse)
async def fir_details_page(request: Request, fir_id: int):
    return templates.TemplateResponse("saverate.html", {"request": request, "fir_id": fir_id})

@app.get("/chat/history", response_class=HTMLResponse)
async def chat_history_page(request: Request):
    return templates.TemplateResponse("chat_history.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Parse session_id from query params if present
    await websocket.accept()
    session_id = None
    parsed = urllib.parse.urlparse(str(websocket.url))
    params = urllib.parse.parse_qs(parsed.query)
    if 'session_id' in params:
        try:
            session_id = int(params['session_id'][0])
            logging.info(f"WebSocket: Received session_id from URL: {session_id}")
        except Exception:
            session_id = None
    active_connections[websocket] = session_id
    chat_db_conn = get_chat_db()
    chat_db_cur = chat_db_conn.cursor()
    try:
        while True:
            data = await websocket.receive_text()
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"{timestamp} - {data}\n"
            with open("chat.log", "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)

            # --- Chat History DB logic ---
            # Only create a new session if session_id is not provided or does not exist
            if session_id:
                chat_db_cur.execute("SELECT id FROM chat_sessions WHERE id = %s", (session_id,))
                row = chat_db_cur.fetchone()
                if not row:
                    chat_db_cur.execute("INSERT INTO chat_sessions (session_name) VALUES (%s)", (None,))
                    session_id = chat_db_cur.lastrowid
                    active_connections[websocket] = session_id
                    chat_db_conn.commit()
                    logging.info(f"WebSocket: Created new session (ID: {session_id}) because provided session_id did not exist.")
                else:
                    logging.info(f"WebSocket: Using existing session (ID: {session_id})")
            else:
                chat_db_cur.execute("INSERT INTO chat_sessions (session_name) VALUES (%s)", (None,))
                session_id = chat_db_cur.lastrowid
                active_connections[websocket] = session_id
                chat_db_conn.commit()
                logging.info(f"WebSocket: Created new session (ID: {session_id}) because no session_id was provided.")
            # Save user message
            chat_db_cur.execute("INSERT INTO chat_messages (session_id, sender, content, timestamp) VALUES (%s, %s, %s, %s)", (session_id, 'user', data, timestamp))
            chat_db_conn.commit()
            logging.info(f"WebSocket: Saved user message to session {session_id}: {data}")

            # Get response from Rasa
            rasa_response = rasa_client.send_message(data, session_id)
            # Send user message back to all clients
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(json.dumps({
                        "type": "user_message",
                        "text": data
                    }))
            # Send Rasa response to the sender
            if rasa_response:
                combined_response = []
                for message in rasa_response:
                    if "text" in message:
                        combined_response.append(message["text"])
                        # Save bot message to DB
                        chat_db_cur.execute("INSERT INTO chat_messages (session_id, sender, content, timestamp) VALUES (%s, %s, %s, %s)", (session_id, 'bot', message["text"], datetime.datetime.now().isoformat()))
                        chat_db_conn.commit()
                        logging.info(f"WebSocket: Saved bot message to session {session_id}: {message['text']}")
                formatted_response = "\n\n".join(combined_response)
                await websocket.send_text(json.dumps({
                    "type": "bot_message",
                    "text": formatted_response
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "text": "I'm sorry, I couldn't process your request at the moment."
                }))
    except WebSocketDisconnect:
        if websocket in active_connections:
            del active_connections[websocket]
    finally:
        chat_db_cur.close()
        chat_db_conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)