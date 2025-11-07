import streamlit as st
from datetime import date, datetime

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📝 To-Do List App with Deadlines")

# 🆕 Add new task
with st.form("add_task_form"):
    title = st.text_input("Task Title")
    due = st.date_input("Due Date", min_value=date.today())
    submitted = st.form_submit_button("Add Task")
    if submitted and title:
        st.session_state.tasks.append({
            "title": title,
            "due": due.isoformat(),
            "done": False
        })

# 🧹 Optional reset button (for debugging)
# if st.button("Reset Task List"):
#     st.session_state.tasks = []
#     st.experimental_rerun()

# 📋 Display tasks
st.subheader("Your Tasks")

def format_due(due_str):
    try:
        due_date = datetime.fromisoformat(due_str).date()
        today = date.today()
        if due_date < today:
            return f"⚠️ Overdue ({due_date})"
        elif due_date == today:
            return f"📅 Due Today ({due_date})"
        else:
            return f"🗓️ Due {due_date}"
    except:
        return "Invalid date"

for i, task in enumerate(st.session_state.tasks):
    if not isinstance(task, dict) or "title" not in task or "due" not in task or "done" not in task:
        continue  # Skip invalid entries

    col1, col2, col3, col4 = st.columns([0.4, 0.3, 0.2, 0.1])
    with col1:
        st.markdown(f"**{task['title']}**")
    with col2:
        st.markdown(format_due(task["due"]))
    with col3:
        task["done"] = st.checkbox("Done", value=task["done"], key=f"done_{i}")
    with col4:
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            st.experimental_rerun()

# ✏️ Modify due date
st.subheader("Modify Task Due Date")
task_titles = [task["title"] for task in st.session_state.tasks]
if task_titles:
    selected = st.selectbox("Select a task", task_titles)
    new_due = st.date_input("New Due Date", min_value=date.today(), key="update_due")
    if st.button("Update Due Date"):
        for task in st.session_state.tasks:
            if task["title"] == selected:
                task["due"] = new_due.isoformat()
                st.success(f"Updated due date for '{selected}'")
else:
    st.info("No tasks available to update.")
