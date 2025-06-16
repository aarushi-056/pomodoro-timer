import tkinter as tk
from tkinter import ttk, messagebox
import math
import platform

# For sound alerts
if platform.system() == "Windows":
    import winsound

# ---------------------------- COLORS & FONTS ------------------------------- #
BG_MAIN = "#ede9e6"      # Light gray background
BORDER_COLOR = "#222222" # Black border
ARC_COLOR = "#222222"    # Black arc
START_COLOR = "#7b9270"  # Greenish
STOP_COLOR = "#992d2b"   # Red
RESET_COLOR = "#5b7a99"  # Blue
BAR_BG = "#e6e6e6"
BAR_FG = "#bcbcbc"
FONT_NAME = "Courier New"

# ---------------------------- CONSTANTS ------------------------------- #
WORK_MIN = 2
SHORT_BREAK_MIN = 1
LONG_BREAK_MIN = 15

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
    canvas.itemconfig(arc, extent=359.999)
    title_label.config(text="Timer")
    check_marks.config(text="")
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

    if pomodoros_completed >= pomodoro_target:
        messagebox.showinfo("Pomodoro Timer", f"Congratulations! You completed {pomodoro_target} Pomodoros!")
        return

    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 2 == 1:  # Work session
        session_seconds = work_sec
        set_session(work_sec)
    elif reps % 8 == 0:
        session_seconds = long_break_sec
        set_session(long_break_sec)
    else:
        session_seconds = short_break_sec
        set_session(short_break_sec)

def set_session(seconds):
    play_sound_start()
    count_down(seconds)

# ---------------------------- STOP TIMER ------------------------------- #
def stop_timer():
    global timer_running, timer
    if timer_running and timer is not None:
        window.after_cancel(timer)
        timer = None
        timer_running = False

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    global timer, session_seconds, timer_running, pomodoros_completed, pomodoro_target, reps
    mins = math.floor(count / 60)
    secs = count % 60
    time_format = f"{mins:02d}:{secs:02d}"
    canvas.itemconfig(timer_text, text=time_format)

    # Visual Arc Countdown (big black arc)
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
        if reps % 2 == 1:
            pomodoros_completed += 1
            update_progress()
            if pomodoros_completed >= pomodoro_target:
                messagebox.showinfo("Pomodoro Timer", f"Congratulations! You completed {pomodoros_completed} Pomodoros!")
                return
        window.after(1000, start_timer)

def update_progress():
    progress_bar['value'] = pomodoros_completed
    marks = "✓" * pomodoros_completed
    check_marks.config(text=marks)

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
window.configure(bg=BORDER_COLOR)

outer_frame = tk.Frame(window, bg=BORDER_COLOR, padx=8, pady=8)
outer_frame.pack(expand=True, fill='both')

main_frame = tk.Frame(outer_frame, bg=BG_MAIN)
main_frame.pack(expand=True, fill='both')

title_label = tk.Label(main_frame, text="Timer", fg=ARC_COLOR, bg=BG_MAIN, font=(FONT_NAME, 32, "bold"))
title_label.pack(pady=(24, 8))

canvas = tk.Canvas(main_frame, width=260, height=260, bg=BG_MAIN, highlightthickness=0)
arc = canvas.create_arc(20, 20, 240, 240, start=90, extent=359.999, style='arc', outline=ARC_COLOR, width=5)
timer_text = canvas.create_text(130, 130, text="25:00", fill=ARC_COLOR, font=(FONT_NAME, 32, "bold"))
canvas.pack(pady=(0, 10))

# --- Pomodoros this session + Entry in one line ---
pomodoro_row = tk.Frame(main_frame, bg=BG_MAIN)
pomodoro_row.pack(pady=(10, 0))
pomodoro_label = tk.Label(pomodoro_row, text="Pomodoros this session:", fg=ARC_COLOR, bg=BG_MAIN, font=(FONT_NAME, 16))
pomodoro_label.pack(side="left")
pomodoro_entry = tk.Entry(pomodoro_row, width=3, font=(FONT_NAME, 16), justify='center', bg="#f5f5f5", relief='flat')
pomodoro_entry.insert(0, "4")
pomodoro_entry.pack(side="left", padx=(8, 0))

# --- Buttons ---
button_frame = tk.Frame(main_frame, bg=BG_MAIN)
button_frame.pack(pady=(20, 0))

button_font = (FONT_NAME, 14, "bold")
button_padx = 18
button_pady = 6

start_button = tk.Button(button_frame, text="Start", font=button_font, fg="white", bg=START_COLOR,
                         activebackground=START_COLOR, activeforeground="white", relief='flat',
                         padx=button_padx, pady=button_pady, command=start_timer)
start_button.grid(row=0, column=0, padx=(0, 10))

stop_button = tk.Button(button_frame, text="Stop", font=button_font, fg="white", bg=STOP_COLOR,
                        activebackground=STOP_COLOR, activeforeground="white", relief='flat',
                        padx=button_padx, pady=button_pady, command=stop_timer)
stop_button.grid(row=0, column=1, padx=(0, 10))

reset_button = tk.Button(button_frame, text="Reset", font=button_font, fg="white", bg=RESET_COLOR,
                         activebackground=RESET_COLOR, activeforeground="white", relief='flat',
                         padx=button_padx, pady=button_pady, command=reset_timer)
reset_button.grid(row=0, column=2)

# --- Progress Bar ---
progress_frame = tk.Frame(main_frame, bg=BG_MAIN)
progress_frame.pack(pady=(24, 0))

style = ttk.Style()
style.theme_use('default')
style.configure("Custom.Horizontal.TProgressbar", troughcolor=BAR_BG, background=BAR_FG,
                thickness=24, bordercolor=BAR_BG, lightcolor=BAR_BG, darkcolor=BAR_BG)

progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=220, mode='determinate',
                              maximum=1, style="Custom.Horizontal.TProgressbar")
progress_bar.pack()

check_marks = tk.Label(main_frame, fg=ARC_COLOR, bg=BG_MAIN, font=(FONT_NAME, 18))
check_marks.pack(pady=(10, 0))

window.mainloop()
()
