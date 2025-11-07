import streamlit as st

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📝 To-Do List App")

# Add new task
new_task = st.text_input("Add a new task")
if st.button("Add Task"):
    if new_task:
        st.session_state.tasks.append(new_task)

# Show tasks
st.subheader("Your Tasks")
for i, task in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write(f"{i+1}. {task}")
    with col2:
        if st.button("❌", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            st.experimental_rerun()

