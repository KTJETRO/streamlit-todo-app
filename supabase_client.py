from supabase import create_client, Client
from datetime import date

# Replace with your Supabase project URL and anon key
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_ANON_KEY"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH ----------------
def signup(email: str, password: str):
    """Sign up a user"""
    res = supabase.auth.sign_up({"email": email, "password": password})
    return res

def login(email: str, password: str):
    """Login a user"""
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res

def get_user(session):
    """Return current user from session dict"""
    return session.get("user")

# ---------------- CRUD ----------------
def add_task(user_id: str, title: str, due: date):
    data = {
        "user_id": user_id,
        "title": title,
        "due": due.isoformat(),
        "done": False
    }
    supabase.table("tasks").insert(data).execute()

def get_tasks(user_id: str):
    res = supabase.table("tasks").select("*").eq("user_id", user_id).order("due").execute()
    if res.data is None:
        return []
    return res.data

def update_task_done(task_id: int, done: bool):
    supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()

def delete_task(task_id: int):
    supabase.table("tasks").delete().eq("id", task_id).execute()
