from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.rag_service import rag_service
from pydantic import BaseModel
from typing import Optional, List
import database as db

app = FastAPI()

# Initialize DB
db.init_db()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    include_images: bool = False
    session_id: Optional[str] = None

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    pinned: Optional[bool] = None

import logging
import traceback

# Setup logging
logger = logging.getLogger("lumina")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("backend_debug.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        logger.info(f"Uploading file: {file.filename} for session: {session_id}")
        await rag_service.process_file(file, session_id)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
def get_sessions():
    try:
        print("API CALL: getting sessions...")
        sessions = db.get_sessions()
        print(f"API SUCCESS: Found {len(sessions)} sessions")
        return sessions
    except Exception as e:
        print(f"API ERROR [get_sessions]: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions")
def create_session():
    try:
        print("API CALL: creating session...")
        session_id = db.create_session("New Chat")
        print(f"API SUCCESS: Created session {session_id}")
        return {"session_id": session_id, "title": "New Chat"}
    except Exception as e:
        print(f"API ERROR [create_session]: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
def get_session_history(session_id: str):
    messages = db.get_session_messages(session_id)
    return {"messages": messages}

@app.put("/sessions/{session_id}")
def update_session(session_id: str, update: SessionUpdate):
    db.update_session(session_id, title=update.title, pinned=update.pinned)
    return {"status": "updated"}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    db.delete_session(session_id)
    return {"status": "deleted"}

@app.delete("/sessions")
def clear_all_sessions():
    db.clear_all_sessions()
    rag_service.clear_storage()
    return {"status": "all_cleared"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Ensure session exists or create on the fly?
    # Frontend should ideally create a session first or pass one.
    # If no session_id, we can create one or treat as ephemeral. 
    # For persistence, we enforce session_id usage or return one if needed.
    # Implementation choice: if session_id provided, save.
    
    sid = request.session_id
    if sid:
        # Save user message
        db.add_message(sid, "user", request.message)
        
        # Auto-title logic
        sessions = db.get_sessions()
        current_session = next((s for s in sessions if s['id'] == sid), None)
        if current_session and current_session['title'] == "New Chat":
            new_title = (request.message[:40] + '...') if len(request.message) > 40 else request.message
            db.update_session(sid, title=new_title)
    
    response = await rag_service.query(request.message, request.include_images, sid)
    
    if sid:
        # Save bot message
        db.add_message(sid, "bot", response.get("answer"), response.get("images"))

    return response

@app.post("/define")
async def define_term(body: dict):
    # body should be {"word": "some word", "context": "surrounding text"}
    return await rag_service.define_word(body.get("word", ""), body.get("context", ""))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)