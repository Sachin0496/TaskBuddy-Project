import tkinter as tk
from tkinter import ttk, scrolledtext

class TaskBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskBuddy - Hackathon Edition")
        self.root.geometry("800x600")
        self.root.configure(bg="#2E2E2E")

        # Style configuration
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#2E2E2E", borderwidth=0)
        style.configure("TNotebook.Tab", background="#3C3C3C", foreground="white", padding=[10, 5], font=("Helvetica", 12, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#4A90E2")])
        style.configure("TButton", background="#4A90E2", foreground="white", font=("Helvetica", 10, "bold"), padding=5)
        style.map("TButton", background=[("active", "#357ABD")])
        style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Helvetica", 11))

        # Splash screen
        self.splash = tk.Toplevel(self.root)
        self.splash.geometry("300x150")
        self.splash.configure(bg="#2E2E2E")
        self.splash.overrideredirect(True)
        tk.Label(self.splash, text="TaskBuddy", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="#4A90E2").pack(pady=20)
        tk.Label(self.splash, text="Hackathon 2025", font=("Helvetica", 14), bg="#2E2E2E", fg="white").pack()
        self.root.after(2000, self.splash.destroy)

        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.screen_frame = ttk.Frame(self.notebook)
        self.suggest_frame = ttk.Frame(self.notebook)
        self.calendar_frame = ttk.Frame(self.notebook)
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.screen_frame, text="Screen")
        self.notebook.add(self.suggest_frame, text="Suggestions")
        self.notebook.add(self.calendar_frame, text="Calendar")
        self.notebook.add(self.tasks_frame, text="Tasks")
        self.notebook.pack(fill="both", expand=True)

        # Screen Content
        ttk.Label(self.screen_frame, text="Live Screen Capture").pack(pady=5)
        self.screen_text = scrolledtext.ScrolledText(self.screen_frame, width=90, height=15, wrap=tk.WORD, bg="#3C3C3C", fg="white", font=("Courier", 10))
        self.screen_text.pack(pady=5)

        # Suggestions
        ttk.Label(self.suggest_frame, text="AI Productivity Tips").pack(pady=5)
        self.suggest_text = scrolledtext.ScrolledText(self.suggest_frame, width=90, height=15, wrap=tk.WORD, bg="#3C3C3C", fg="white", font=("Helvetica", 10))
        self.suggest_text.pack(pady=5)

        # Calendar
        ttk.Label(self.calendar_frame, text="Upcoming Events").pack(pady=5)
        self.calendar_text = scrolledtext.ScrolledText(self.calendar_frame, width=90, height=15, wrap=tk.WORD, bg="#3C3C3C", fg="white", font=("Helvetica", 10))
        self.calendar_text.pack(pady=5)

        # Tasks
        ttk.Label(self.tasks_frame, text="Your Tasks").pack(pady=5)
        self.tasks_text = scrolledtext.ScrolledText(self.tasks_frame, width=90, height=10, wrap=tk.WORD, bg="#3C3C3C", fg="white", font=("Helvetica", 10))
        self.tasks_text.pack(pady=5)
        self.task_entry = ttk.Entry(self.tasks_frame, width=60, font=("Helvetica", 10))
        self.task_entry.pack(pady=5)
        self.task_buttons_frame = ttk.Frame(self.tasks_frame)
        self.task_buttons_frame.pack(pady=5)
        self.add_task_button = ttk.Button(self.task_buttons_frame, text="Add Task", command=self.add_manual_task)
        self.add_task_button.pack(side=tk.LEFT, padx=5)
        self.delete_task_button = ttk.Button(self.task_buttons_frame, text="Delete Selected", command=self.delete_manual_task)
        self.delete_task_button.pack(side=tk.LEFT, padx=5)

        # Refresh Button
        self.refresh_button = ttk.Button(self.main_frame, text="Refresh Now", command=self.refresh_data)
        self.refresh_button.pack(pady=10)

        # Status Bar
        self.status_var = tk.StringVar(value="TaskBuddy - Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, background="#4A90E2", foreground="white", padding=5)
        self.status_bar.pack(fill="x", side=tk.BOTTOM)

        self.running = True
        self.refresh_callback = None  # Placeholder for backend callback

    def set_refresh_callback(self, callback):
        """Set the refresh callback from taskbuddy.py"""
        self.refresh_callback = callback

    def update_loop(self):
        pass  # Handled by taskbuddy.py

    def update_gui(self, screen_content, suggestion, calendar_events, tasks):
        self.screen_text.delete(1.0, tk.END)
        self.screen_text.insert(tk.END, screen_content)
        self.suggest_text.delete(1.0, tk.END)
        self.suggest_text.insert(tk.END, suggestion)
        self.calendar_text.delete(1.0, tk.END)
        self.calendar_text.insert(tk.END, calendar_events)
        self.tasks_text.delete(1.0, tk.END)
        self.tasks_text.insert(tk.END, tasks)
        self.status_var.set("TaskBuddy - Updated")

    def refresh_data(self):
        """Trigger manual refresh using the callback"""
        if self.refresh_callback:
            self.refresh_callback()
            self.status_var.set("TaskBuddy - Refreshed")
        else:
            self.status_var.set("TaskBuddy - Refresh not set")

    def add_manual_task(self):
        task = self.task_entry.get().strip()
        if task:
            current_tasks = self.tasks_text.get(1.0, tk.END).strip()
            if current_tasks.startswith("Add your tasks"):
                current_tasks = ""
            self.tasks_text.delete(1.0, tk.END)
            self.tasks_text.insert(tk.END, f"{current_tasks}\n{task}" if current_tasks else task)
            self.task_entry.delete(0, tk.END)
            self.status_var.set(f"TaskBuddy - Added '{task}'")

    def delete_manual_task(self):
        try:
            selected = self.tasks_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected:
                current_tasks = self.tasks_text.get(1.0, tk.END).strip().split("\n")
                current_tasks = [t for t in current_tasks if t != selected]
                self.tasks_text.delete(1.0, tk.END)
                self.tasks_text.insert(tk.END, "\n".join(current_tasks))
                self.status_var.set(f"TaskBuddy - Deleted '{selected}'")
        except tk.TclError:
            self.status_var.set("TaskBuddy - Select a task to delete")

    def on_closing(self):
        self.running = False
        self.root.destroy()