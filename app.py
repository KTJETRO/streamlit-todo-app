import streamlit as st
from datetime import date
from supabase_client import signup, login, logout, get_user_tasks, add_task, update_task_completed, delete_task
from utils import import_tasks_from_excel, export_tasks_to_excel, notify_due_tasks

st.set_page_config(page_title="To-Do App", page_icon="📝")
st.title("📝 Streamlit To-Do App")

# ------------------- AUTH -------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
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
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            res = signup(email, password)
            if res.user:
                st.success("Account created! Please log in.")
            else:
                st.error("Signup failed.")

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
            add_task(user_id, task_title, due)
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
            add_task(user_id, t["task"], t.get("due_date", date.today()))
        st.success("Imported tasks!")
        st.experimental_rerun()

    # ------------------- DISPLAY TASKS -------------------
    st.subheader("Your To-Do List")
    todos = get_user_tasks(user_id)
    if todos:
        for todo in todos:
            col1, col2, col3 = st.columns([6,1,1])
            with col1:
                st.write(("✔️ " if todo["completed"] else "❗ ") + todo["task"])
            with col2:
                if st.checkbox("Done", value=todo["completed"], key=f"done{todo['id']}"):
                    update_task_completed(todo["id"], True)
                    st.experimental_rerun()
            with col3:
                if st.button("🗑️", key=f"del{todo['id']}"):
                    delete_task(todo["id"])
                    st.experimental_rerun()
    else:
        st.info("No tasks yet.")

    # ------------------- EXPORT EXCEL -------------------
    st.subheader("Export tasks to Excel")
    if st.button("Download Excel"):
        output = export_tasks_to_excel(todos)
        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="todos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ------------------- LOCAL NOTIFICATIONS -------------------
    if todos:
        notify_due_tasks(todos)
