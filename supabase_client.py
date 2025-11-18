from supabase import create_client, Client
import os
from datetime import date

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------- AUTH -----------------
def signup(email, password):
    res = supabase.auth.sign_up({"email": email, "password": password})
    return res

def login(email, password):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res

def get_user():
    return supabase.auth.user()

# ----------------- TASKS -----------------
def add_task(user_id, title, due):
    if isinstance(due, date):
        due_str = due.isoformat()
    else:
        due_str = str(due)
    
    supabase.table("tasks").insert({
        "user_id": user_id,
        "title": title,
        "due": due_str,
        "done": False
    }).execute()

def get_tasks(user_id):
    res = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return res.data

def update_task_done(task_id, done=True):
    supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()

def delete_task(task_id):
    supabase.table("tasks").delete().eq("id", task_id).execute()
