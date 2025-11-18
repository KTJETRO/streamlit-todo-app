from supabase import create_client, Client
from datetime import date

# ---------------- SUPABASE SETUP ----------------
# Add your Supabase URL and ANON key here
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- AUTH FUNCTIONS ----------------
def signup(email: str, password: str):
    """
    Sign up a new user with email and password.
    Returns response with user object if successful.
    """
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return res
    except Exception as e:
        return {"error": str(e)}

def login(email: str, password: str):
    """
    Login user with email and password.
    Returns response with user object if successful.
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        return {"error": str(e)}

def get_user():
    """
    Get the currently logged-in user.
    """
    return supabase.auth.user()


# ---------------- TASK FUNCTIONS ----------------
def get_tasks(user_id: str):
    """
    Fetch all tasks for a specific user.
    Returns a list of dicts with task info.
    """
    try:
        res = supabase.table("tasks").select("*").eq("user_id", user_id).order("due", ascending=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def add_task(user_id: str, title: str, due):
    """
    Add a task with title, due date, and default done=False.
    """
    try:
        if isinstance(due, date):
            due_str = due.isoformat()
        else:
            due_str = str(due)
        res = supabase.table("tasks").insert({
            "user_id": user_id,
            "title": title,
            "due": due_str,
            "done": False
        }).execute()
        return res
    except Exception as e:
        print(f"Error adding task: {e}")
        return None

def update_task_done(task_id: int, done: bool):
    """
    Update the 'done' status of a task by its ID.
    """
    try:
        res = supabase.table("tasks").update({"done": done}).eq("id", task_id).execute()
        return res
    except Exception as e:
        print(f"Error updating task: {e}")
        return None

def delete_task(task_id: int):
    """
    Delete a task by its ID.
    """
    try:
        res = supabase.table("tasks").delete().eq("id", task_id).execute()
        return res
    except Exception as e:
        print(f"Error deleting task: {e}")
        return None
