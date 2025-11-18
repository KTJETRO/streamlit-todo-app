# utils.py
from datetime import date, datetime
import platform

# Cross-platform notifications
try:
    if platform.system() == "Windows":
        from win10toast import ToastNotifier
        notifier = ToastNotifier()
    elif platform.system() == "Darwin":  # Mac
        import subprocess
except ImportError:
    notifier = None

def notify(title: str, due: str):
    """Show local notification for a task"""
    try:
        msg = f"Task: {title}\nDue: {due}"
        if platform.system() == "Windows" and notifier:
            notifier.show_toast("To-Do Reminder", msg, duration=10)
        elif platform.system() == "Darwin":
            subprocess.call(['osascript', '-e', f'display notification "{title}" with title "To-Do Reminder"'])
    except Exception as e:
        print("Notification error:", e)

def format_due(due_str: str) -> str:
    """Format due date for display"""
    try:
        due_date = datetime.fromisoformat(due_str).date()
        today = date.today()
        if due_date < today:
            return f"⚠️ Overdue ({due_date})"
        elif due_date == today:
            return f"📅 Due Today ({due_date})"
        else:
            return f"🗓️ Due {due_date}"
    except Exception:
        return "Invalid date"
