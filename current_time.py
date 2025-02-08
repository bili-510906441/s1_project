import tkinter as tk
from datetime import datetime
from current_time_settings import *

if reset_to_default == True:
    import base64
    with open('current_time_settings.py', 'r+', encoding='utf-8') as f:
        f.seek(0)
        f.truncate()
        default_text = 'IyDov5nmmK9jdXJyZW50X3RpbWUucHnnmoTphY3nva7mlofku7YKIyBDb25maWd1cmF0aW9ucwoKZm9udF9zaXplID0gNDAKcmVmcmVzaF90aW1lID0gMTAwMAp3aW5kb3dfdG9wbW9zdCA9IFRydWUKcmVzZXRfdG9fZGVmYXVsdCA9IEZhbHNl'
        decoded_text = base64.b64decode(default_text).decode('utf-8')
        f.write(decoded_text)
    raise SystemExit
    
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