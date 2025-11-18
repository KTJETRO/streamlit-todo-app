from datetime import datetime, date
import platform

# ---------------- FORMAT DUE DATE ----------------
def format_due(due_str):
    """
    Format the due date nicely, highlighting overdue tasks
    """
    try:
        due_date = datetime.fromisoformat(due_str).date()
        today = date.today()
        if due_date < today:
            return f"⚠️ Overdue ({due_date})"
        elif due_date == today:
            return f"📅 Due Today ({due_date})"
        else:
            return f"🗓️ Due {due_date}"
    except Exception as e:
        return "Invalid date"

# ---------------- LOCAL NOTIFICATIONS ----------------
def notify(title, due_str):
    """
    Send local PC notification for a task
    """
    try:
        os_platform = platform.system()
        if os_platform == "Windows":
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(f"Task Due: {title}", f"Due: {due_str}", duration=10)
        elif os_platform == "Darwin":  # macOS
            from pync import Notifier
            Notifier.notify(f"Task Due: {title} (Due: {due_str})")
        else:
            print(f"Reminder: Task '{title}' is due on {due_str}")
    except Exception as e:
        print("Notification error:", e)
