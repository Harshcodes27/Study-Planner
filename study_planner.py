import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("study_planner.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Tasks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    name TEXT,
    subject TEXT,
    deadline TEXT,
    priority INTEGER,
    duration REAL
)
""")

conn.commit()

current_user = None

# ---------------- AUTH FUNCTIONS ----------------

def signup():
    username = user_entry.get()
    password = pass_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Fill all fields")
        return

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Account Created!")
    except:
        messagebox.showerror("Error", "User already exists!")


def login():
    global current_user
    username = user_entry.get()
    password = pass_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        current_user = username
        messagebox.showinfo("Success", f"Welcome {username}!")
        open_main_app()
    else:
        messagebox.showerror("Error", "Invalid credentials")


# ---------------- MAIN APP ----------------

def open_main_app():
    login_frame.pack_forget()
    app_frame.pack()

def add_task():
    name = name_entry.get()
    subject = subject_entry.get()
    deadline = deadline_entry.get()
    priority = priority_var.get()
    duration = duration_entry.get()

    if not name or not subject or not deadline or not duration:
        messagebox.showerror("Error", "All fields required!")
        return

    try:
        datetime.datetime.strptime(deadline, "%Y-%m-%d")
        duration = float(duration)
    except:
        messagebox.showerror("Error", "Invalid input!")
        return

    cursor.execute("""
    INSERT INTO tasks (user, name, subject, deadline, priority, duration)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (current_user, name, subject, deadline, priority, duration))

    conn.commit()
    messagebox.showinfo("Success", "Task Added!")
    view_tasks()


def view_tasks():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM tasks WHERE user=?", (current_user,))
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def delete_task():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select a task!")
        return

    item = tree.item(selected[0])
    task_id = item["values"][0]

    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

    messagebox.showinfo("Deleted", "Task removed!")
    view_tasks()


def generate_plan():
    cursor.execute("SELECT * FROM tasks WHERE user=?", (current_user,))
    tasks = cursor.fetchall()

    if not tasks:
        messagebox.showinfo("Info", "No tasks available")
        return

    today = datetime.datetime.now()

    tasks.sort(key=lambda x: (x[5], x[4]))  # priority + deadline

    result = "📅 Smart Study Plan:\n\n"

    for task in tasks:
        name, subject, deadline, priority, duration = task[2], task[3], task[4], task[5], task[6]

        deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
        days_left = (deadline_date - today).days
        if days_left <= 0:
            days_left = 1

        daily_time = duration / days_left

        result += f"{name} ({subject})\n"
        result += f"Deadline: {deadline}\n"
        result += f"Study: {round(daily_time,2)} hrs/day\n\n"

    messagebox.showinfo("Study Plan", result)


# ---------------- GUI ----------------

root = tk.Tk()
root.title("AI Study Planner")
root.geometry("800x500")

# LOGIN FRAME
login_frame = tk.Frame(root)
login_frame.pack(expand=True)

tk.Label(login_frame, text="Username").grid(row=0, column=0)
user_entry = tk.Entry(login_frame)
user_entry.grid(row=0, column=1)

tk.Label(login_frame, text="Password").grid(row=1, column=0)
pass_entry = tk.Entry(login_frame, show="*")
pass_entry.grid(row=1, column=1)

tk.Button(login_frame, text="Login", command=login).grid(row=2, column=0)
tk.Button(login_frame, text="Signup", command=signup).grid(row=2, column=1)

# MAIN APP FRAME
app_frame = tk.Frame(root)

tk.Label(app_frame, text="Task Name").grid(row=0, column=0)
name_entry = tk.Entry(app_frame)
name_entry.grid(row=0, column=1)

tk.Label(app_frame, text="Subject").grid(row=1, column=0)
subject_entry = tk.Entry(app_frame)
subject_entry.grid(row=1, column=1)

tk.Label(app_frame, text="Deadline").grid(row=2, column=0)
deadline_entry = tk.Entry(app_frame)
deadline_entry.grid(row=2, column=1)

tk.Label(app_frame, text="Priority").grid(row=3, column=0)
priority_var = tk.IntVar(value=1)
tk.OptionMenu(app_frame, priority_var, 1, 2, 3).grid(row=3, column=1)

tk.Label(app_frame, text="Duration").grid(row=4, column=0)
duration_entry = tk.Entry(app_frame)
duration_entry.grid(row=4, column=1)

tk.Button(app_frame, text="Add Task", command=add_task).grid(row=5, column=0)
tk.Button(app_frame, text="Delete Task", command=delete_task).grid(row=5, column=1)
tk.Button(app_frame, text="Generate Plan", command=generate_plan).grid(row=6, column=0, columnspan=2)

columns = ("ID", "User", "Name", "Subject", "Deadline", "Priority", "Duration")
tree = ttk.Treeview(app_frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.grid(row=7, column=0, columnspan=4)

root.mainloop()