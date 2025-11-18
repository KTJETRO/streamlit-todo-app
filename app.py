import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
from streamlit_calendar import calendar
from supabase_client import signup, login, get_user, add_task, get_tasks, update_task_done, delete_tasks
from utils import format_due, notify

st.set_page_config(page_title="Supabase To-Do App", page_icon="📝")
st.title("📝 Supabase To-Do App")

# ---------------- SESSION STATE ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "refresh_trigger" not in st.session_state:
    st.session_state.refresh_trigger = 0
if "imported" not in st.session_state:
    st.session_state.imported = False

# ---------------- AUTHENTICATION ----------------
if st.session_state.user:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
else:
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

# ---------------- MAIN APP ----------------
if st.session_state.user:
    user_id = st.session_state.user.id
    tasks = get_tasks(user_id)

    # ---------------- ADD TASK ----------------
    with st.form("add_task_form"):
        task_title = st.text_input("Task Title")
        due = st.date_input("Due Date", min_value=date.today())
        category = st.text_input("Category", placeholder="e.g. Work, Personal")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        recurrence = st.selectbox("Repeat", ["None", "Daily", "Weekly", "Monthly"])
        reminder = st.time_input("Reminder Time (optional)", value=None)
        email_reminder = st.checkbox("Send email reminder")

        if st.form_submit_button("Add Task"):
            reminder_dt = datetime.combine(due, reminder) if reminder else None
            recurrence_val = recurrence if recurrence != "None" else None
            add_task(user_id, task_title, due, category, priority, reminder_dt, recurrence_val, email_reminder)
            notify(task_title, due.isoformat())
            st.session_state.refresh_trigger += 1
            st.rerun()

    # ---------------- FILTERS ----------------
    st.sidebar.subheader("🔍 Filter Tasks")
    categories = sorted(set(task.get("category", "") or "Uncategorized" for task in tasks))
    priorities = ["Low", "Medium", "High"]
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    selected_priorities = st.sidebar.multiselect("Priority", priorities, default=priorities)
    due_before = st.sidebar.date_input("Due Before", value=None)

    filtered_tasks = []
    for task in tasks:
        task_category = task.get("category", "") or "Uncategorized"
        task_priority = task.get("priority", "Medium")
        task_due = pd.to_datetime(task["due"]).date()

        if task_category not in selected_categories:
            continue
        if task_priority not in selected_priorities:
            continue
        if due_before and task_due > due_before:
            continue

        filtered_tasks.append(task)

    # ---------------- DISPLAY TASKS ----------------
    st.subheader("📋 Your Tasks")
    if not filtered_tasks:
        st.info("No tasks match your current filters.")
    else:
        select_all = st.checkbox("Select All Tasks")
        selected_ids = []

        for task in filtered_tasks:
            checkbox_key = f"select_{task['id']}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            if select_all:
                st.session_state[checkbox_key] = True

            is_overdue = pd.to_datetime(task["due"]).date() < date.today() and not task["done"]

            cols = st.columns([0.05, 0.4, 0.2, 0.15, 0.1, 0.1])
            with cols[0]:
                selected = st.checkbox("Select", key=checkbox_key, label_visibility="collapsed")
                if selected:
                    selected_ids.append(task["id"])
            with cols[1]:
                title = f"**{task['title']}**"
                if is_overdue:
                    title = f"**:red[{task['title']}]**"
                st.markdown(title)
            with cols[2]:
                st.markdown(format_due(task["due"]))
            with cols[3]:
                st.markdown(task.get("category", "") or "Uncategorized")
            with cols[4]:
                st.markdown(task.get("priority", "Medium"))
            with cols[5]:
                st.markdown("✅" if task["done"] else "❌")

        colA, colB = st.columns(2)
        with colA:
            if st.button("Mark Selected as Done") and selected_ids:
                update_task_done(selected_ids, True)
                st.session_state.refresh_trigger += 1
                st.rerun()
        with colB:
            if st.button("Delete Selected") and selected_ids:
                delete_tasks(selected_ids)
                st.session_state.refresh_trigger += 1
                st.rerun()

    # ---------------- EXCEL IMPORT ----------------
    st.subheader("📥 Import Tasks from Excel")
    upload = st.file_uploader("Upload Excel", type=["xlsx"], key="excel_upload")
    if upload and not st.session_state.imported:
        try:
            df = pd.read_excel(upload)

            # Clean and validate
            df["title"] = df["title"].astype(str).str.strip()
            df["due"] = pd.to_datetime(df["due"], errors="coerce")
            df = df[df["title"].notna() & df["title"].ne("") & df["due"].notna()]
            df["reminder"] = pd.to_datetime(df.get("reminder"), errors="coerce")
            df = df.where(pd.notnull(df), None)

            imported_count = 0
            for i, row in df.iterrows():
                try:
                    reminder_val = row.get("reminder", None)
                    if pd.isna(reminder_val) or str(reminder_val).lower() == "nat":
                        reminder_val = None
                    elif isinstance(reminder_val, pd.Timestamp):
                        reminder_val = reminder_val.to_pydatetime()

                    due_val = row["due"]
                    if isinstance(due_val, pd.Timestamp):
                        due_val = due_val.to_pydatetime()

                    add_task(
                        user_id,
                        row["title"],
                        due_val,
                        row.get("category", ""),
                        row.get("priority", "Medium"),
                        reminder_val,
                        row.get("recurrence", None),
                        bool(row.get("email_reminder", False))
                    )
                    imported_count += 1
                except Exception as e:
                    st.error(f"Row {i+2} failed: {e}")

            st.success(f"Import complete. {imported_count} task(s) added.")
            st.session_state.imported = True
            st.rerun()

        except Exception as e:
            st.error(f"Import failed: {e}")

    # ---------------- EXCEL EXPORT ----------------
    st.subheader("📤 Export Tasks")
    if st.button("Export to Excel"):
        df_export = pd.DataFrame(tasks)
        export_cols = ["title", "due", "done", "category", "priority", "reminder", "recurrence", "email_reminder"]
        df_export = df_export[export_cols]
        output = BytesIO()
        df_export.to_excel(output, index=False)
        st.download_button("Download Excel", data=output.getvalue(), file_name="tasks.xlsx")

    # ---------------- CALENDAR VIEW ----------------
    st.subheader("📆 Calendar View")
    calendar_events = []
    for task in tasks:
        calendar_events.append({
            "title": task["title"],
            "start": task["due"],
            "end": task["due"],
            "color": "#f39c12" if task.get("priority") == "High" else "#27ae60"
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }

    calendar(events=calendar_events, options=calendar_options)

# ---------------- SAFE REFRESH ----------------
if st.session_state.refresh_trigger > 0;

