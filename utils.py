import pandas as pd
from plyer import notification

# Export tasks to Excel
def export_to_excel(tasks):
    df = pd.DataFrame(tasks)
    df.to_excel("tasks_export.xlsx", index=False)
    return "tasks_export.xlsx"

# Import tasks from Excel
def import_from_excel(file):
    df = pd.read_excel(file)
    return df.to_dict(orient="records")

# Local PC notifications
def notify_task(task_title, due_date):
    notification.notify(
        title=f"Task Due: {task_title}",
        message=f"Due Date: {due_date}",
        timeout=10
    )
