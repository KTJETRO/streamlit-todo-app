from datetime import date, datetime
import platform

# Cross-platform notifications
try:
    if platform.system() == "Windows":
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
    else:
        from plyer import notification
except:
    toaster = None

def format_due(due_str):
    """Format due date with status emojis"""
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
    """Send a local notification"""
    message = f"Due date: {due_date}"
    try:
        if platform.system() == "Windows":
            toaster.show_toast(f"Task Due: {task_title}", message, duration=10)
        else:
            notification.notify(title=f"Task Due: {task_title}", message=message, timeout=10)
    except:
        pass
