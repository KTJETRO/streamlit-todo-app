To-Do List App with Deadlines

A simple yet powerful task manager built with Streamlit that lets you:

- Add tasks with due dates
- Automatically detect overdue tasks
- Mark tasks as complete
- Modify task due dates
- Delete tasks safely
- Save tasks persistently across sessions

Live App

Access the app here:
https://app-todo-app-v48zuvccpu5bjfvxrwjv5x.streamlit.app/

GitHub Repository:
https://github.com/KTJETRO/streamlit-todo-app

Features

Feature              | Description
---------------------|-------------------------------------------------------------
Add Task             | Enter a task title and select a due date
Task Completion      | Mark tasks as done using checkboxes
Overdue Detection    | Tasks past their due date are flagged with a warning
Modify Due Date      | Select any task and update its deadline
Persistent Storage   | Tasks are saved to a local tasks.json file and persist across sessions
Safe Deletion        | Tasks can be deleted without crashing the app

How It Works

- Built with Streamlit for fast web deployment
- Stores tasks in a local JSON file (tasks.json)
- Uses st.session_state to manage task state
- Automatically reruns the app when tasks are added, deleted, or updated

File Structure

streamlit-todo-app/
├── app.py              # Main Streamlit app
├── tasks.json          # Stores task data
└── requirements.txt    # Python dependencies

Installation (Local)

git clone https://github.com/KTJETRO/streamlit-todo-app.git
cd streamlit-todo-app
pip install -r requirements.txt
streamlit run app.py

Contributing

Feel free to fork the repo, submit pull requests, or suggest features like:
- User login
- Cloud database integration
- Task categories or priorities
