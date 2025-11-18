from datetime import datetime, date
from plyer import notification

# Format due date
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

# Local PC notification
def notify(task_title, due_str):
    notification.notify(
        title=f"Task Due: {task_title}",
        message=f"Due Date: {due_str}",
        timeout=10
    )
