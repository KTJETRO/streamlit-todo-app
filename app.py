# app.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase_client import signup, login, get_tasks, add_task, update_task_done, delete_task
from utils import format_due, notify

st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")
st.title("📝 Supabase To-Do App")

# ---------------- AUTHENTICATION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

auth_option = st.sidebar.selectbox("Login / Sign Up", ["Login", "Sign Up"])
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_option == "Sign Up":
    if st.sidebar.button("Sign Up"):
        if email and password:
            res = signup(email, password)
            if res.user:
                st.success("Signup successful! Please check your email if verification is required.")
            elif res.error:
                st.error(f"Signup failed: {res.error.message}")
        else:
            st.warning("Please enter email and password.")

elif auth_option == "Login":
    if st.sidebar.button("Login"):
        if email and password:
            res = login(email, password)
            if res.user:
                st.session_state.user = res.user
                st.success(f"Logged in as {email}")
            elif res.error:
                st.error(f"Login failed: {res.error.message}")
        else:
            st.warning("Please enter email and password.")

# ---------------- MAIN APP ----------------
if st.session_state.user:
    user_id = st.session_state.user.id
    tasks = get_tasks(user_id)

    # ---------------- Add Task ----------------
    st.subheader("➕ Add a New Task")
    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due_date = st.date_input("Due Date", min_value=date.today())
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if task_title:
                add_task(user_id, task_title, due_date)
                notify(task_title, due_date)
                st.success("Task added!")
                st.experimental_rerun()
            else:
                st.warning("Task title cannot be empty.")

    # ---------------- Display Tasks ----------------
    st.subheader("📋 Your Tasks")
    for task in tasks:
        col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
        with col1:
            st.markdown(f"**{task['title']}**")
        with col2:
            st.markdown(format_due(task["due"]))
        with col3:
            done_checkbox = st.checkbox("Done", value=task["done"], key=f"done_{task['id']}")
            if done_checkbox != task["done"]:
                update_task_done(task["id"], done_checkbox)
                st.experimental_rerun()
        if st.button("🗑️ Delete", key=f"del_{task['id']}"):
            delete_task(task["id"])
            st.experimental_rerun()

    # ---------------- Excel Import ----------------
    st.subheader("📥 Import Tasks from Excel")
    upload = st.file_uploader("Upload Excel file", type=["xlsx"])
    if upload:
        try:
            df = pd.read_excel(upload)
            for _, row in df.iterrows():
                if "title" in row and "due" in row:
                    due_val = row["due"]
                    if isinstance(due_val, pd.Timestamp):
                        due_val = due_val.date()
                    add_task(user_id, row["title"], due_val)
                    notify(row["title"], due_val)
            st.success("Tasks imported successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to import Excel: {e}")

    # ---------------- Excel Export ----------------
    st.subheader("📤 Export Tasks to Excel")
    if st.button("Export Tasks"):
        try:
            df_export = pd.DataFrame(tasks)
            df_export.to_excel("tasks_export.xlsx", index=False)
            with open("tasks_export.xlsx", "rb") as f:
                st.download_button("Download Excel", data=f, file_name="tasks.xlsx")
        except Exception as e:
            st.error(f"Failed to export tasks: {e}")
