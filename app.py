
import streamlit as st
from supabase_client import supabase
from gcalendar import add_task_to_calendar
from utils import import_tasks_from_excel, export_tasks_to_excel
from io import BytesIO
from datetime import date

st.set_page_config(page_title="To-Do App", page_icon="📝")

# -------------------- USER SESSION --------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------- AUTH --------------------
def signup(email, password):
    res = supabase.auth.sign_up({"email": email, "password": password})
    return res

def login(email, password):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res

def logout():
    st.session_state.user = None
    supabase.auth.sign_out()

# -------------------- LOGIN / SIGNUP --------------------
if not st.session_state.user:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = login(email, password)
            if res.user:
                st.session_state.user = res.user
                st.success("Logged in!")
                st.experimental_rerun()
            else:
                st.error("Login failed.")

    with tab2:
        st.subheader("Sign Up")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            res = signup(email, password)
            if res.user:
                st.success("Account created! Please log in.")
            else:
                st.error("Signup failed.")

# -------------------- MAIN APP --------------------
else:
    user_id = st.session_state.user.id
    st.success(f"Logged in as {st.session_state.user.email}")

    if st.button("Logout"):
        logout()
        st.experimental_rerun()

    # -------------------- ADD TASK --------------------
    st.subheader("Add a new task")
    task_title = st.text_input("Task")
    due = st.date_input("Due Date", min_value=date.today())
    if st.button("Add Task"):
        if task_title.strip():
            supabase.table("todos").insert({
                "task": task_title,
                "user_id": user_id,
                "completed": False,
                "due_date": due
            }).execute()
            add_task_to_calendar(task_title, due.isoformat())
            st.success("Task added & synced to Google Calendar!")
            st.experimental_rerun()
        else:
            st.error("Task cannot be empty.")

    # -------------------- IMPORT EXCEL --------------------
    st.subheader("Import tasks from Excel")
    uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        tasks = import_tasks_from_excel(uploaded_file)
        for t in tasks:
            supabase.table("todos").insert({
                "task": t["task"],
                "user_id": user_id,
                "completed": t.get("completed", False),
                "due_date": t.get("due_date")
            }).execute()
            if "due_date" in t:
                add_task_to_calendar(t["task"], str(t["due_date"]))
        st.success("Imported tasks & synced to calendar!")
        st.experimental_rerun()

    # -------------------- DISPLAY TASKS --------------------
    st.subheader("Your To-Do List")
    todos = supabase.table("todos").select("*").eq("user_id", user_id).execute()

    if todos.data:
        for todo in todos.data:
            col1, col2, col3 = st.columns([6,1,1])
            with col1:
                st.write(("✔️ " if todo["completed"] else "❗ ") + todo["task"])
            with col2:
                if st.checkbox("Done", value=todo["completed"], key=f"done{todo['id']}"):
                    supabase.table("todos").update({"completed": True}).eq("id", todo["id"]).execute()
                    st.experimental_rerun()
            with col3:
                if st.button("🗑️", key=f"del{todo['id']}"):
                    supabase.table("todos").delete().eq("id", todo["id"]).execute()
                    st.experimental_rerun()
    else:
        st.info("No tasks yet.")

    # -------------------- EXPORT EXCEL --------------------
    st.subheader("Export tasks to Excel")
    if st.button("Download Excel"):
        tasks_data = todos.data
        output = export_tasks_to_excel(tasks_data)
        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="todos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
