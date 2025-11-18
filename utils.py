from datetime import date, datetime
import platform

# Notifications
try:
    if platform.system() == "Windows":
        from win10toast import ToastNotifier
        notifier = ToastNotifier()
    else:
        from plyer import notification
except ImportError:
    notifier = None


def format_due(due_str):
    """
    Format the due date for display with icons.
    - Overdue: ⚠️
    - Due Today: 📅
    - Future: 🗓️
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
    except Exception:
        return "Invalid date"


def notify(title, due_date_str):
    """
    Show a local notification for a task.
    Works on Windows (win10toast) and Mac/Linux (plyer).
    """
    message = f"Task due: {due_date_str}"
    try:
        if platform.system() == "Windows" and 'notifier' in globals():
            notifier.show_toast(title, message, duration=10, threaded=True)
        else:
            # plyer fallback for Mac/Linux
            notification.notify(title=title, message=message, timeout=10)
    except Exception as e:
        print(f"Notification failed: {e}")
