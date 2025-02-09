import tkinter as tk
from datetime import datetime

font_size = 30
refresh_time = 1000
window_topmost = True
    
def update_time():
    now = datetime.now()
    time_string = now.strftime("%H:%M:%S")
    time_label.config(text=time_string)
    time_label.after(refresh_time, update_time)

root = tk.Tk()
root.title("current_time s1_project")
root.overrideredirect(True)
root.wm_attributes("-topmost", window_topmost)

time_label = tk.Label(root, font=('Arial', font_size), bg='white')
time_label.pack(padx=0, pady=0)
 
update_time()

root.mainloop()
