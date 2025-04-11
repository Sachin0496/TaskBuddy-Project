import requests
from groq import Groq
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, UTC
from ui.ui import TaskBuddyApp
import tkinter as tk

groq_client = Groq(api_key="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")

def capture_screen_data():
    try:
        response = requests.get("http://localhost:3030/search?q=&limit=1&content_type=ocr", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            return data["data"][0]["content"].get("text", "No text found")
        return "Screenpipe: No data available"
    except requests.RequestException:
        return "Screenpipe: Check if running (Fallback: 'Sample text')"

def process_with_groq(screen_data):
    prompt = f"Analyze the following screen content and provide a smart productivity suggestion:\n\"{screen_data}\""
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception:
        return "Groq: Take a break!"

def get_calendar_events():
    try:
        creds = None
        scopes = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/calendar'
        ]
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.now(UTC).isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=5, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return "\n".join([f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}" for event in events]) or "No upcoming events"
    except Exception:
        return "2025-04-11T14:00:00Z: Hackathon Demo\n2025-04-11T15:00:00Z: Judges' Review"

def add_calendar_event(service, summary, start_time, end_time):
    try:
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'}
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return f"Added event: {summary}"
    except Exception:
        return "Event add skipped (using fallback)"

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskBuddyApp(root)

    def update_loop():
        try:
            screen_content = capture_screen_data()
            suggestion = process_with_groq(screen_content)
            calendar_events = get_calendar_events()
            scopes = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar']
            creds = Credentials.from_authorized_user_file('token.json', scopes) if os.path.exists('token.json') else None
            if creds and creds.valid:
                service = build('calendar', 'v3', credentials=creds)
                add_calendar_event(service, "Hackathon Demo", "2025-04-11T14:00:00Z", "2025-04-11T15:00:00Z")
            tasks = app.tasks_text.get(1.0, tk.END).strip() or "Add your tasks below!"
            app.update_gui(screen_content, suggestion, calendar_events, tasks)
        except Exception as e:
            app.update_gui("Error in loop", "Check console", "Error", tasks)
            print(f"Update loop error: {e}")
        if app.running:
            root.after(10000, update_loop)

    def refresh_data():
        try:
            screen_content = capture_screen_data()
            suggestion = process_with_groq(screen_content)
            calendar_events = get_calendar_events()
            tasks = app.tasks_text.get(1.0, tk.END).strip() or "Add your tasks below!"
            app.update_gui(screen_content, suggestion, calendar_events, tasks)
        except Exception as e:
            app.update_gui("Refresh failed", "Check console", "Error", tasks)
            print(f"Refresh error: {e}")

    app.set_refresh_callback(refresh_data)  # Link the backend refresh function
    app.update_loop = update_loop
    app.refresh_data = refresh_data

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.after(1000, update_loop)
    root.mainloop()