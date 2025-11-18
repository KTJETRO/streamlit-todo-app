# utils.py
from datetime import datetime, date
import platform

# Notifications
try:
    if platform.system() == "Windows":
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
    else:
        from plyer import notification
except ImportError:
    toaster = None

def format_due(due_str):
    """Format due date for display."""
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

def notify(task_title, due_date):
    """Send local notification for due tasks."""
    message = f"Task '{task_title}' is due on {due_date}."
    try:
        if platform.system() == "Windows" and toaster:
            toaster.show_toast("To-Do Reminder", message, duration=10)
        else:
            from plyer import notification
            notification.notify(
                title="To-Do Reminder",
                message=message,
                timeout=10
            )
    except Exception as e:
        print(f"Notification failed: {e}")
