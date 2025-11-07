import streamlit as st
import os

TODO_FILE = "todo.txt"

def load_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_tasks(tasks):
    with open(TODO_FILE, "w") as file:
        for task in tasks:
            file.write(task + "\n")

st.title("📝 To-Do List App")

tasks = load_tasks()

# Add new task
new_task = st.text_input("Add a new task")
if st.button("Add Task"):
    if new_task:
        tasks.append(new_task)
        save_tasks(tasks)
        st.experimental_rerun()

# Show tasks
st.subheader("Your Tasks")
for i, task in enumerate(tasks):
    if st.checkbox(task, key=i):
        tasks.pop(i)
        save_tasks(tasks)
        st.experimental_rerun()
