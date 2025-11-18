# supabase_client.py
from supabase import create_client, Client
import os
from datetime import date

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH ----------------
def signup(email, password):
    """Sign up a new user."""
    return supabase.auth.sign_up({"email": email, "password": password})

def login(email, password):
    """Login existing user."""
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def get_user():
    """Get the currently logged-in user."""
    return supabase.auth.user()

# ---------------- TASKS ----------------
def add_task(user_id, title, due):
    """Add a new task for the user."""
    return supabase.table("tasks").insert({
        "user_id": user_id,
        "title": title,
        "due": due,
        "done": False
    }).execute()

def get_tasks(user_id):
    """Fetch all tasks for a user, ordered by due date."""
    res = supabase.table("tasks").select("*").eq("user_id", user_id).order("due").execute()
    return res.data if res.data else []

def update_task_done(task_id, done):
    """Update task completion status."""
    return supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()

def delete_task(task_id):
    """Delete a task."""
    return supabase.table("tasks").delete().eq("id", task_id).execute()
