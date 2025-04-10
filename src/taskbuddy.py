import requests
from groq import Groq
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from notion_client import Client
from datetime import datetime, UTC
import datetime


groq_client = Groq(api_key="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")

def capture_screen_data():
    try:
        response = requests.get("http://localhost:3030/search?q=&limit=1&content_type=ocr", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            return data["data"][0]["content"].get("text", "No text found")
        return "No data returned"
    except requests.RequestException as e:
        return f"Error: {e}"

def process_with_groq(screen_data):
    prompt = f"Analyze the following screen content and provide a smart productivity suggestion:\n\"{screen_data}\""
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing with Groq: {e}"

def get_calendar_events():
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
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return "\n".join([f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}" for event in events]) or "No events"

def get_notion_tasks(notion_token, database_id):
    try:
        notion = Client(auth=notion_token)
        results = notion.databases.query(database_id=database_id).get("results", [])
        return "\n".join([f"{page['properties']['Name']['title'][0]['text']['content']}" for page in results if page['properties']['Name']['title']]) or "No tasks"
    except Exception as e:
        return f"Notion error: {e}"

def delete_calendar_event(service, event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return f"Deleted event: {event_id}"

class TaskBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskBuddy")
        self.root.geometry("600x400")

        self.notebook = ttk.Notebook(root)
        self.screen_frame = ttk.Frame(self.notebook)
        self.suggest_frame = ttk.Frame(self.notebook)
        self.calendar_frame = ttk.Frame(self.notebook)
        self.notion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.screen_frame, text="Screen Content")
        self.notebook.add(self.suggest_frame, text="Suggestions")
        self.notebook.add(self.calendar_frame, text="Calendar")
        self.notebook.add(self.notion_frame, text="Notion Tasks")
        self.notebook.pack(pady=5, fill="both", expand=True)

        ttk.Label(self.screen_frame, text="Screen Content:").pack(pady=5)
        self.screen_text = scrolledtext.ScrolledText(self.screen_frame, width=70, height=10, wrap=tk.WORD)
        self.screen_text.pack(pady=5)

        ttk.Label(self.suggest_frame, text="TaskBuddy Suggests:").pack(pady=5)
        self.suggest_text = scrolledtext.ScrolledText(self.suggest_frame, width=70, height=10, wrap=tk.WORD)
        self.suggest_text.pack(pady=5)

        ttk.Label(self.calendar_frame, text="Upcoming Events:").pack(pady=5)
        self.calendar_text = scrolledtext.ScrolledText(self.calendar_frame, width=70, height=10, wrap=tk.WORD)
        self.calendar_text.pack(pady=5)

        ttk.Label(self.notion_frame, text="Notion Tasks:").pack(pady=5)
        self.notion_text = scrolledtext.ScrolledText(self.notion_frame, width=70, height=10, wrap=tk.WORD)
        self.notion_text.pack(pady=5)

        self.refresh_button = ttk.Button(root, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(pady=10)

        self.running = True
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def update_loop(self):
        notion_token = "ntn_S64301911062taY4BlLABKXTNkIdSgI973JJivJ7CUl4Ov"
        database_id = "1d117f44-ee02-80a0-b40c-f9f3a6e5d7f6"  # Hyphenated
        scopes = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar']
        while self.running:
            screen_content = capture_screen_data()
            suggestion = process_with_groq(screen_content)
            calendar_events = get_calendar_events()
            creds = Credentials.from_authorized_user_file('token.json', scopes) if os.path.exists('token.json') else None
            if creds and creds.valid:
                service = build('calendar', 'v3', credentials=creds)
                add_calendar_event(service, "Test Event", "2025-04-11T10:00:00Z", "2025-04-11T11:00:00Z")
            notion_tasks = get_notion_tasks(notion_token, database_id)
            self.update_gui(screen_content, suggestion, calendar_events, notion_tasks)
            time.sleep(30)

    def update_gui(self, screen_content, suggestion, calendar_events, notion_tasks):
        self.screen_text.delete(1.0, tk.END)
        self.screen_text.insert(tk.END, screen_content)
        self.suggest_text.delete(1.0, tk.END)
        self.suggest_text.insert(tk.END, suggestion)
        self.calendar_text.delete(1.0, tk.END)
        self.calendar_text.insert(tk.END, calendar_events)
        self.notion_text.delete(1.0, tk.END)
        self.notion_text.insert(tk.END, notion_tasks)

    def refresh_data(self):
        notion_token = "ntn_S64301911062taY4BlLABKXTNkIdSgI973JJivJ7CUl4Ov"
        database_id = "1d117f44-ee02-80a0-b40c-f9f3a6e5d7f6"
        screen_content = capture_screen_data()
        suggestion = process_with_groq(screen_content)
        calendar_events = get_calendar_events()
        notion_tasks = get_notion_tasks(notion_token, database_id)
        self.update_gui(screen_content, suggestion, calendar_events, notion_tasks)

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskBuddyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()