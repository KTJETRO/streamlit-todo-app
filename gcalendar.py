from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service

def add_task_to_calendar(task_title, due_date):
    service = get_calendar_service()
    event = {
        "summary": task_title,
        "start": {"date": due_date},
        "end": {"date": due_date},
        "reminders": {"useDefault": True},
    }
    service.events().insert(calendarId="primary", body=event).execute()
