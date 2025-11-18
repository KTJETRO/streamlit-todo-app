import pandas as pd
from io import BytesIO
from datetime import date
from plyer import notification

# ------------------- EXCEL -------------------
def import_tasks_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    tasks = df.to_dict(orient="records")
    return tasks

def export_tasks_to_excel(tasks):
    df = pd.DataFrame(tasks)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output

# ------------------- NOTIFICATIONS -------------------
def notify_due_tasks(tasks):
    today = date.today()
    for task in tasks:
        task_due = task.get("due_date")
        if task_due:
            if isinstance(task_due, str):
                task_due = date.fromisoformat(task_due)
            if task_due == today and not task.get("completed", False):
                notification.notify(
                    title="Task Due Today!",
                    message=f"{task['task']}",
                    timeout=10
                )
