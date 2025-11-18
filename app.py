import streamlit as st
import pandas as pd
from datetime import date
from supabase_client import signup, login, get_user, add_task, get_tasks, update_task_done, delete_task
from utils import format_due, notify

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")

st.title("📝 Supabase To-Do App")

# ---------------- SESSION STATE ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "rerun" not in st.session_state:
    st.session_state.rerun = False

# ---------------- AUTHENTICATION ----------------
auth_option = st.sidebar.selectbox("Login / Signup", ["Login", "Sign Up"])
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_option == "Sign Up":
    if st.sidebar.button("Sign Up"):
        res = signup(email, password)
        if res.get("user"):
            st.success("Signup successful! Please check your email and login after confirmation.")
        else:
            st.error(res.get('error', 'Signup failed.'))

elif auth_option == "Login":
    if st.sidebar.button("Login"):
        res = login(email, password)
        if res.get("user"):
            st.session_state.user = res.user
            st.success(f"Logged in as {email}")
        else:
            error_msg = res.get('error', 'Login failed.')
            if "Email not confirmed" in str(error_msg):
                st.info("Please check your email and confirm before logging in.")
            else:
                st.error(error_msg)

# ---------------- MAIN APP ----------------
if st.session_state.user:
    user_id = st.session_state.user.id
    tasks = get_tasks(user_id)

    # ---------------- ADD TASK ----------------
    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due = st.date_input("Due Date", min_value=date.today())
        if st.form_submit_button("Add Task"):
            if task_title:
                add_task(user_id, task_title, due)
                st.success("Task added!")
                notify(task_title, due.isoformat())
                st.session_state.rerun = not st.session_state.rerun
                st.stop()
            else:
                st.warning("Please enter a task title.")

    # ---------------- DISPLAY TASKS ----------------
    st.subheader("📋 Your Tasks")
    if tasks:
        for task in tasks:
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
            with col1:
                st.markdown(f"**{task['title']}**")
            with col2:
                st.markdown(format_due(task["due"]))
            with col3:
                done = st.checkbox("Done", value=task["done"], key=f"done_{task['id']}")
                if done != task["done"]:
                    update_task_done(task["id"], done)
                    st.session_state.rerun = not st.session_state.rerun
                    st.stop()
            if st.button("🗑️ Delete", key=f"del_{task['id']}"):
                delete_task(task["id"])
                st.session_state.rerun = not st.session_state.rerun
                st.stop()
    else:
        st.info("No tasks yet. Add a task to get started!")

    # ---------------- EXCEL IMPORT ----------------
    st.subheader("📥 Import Tasks from Excel")
    upload = st.file_uploader("Upload Excel", type=["xlsx"])
    if upload:
        df = pd.read_excel(upload)
        for _, row in df.iterrows():
            add_task(user_id, row['title'], row['due'])
        st.success("Tasks imported!")
        st.session_state.rerun = not st.session_state.rerun
        st.stop()

    # ---------------- EXCEL EXPORT ----------------
    st.subheader("📤 Export Tasks")
    if tasks:
        if st.button("Export to Excel"):
            df_export = pd.DataFrame(tasks)
            df_export.to_excel("tasks_export.xlsx", index=False)
            st.download_button("Download Excel", data=open("tasks_export.xlsx", "rb"), file_name="tasks.xlsx")
    else:
        st.info("No tasks to export.")
