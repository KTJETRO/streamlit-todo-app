import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Load credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH ----------------
def signup(email: str, password: str):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        st.error(f"Signup error: {e}")
        return None

def login(email: str, password: str):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def get_user():
    return supabase.auth.user()

# ---------------- TASKS ----------------
def add_task(user_id, title, due, category="", priority="Medium", reminder=None, recurrence=None, email_reminder=False):
    try:
        # Ensure ISO format for timestamps or None
        due_str = due.isoformat() if isinstance(due, datetime) else str(due)
        reminder_str = reminder.isoformat() if isinstance(reminder, datetime) else None

        data = {
            "user_id": user_id,
            "title": title,
            "due": due_str,
            "done": False,
            "category": category,
            "priority": priority,
            "reminder": reminder_str,
            "recurrence": recurrence,
            "email_reminder": email_reminder
        }

        supabase.table("tasks").insert(data).execute()
    except Exception as e:
        st.error(f"Add task error: {e}")

def get_tasks(user_id: str):
    try:
        response = supabase.table("tasks").select("*").eq("user_id", user_id).order("due", desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Get tasks error: {e}")
        return []

def update_task_done(task_ids: list[int], done: bool):
    try:
        for task_id in task_ids:
            supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Update task error: {e}")

def delete_tasks(task_ids: list[int]):
    try:
        for task_id in task_ids:
            supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Delete task error: {e}")
