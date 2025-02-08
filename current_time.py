import tkinter as tk
from datetime import datetime
 
def update_time():
    now = datetime.now()
    time_string = now.strftime("%H:%M:%S")
    time_label.config(text=time_string)
    time_label.after(1000, update_time)

root = tk.Tk()
root.title("current_time s1_project")
root.overrideredirect(True)
root.wm_attributes("-topmost", True)

time_label = tk.Label(root, font=('Arial', 40), bg='white')
time_label.pack(padx=0, pady=0)
 
update_time()

root.mainloop()