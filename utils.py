import platform
import datetime

# ---------------- FORMAT DUE DATE ----------------
def format_due(due):
    if isinstance(due, str):
        due_date = datetime.datetime.fromisoformat(due)
    else:
        due_date = due
    today = datetime.date.today()
    if due_date.date() == today:
        return "Due Today"
    elif due_date.date() < today:
        return "Overdue!"
    else:
        return f"Due {due_date.strftime('%b %d, %Y')}"

# ---------------- CROSS-PLATFORM NOTIFICATIONS ----------------
def notify(title, due_date_str):
    """Send local notification on Windows or Mac."""
    system = platform.system()
    if system == "Darwin":  # Mac
        try:
            import subprocess
            subprocess.run([
                "osascript", "-e",
                f'display notification "Due: {due_date_str}" with title "{title}"'
            ])
        except Exception as e:
            print("Mac notification error:", e)
    elif system == "Windows":
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, f"Due: {due_date_str}", duration=10)
        except Exception as e:
            print("Windows notification error:", e)
    else:
        print(f"Task Reminder: {title} - Due {due_date_str}")
