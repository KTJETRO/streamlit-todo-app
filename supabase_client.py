# supabase_client.py
from supabase import create_client, Client
from datetime import date

# --- Configure your Supabase project ---
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-or-service-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTHENTICATION ----------------
def signup(email: str, password: str):
    """Sign up a new user"""
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        return {"error": str(e)}

def login(email: str, password: str):
    """Login existing user"""
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        return {"error": str(e)}

def get_user():
    """Get current authenticated user"""
    return supabase.auth.user()

# ---------------- TASK CRUD ----------------
def add_task(user_id: str, title: str, due: date):
    """Add a task for a user"""
    try:
        due_str = due.isoformat() if isinstance(due, date) else str(due)
        return supabase.table("tasks").insert({
            "user_id": user_id,
            "title": title,
            "due": due_str,
            "done": False
        }).execute()
    except Exception as e:
        print("Add task error:", e)
        return None

def get_tasks(user_id: str):
    """Get all tasks for a user"""
    try:
        response = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        return response.data or []
    except Exception as e:
        print("Get tasks error:", e)
        return []

def update_task_done(task_id: int, done: bool):
    """Update the done status of a task"""
    try:
        return supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()
    except Exception as e:
        print("Update task error:", e)
        return None

def delete_task(task_id: int):
    """Delete a task by id"""
    try:
        return supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        print("Delete task error:", e)
        return None
