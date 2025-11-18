import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date
from io import BytesIO
from plyer import notification

# ------------------- CONFIG -------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="To-Do App", page_icon="📝")
st.title("📝 Streamlit To-Do App (Supabase + Notifications)")

# ------------------- AUTH -------------------
if "user" not in st.session_state:
    st.session_state.user = None

def signup(email, password):
    res = supabase.auth.sign_up({"email": email, "password": password})
    return res

def login(email, password):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res

def logout():
    st.session_state.user = None
    supabase.auth.sign_out()
    st.experimental_rerun()

# ------------------- NOTIFICATIONS -------------------
def notify_due_tasks(tasks):
    today = date.today()
    for task in tasks:
        task_due = task.get("due_date")
        if task_due:
            # Convert string to date if needed
            task_due_date = task_due
            if isinstance(task_due, str):
                task_due_date = date.fromisoformat(task_due)
            if task_due_date == today and not task.get("completed", False):
                notification.notify(
                    title="Task Due Today!",
                    message=f"{task['task']}",
                    timeout=10
                )

# ------------------- EXCEL UTILS -------------------
def import_tasks_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    tasks = df.to_dict(orient="records")
    return tasks

def export_tasks_to_excel(tasks):
    df = pd.DataFrame(tasks)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output

# ------------------- LOGIN / SIGNUP -------------------
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
                st.error("Login failed. Check email/password.")

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

# ------------------- MAIN APP -------------------
else:
    user_id = st.session_state.user.id
    st.success(f"Logged in as {st.session_state.user.email}")

    if st.button("Logout"):
        logout()

    # ------------------- ADD TASK -------------------
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
            st.success("Task added!")
            st.experimental_rerun()
        else:
            st.error("Task cannot be empty.")

    # ------------------- IMPORT EXCEL -------------------
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
        st.success("Imported tasks!")
        st.experimental_rerun()

    # ------------------- DISPLAY TASKS -------------------
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

    # ------------------- EXPORT EXCEL -------------------
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

    # ------------------- LOCAL NOTIFICATIONS -------------------
    if todos.data:
        notify_due_tasks(todos.data)
