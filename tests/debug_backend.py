import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    print("Attempting to import database module...")
    import database as db
    print("Database module imported.")

    print("Initializing database...")
    db.init_db()
    print("Database initialized.")

    print("Creating a session...")
    session_id = db.create_session("Test Chat")
    print(f"Session created: {session_id}")

    print("Fetching sessions...")
    sessions = db.get_sessions()
    print(f"Sessions count: {len(sessions)}")
    
    # Clean up
    # db.delete_session(session_id)
    # print("Session deleted.")

    print("Backend logic seems OK.")

    print("Attempting to import main app...")
    from main import app
    print("Main app imported successfully.")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
