import os
import sqlite3
import json
from datetime import datetime
import uuid

# Use absolute path for DB to ensure it's found regardless of where python is run
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "lumina_chat.db")

def init_db():
    """Initialize the database tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            images TEXT, -- JSON string of images list
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def get_sessions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Order by pinned (desc) then created_at (desc)
    c.execute("SELECT id, title, pinned, created_at FROM sessions ORDER BY pinned DESC, created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "pinned": bool(r[2]), "created_at": r[3]} for r in rows]

def get_session_messages(session_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content, images FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    messages = []
    for r in rows:
        images = []
        if r[2]:
            try:
                images = json.loads(r[2])
            except:
                images = []
        messages.append({"role": r[0], "content": r[1], "images": images})
    return messages

def add_message(session_id, role, content, images=None):
    if not images:
        images = []
    images_json = json.dumps(images)
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, images) VALUES (?, ?, ?, ?)", 
              (session_id, role, content, images_json))
    conn.commit()
    conn.close()

def update_session(session_id, title=None, pinned=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if title is not None:
        c.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
    if pinned is not None:
        # Convert boolean to integer implementation 
        pin_val = 1 if pinned else 0
        c.execute("UPDATE sessions SET pinned = ? WHERE id = ?", (pin_val, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit() # Cascade delete handles messages
    conn.close()

def clear_all_sessions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

# Initialize on module load check if needed, but safe to call explicitly in main.py
if __name__ == "__main__":
    init_db()
