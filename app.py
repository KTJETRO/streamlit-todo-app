import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
from streamlit_calendar import calendar
from supabase_client import signup, login, get_user, add_task, get_tasks, update_task_done, delete_tasks
from utils import format_due, notify

st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")
st.title("📝 Supabase To-Do App")

if "user" not in st.session_state:
    st.session_state.user = None
if "refresh_trigger" not in st.session_state:
    st.session_state.refresh_trigger = 0

auth_option = st.sidebar.selectbox("Login / Signup", ["Login", "Sign Up"])
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_option == "Sign Up":
    if st.sidebar.button("Sign Up"):
        res = signup(email, password)
        if res and hasattr(res, "user") and res.user:
            st.success("Signup successful! Please login and confirm your email.")
        else:
            st.error("Signup failed. Please check your details.")
elif auth_option == "Login":
    if st.sidebar.button("Login"):
        res = login(email, password)
        if res and hasattr(res, "user") and res.user:
            st.session_state.user = res.user
            st.success(f"Logged in as {email}")
        else:
            st.error("Login failed. Make sure your email is confirmed.")

if st.session_state.user:
    user_id = st.session_state.user.id
    tasks = get_tasks(user_id)

    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due = st.date_input("Due Date", min_value=date.today())
        category = st.text_input("Category", placeholder="e.g. Work, Personal")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        reminder = st.time_input("Reminder Time (optional)", value=None)
        if st.form_submit_button("Add Task"):
            reminder_dt = datetime.combine(due, reminder) if reminder else None
            add_task(user_id, task_title, due, category, priority, reminder_dt)
            notify(task_title, due.isoformat())
            st.session_state.refresh_trigger += 1
            st.success("Task added!")

    st.subheader("📋 Your Tasks")
    selected_ids = []
    for task in tasks:
        cols = st.columns([0.05, 0.4, 0.2, 0.15, 0.1, 0.1])
        with cols[0]:
            selected = st.checkbox("", key=f"select_{task['id']}")
            if selected:
                selected_ids.append(task["id"])
        with cols[1]:
            st.markdown(f"**{task['title']}**")
        with cols[2]:
            st.markdown(format_due(task["due"]))
        with cols[3]:
            st.markdown(task.get("category", ""))
        with cols[4]:
            st.markdown(task.get("priority", ""))
        with cols[5]:
            st.markdown("✅" if task["done"] else "❌")

    colA, colB = st.columns(2)
    with colA:
        if st.button("Mark Selected as Done"):
            update_task_done(selected_ids, True)
            st.session_state.refresh_trigger += 1
    with colB:
        if st.button("Delete Selected"):
            delete_tasks(selected_ids)
            st.session_state.refresh_trigger += 1

    st.subheader("📥 Import Tasks from Excel")
    upload = st.file_uploader("Upload Excel", type=["xlsx"])
    if upload:
        df = pd.read_excel(upload)
        df = df.dropna(subset=["title", "due"])
        df["due"] = pd.to_datetime(df["due"], errors="coerce")
        if "reminder" in df.columns:
            df["reminder"] = pd.to_datetime(df["reminder"], errors="coerce")
        for _, row in df.iterrows():
            add_task(
                user_id,
                row["title"],
                row["due"],
                row.get("category", ""),
                row.get("priority", "Medium"),
                row.get("reminder", None)
            )
        st.session_state.refresh_trigger += 1
        st.success("Tasks imported!")

    st.subheader("📤 Export Tasks")
    if st.button("Export to Excel"):
        df_export = pd.DataFrame(tasks)
        export_cols = ["title", "due", "done", "category", "priority", "reminder"]
        df_export = df_export[export_cols]
        output = BytesIO()
        df_export.to_excel(output, index=False)
        st.download_button("Download Excel", data=output.getvalue(), file_name="tasks.xlsx")

    st.subheader("📆 Calendar View")
    calendar_events = []
    for task in tasks:
        calendar_events.append({
            "title": task["title"],
            "start": task["due"],
            "end": task["due"],
            "color": "#f39c12" if task["priority"] == "High" else "#27ae60"
        })
    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
