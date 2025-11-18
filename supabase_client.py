import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Read credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH ----------------
def signup(email: str, password: str):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Signup error: {e}")
        return None

def login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def get_user():
    return supabase.auth.user()

# ---------------- TASKS CRUD ----------------
def add_task(user_id: str, title: str, due):
    try:
        due_date = due if isinstance(due, str) else due.isoformat()
        supabase.table("tasks").insert({
            "user_id": user_id,
            "title": title,
            "due": due_date,
            "done": False
        }).execute()
    except Exception as e:
        st.error(f"Add task error: {e}")

def get_tasks(user_id: str):
    try:
        response = supabase.table("tasks").select("*").eq("user_id", user_id).order("due", ascending=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Get tasks error: {e}")
        return []

def update_task_done(task_id: int, done: bool):
    try:
        supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Update task error: {e}")

def delete_task(task_id: int):
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Delete task error: {e}")
