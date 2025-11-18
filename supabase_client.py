from supabase import create_client, Client
from datetime import date

import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")  # Set in Streamlit secrets
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")  # Set in Streamlit secrets

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH ----------------

def signup(email, password):
    """
    Sign up a new user
    """
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return res
    except Exception as e:
        return {"error": str(e)}

def login(email, password):
    """
    Login existing user
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        return {"error": str(e)}

def get_user():
    """
    Return current user
    """
    return supabase.auth.user()

# ---------------- TASKS ----------------

def add_task(user_id, title, due):
    """
    Add a new task for a user
    """
    try:
        due_str = due.isoformat() if isinstance(due, date) else str(due)
        supabase.table("todos").insert({
            "user_id": user_id,
            "title": title,
            "due": due_str,
            "done": False
        }).execute()
    except Exception as e:
        print("Add task error:", e)
        raise e

def get_tasks(user_id):
    """
    Retrieve all tasks for a user, ordered by due date
    """
    try:
        res = supabase.table("todos").select("*").eq("user_id", user_id).order("due").execute()
        return res.data if res.data else []
    except Exception as e:
        print("Get tasks error:", e)
        return []

def update_task_done(task_id, done):
    """
    Mark a task as done / not done
    """
    try:
        supabase.table("todos").update({"done": done}).eq("id", task_id).execute()
    except Exception as e:
        print("Update task done error:", e)
        raise e

def delete_task(task_id):
    """
    Delete a task
    """
    try:
        supabase.table("todos").delete().eq("id", task_id).execute()
    except Exception as e:
        print("Delete task error:", e)
        raise e
