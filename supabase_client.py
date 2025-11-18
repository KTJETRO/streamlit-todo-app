from supabase import create_client

import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------- AUTH -------------------
def signup(email, password):
    res = supabase.auth.sign_up({"email": email, "password": password})
    return res

def login(email, password):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.experimental_rerun()

# ------------------- DATABASE -------------------
def get_user_tasks(user_id):
    result = supabase.table("todos").select("*").eq("user_id", user_id).execute()
    return result.data if result.data else []

def add_task(user_id, task, due_date):
    supabase.table("todos").insert({
        "task": task,
        "user_id": user_id,
        "completed": False,
        "due_date": due_date
    }).execute()

def update_task_completed(task_id, completed=True):
    supabase.table("todos").update({"completed": completed}).eq("id", task_id).execute()

def delete_task(task_id):
    supabase.table("todos").delete().eq("id", task_id).execute()
