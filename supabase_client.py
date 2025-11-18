from supabase import create_client
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def signup(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Signup error: {e}")
        return False

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            return res.user
        else:
            st.error("Login failed. Please check email/password or confirm your email.")
            return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def get_tasks(user_id):
    return supabase.table("todos").select("*").eq("user_id", user_id).execute().data

def add_task(user_id, task, due_date):
    supabase.table("todos").insert({
        "user_id": user_id,
        "task": task,
        "completed": False,
        "due_date": due_date
    }).execute()

def update_task(user_id, task_id, completed):
    supabase.table("todos").update({"completed": completed}).eq("id", task_id).eq("user_id", user_id).execute()

def delete_task(user_id, task_id):
    supabase.table("todos").delete().eq("id", task_id).eq("user_id", user_id).execute()
