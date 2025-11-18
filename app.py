import streamlit as st
import pandas as pd
from datetime import date
from supabase_client import signup, login, get_user, add_task, get_tasks, update_task_done, delete_task
from utils import format_due, notify

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")
st.title("📝 Supabase To-Do App")

# ---------------- SESSION STATE ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# ---------------- AUTHENTICATION ----------------
auth_option = st.sidebar.selectbox("Login / Signup", ["Login", "Sign Up"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_option == "Sign Up":
    if st.sidebar.button("Sign Up"):
        res = signup(email, password)
        if hasattr(res, "user") and res.user:
            st.success("Signup successful! Please login and confirm your email.")
        else:
            st.error("Signup failed. Please check your details.")
elif auth_option == "Login":
    if st.sidebar.button("Login"):
        res = login(email, password)
        if hasattr(res, "user") and res.user:
            st.session_state.user = res.user
            st.success(f"Logged in as {email}")
        else:
            st.error("Login failed. Make sure your email is confirmed.")

# ---------------- MAIN APP ----------------
if st.session_state.user:
    user_id = st.session_state.user.id
    tasks = get_tasks(user_id)

    # ---------------- ADD TASK ----------------
    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due = st.date_input("Due Date", min_value=date.today())
        if st.form_submit_button("Add Task"):
            add_task(user_id, task_title, due)
            notify(task_title, due.isoformat())
            st.session_state.refresh = True
            st.success("Task added!")

    # ---------------- DISPLAY TASKS ----------------
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
                st.session_state.refresh = True

        if st.button("🗑️ Delete", key=f"del_{task['id']}"):
            delete_task(task["id"])
            st.session_state.refresh = True

    # ---------------- EXCEL IMPORT ----------------
    st.subheader("📥 Import Tasks from Excel")
    upload = st.file_uploader("Upload Excel", type=["xlsx"])
    if upload:
        df = pd.read_excel(upload)
        for _, row in df.iterrows():
            add_task(user_id, row['title'], row['due'])
        st.session_state.refresh = True
        st.success("Tasks imported!")

    # ---------------- EXCEL EXPORT ----------------
    st.subheader("📤 Export Tasks")
    if st.button("Export to Excel"):
        df_export = pd.DataFrame(tasks)
        df_export.to_excel("tasks_export.xlsx", index=False)
        st.download_button("Download Excel", data=open("tasks_export.xlsx", "rb"), file_name="tasks.xlsx")

# ---------------- SAFE REFRESH ----------------
if st.session_state.refresh:
    st.session_state.refresh = False
    st.experimental_refresh()  # safely refresh the app
