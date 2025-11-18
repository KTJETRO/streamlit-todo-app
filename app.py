import streamlit as st
from datetime import date
from supabase_client import signup, login, get_tasks, add_task, update_task, delete_task
from utils import import_from_excel, export_to_excel, notify_task

st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")
st.title("📝 Supabase To-Do App")

# -------------------- AUTHENTICATION --------------------
auth_choice = st.radio("Login / Signup", ["Login", "Signup"])

if auth_choice == "Signup":
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if signup(email, password):
                st.info("Signup successful! Please check your email and confirm before logging in.")
else:
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = login(email, password)
            if user:
                st.session_state["user_id"] = user.id
                st.success(f"Logged in as {email}")

# -------------------- TO-DO APP --------------------
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]

    # Load tasks
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = get_tasks(user_id)

    tasks = st.session_state["tasks"]

    # Add Task
    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due = st.date_input("Due Date", min_value=date.today())
        submitted = st.form_submit_button("Add Task")
        if submitted and task_title:
            add_task(user_id, task_title, due)
            st.success("Task added!")
            st.session_state["tasks"] = get_tasks(user_id)
            notify_task(task_title, due)

    # Display tasks
    st.subheader("Your Tasks")
    for t in tasks:
        cols = st.columns([0.5, 0.2, 0.2])
        cols[0].write(f"**{t['task']}** — 📅 {t['due_date']}")
        completed = cols[1].checkbox("Done", value=t["completed"], key=f"done_{t['id']}")
        if completed != t["completed"]:
            update_task(user_id, t["id"], completed)
        if cols[2].button("🗑️", key=f"delete_{t['id']}"):
            delete_task(user_id, t["id"])
            st.session_state["tasks"] = get_tasks(user_id)
            st.experimental_rerun()

    # Excel Import
    uploaded_file = st.file_uploader("Import Excel", type=["xlsx"])
    if uploaded_file:
        new_tasks = import_from_excel(uploaded_file)
        for task in new_tasks:
            add_task(user_id, task["task"], task["due_date"])
        st.success("Tasks imported!")
        st.session_state["tasks"] = get_tasks(user_id)

    # Excel Export
    if st.button("Export Tasks to Excel"):
        file_path = export_to_excel(tasks)
        st.download_button("Download Excel", file_path)
