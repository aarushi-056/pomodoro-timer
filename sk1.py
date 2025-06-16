import tkinter as tk
from tkinter import messagebox, ttk
import math
import platform

# For sound alerts
if platform.system() == "Windows":
    import winsound

# ---------------------------- CONSTANTS ------------------------------- #
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

reps = 0
timer = None
session_seconds = 0
timer_running = False
pomodoro_target = None
pomodoros_completed = 0

# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    global reps, session_seconds, timer_running, timer, pomodoros_completed, pomodoro_target
    if timer is not None:
        window.after_cancel(timer)
        timer = None
    canvas.itemconfig(timer_text, text="25:00")
    title_label.config(text="Timer", fg=GREEN)
    check_marks.config(text="")
    window.config(bg=YELLOW)
    canvas.itemconfig(arc, extent=359.999)  # Reset arc
    progress_bar['value'] = 0
    reps = 0
    session_seconds = 0
    timer_running = False
    pomodoros_completed = 0
    pomodoro_target = None
    progress_bar['maximum'] = 1
    progress_bar['value'] = 0
    pomodoro_entry.config(state="normal")
    pomodoro_entry.delete(0, tk.END)
    pomodoro_entry.insert(0, "4")

# ---------------------------- GET POMODORO TARGET ------------------------------- #
def get_pomodoro_target():
    try:
        value = int(pomodoro_entry.get())
        if value < 1:
            return 1
        return value
    except:
        return 1

# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_timer():
    global reps, session_seconds, timer_running, timer, pomodoro_target, pomodoros_completed
    if timer_running:
        return  # Prevent multiple timers

    if pomodoro_target is None:
        pomodoro_target = get_pomodoro_target()
        progress_bar['maximum'] = pomodoro_target
        pomodoro_entry.config(state="readonly")  # Lock the entry after first start

    # If user already completed their target, stop here
    if pomodoros_completed >= pomodoro_target:
        messagebox.showinfo("Pomodoro Timer", f"Congratulations! You completed {pomodoro_target} Pomodoros!")
        return

    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    # Only count work sessions towards the target
    if reps % 2 == 1:  # Work session
        session_seconds = work_sec
        set_session("Work", GREEN, work_sec)
    elif reps % 8 == 0:
        session_seconds = long_break_sec
        set_session("Long Break", RED, long_break_sec)
    else:
        session_seconds = short_break_sec
        set_session("Break", PINK, short_break_sec)

    canvas.itemconfig(arc, extent=359.999)  # Full arc at start

# ---------------------------- SESSION SETUP ------------------------------- #
def set_session(label, color, seconds):
    # Background color does NOT change for work or break
    title_label.config(text=label, fg=color)
    # window.config(bg=color)  # <--- This line is removed/commented!
    play_sound_start()
    count_down(seconds)

# ---------------------------- STOP TIMER ------------------------------- #
def stop_timer():
    global timer_running, timer
    if timer_running and timer is not None:
        window.after_cancel(timer)
        timer = None
        timer_running = False

# ---------------------------- NEXT POMODORO ------------------------------- #
def next_pomodoro():
    global timer_running, timer
    if timer_running and timer is not None:
        window.after_cancel(timer)
        timer = None
    timer_running = False
    start_timer()

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    global timer, session_seconds, timer_running, pomodoros_completed, pomodoro_target, reps
    mins = math.floor(count / 60)
    secs = count % 60
    time_format = f"{mins:02d}:{secs:02d}"
    canvas.itemconfig(timer_text, text=time_format)

    # Visual Arc Countdown
    if session_seconds > 0:
        arc_extent = (count / session_seconds) * 359.999
    else:
        arc_extent = 0
    canvas.itemconfig(arc, extent=arc_extent)

    if count > 0:
        timer_running = True
        timer = window.after(1000, count_down, count - 1)
    else:
        timer_running = False
        play_sound_end()
        show_alert()
        # Only increment pomodoros_completed on work sessions
        if reps % 2 == 1:
            pomodoros_completed += 1
            update_progress()
            # If target reached, stop the cycle
            if pomodoros_completed >= pomodoro_target:
                messagebox.showinfo("Pomodoro Timer", f"Congratulations! You completed {pomodoros_completed} Pomodoros!")
                return
        # Start next session automatically after 1 second
        window.after(1000, start_timer)

def update_progress():
    progress_bar['value'] = pomodoros_completed
    marks = "✓" * pomodoros_completed
    check_marks.config(text=marks)

# ---------------------------- SOUND & VISUAL ALERTS ------------------------------- #
def play_sound_start():
    if platform.system() == "Windows":
        winsound.Beep(1500, 300)
    else:
        try:
            import os
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        except:
            pass

def play_sound_end():
    if platform.system() == "Windows":
        winsound.Beep(1000, 500)
    else:
        try:
            import os
            os.system('afplay /System/Library/Sounds/Ping.aiff')
        except:
            pass

def show_alert():
    messagebox.showinfo("Pomodoro Timer", "Time's up!")

# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Pomodoro Timer")
window.config(padx=100, pady=50, bg=YELLOW)

title_label = tk.Label(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 40, "bold"))
title_label.grid(column=1, row=0, columnspan=2)

canvas = tk.Canvas(width=220, height=224, bg=YELLOW, highlightthickness=0)
arc = canvas.create_arc(10, 10, 210, 210, start=90, extent=359.999, style='arc', outline=RED, width=10)
timer_text = canvas.create_text(110, 120, text="25:00", fill="black", font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1, columnspan=2)

# Pomodoro Target Entry
pomodoro_label = tk.Label(text="Pomodoros this session:", fg="black", bg=YELLOW, font=(FONT_NAME, 12))
pomodoro_label.grid(column=0, row=2, sticky='e')
pomodoro_entry = tk.Entry(width=5, font=(FONT_NAME, 12))
pomodoro_entry.insert(0, "4")
pomodoro_entry.grid(column=1, row=2, sticky='w')

progress_bar = ttk.Progressbar(window, orient='horizontal', length=200, mode='determinate', maximum=1)
progress_bar.grid(column=1, row=3, columnspan=2, pady=10)

start_button = tk.Button(text="Start", highlightbackground=YELLOW, command=start_timer)
start_button.grid(column=0, row=4)

stop_button = tk.Button(text="Stop", highlightbackground=YELLOW, command=stop_timer)
stop_button.grid(column=1, row=4)

next_button = tk.Button(text="Next Pomodoro", highlightbackground=YELLOW, command=next_pomodoro)
next_button.grid(column=2, row=4)

reset_button = tk.Button(text="Reset", highlightbackground=YELLOW, command=reset_timer)
reset_button.grid(column=1, row=5)

check_marks = tk.Label(fg=GREEN, bg=YELLOW, font=(FONT_NAME, 20))
check_marks.grid(column=1, row=6, columnspan=2)

window.mainloop()
