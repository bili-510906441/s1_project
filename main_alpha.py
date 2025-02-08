import os
import sys
import atexit
import math
import tkinter as tk
import datetime
from tkinter import messagebox
import platform
import ctypes

def get_info():
    pyimp = platform.python_implementation()
    ad = 'User'
    pyver = platform.python_compiler()
    osver = platform.platform()
    return 'Python Implementation: '+ pyimp + '\n' \
        'Version: ' +pyver+'\n' \
            'System Version: '+osver+'\n'+ad

if sys.platform != 'win32':
    sys.exit(1)

def show_time():
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    t1.config(text=time_now)
    t1.after(1000, show_time)

def show_info():
    messagebox.showinfo('关于', get_info())

if __name__ == '__main__':
    w = tk.Tk()
    w.geometry('800x600')
    w.resizable(False, False)
    w.title('s6')
    w.configure(background='#000000')
    b1 = tk.Button(w, text='关于', font='HYWenHei-85W', fg='black', bg='#ffffff', relief='flat', command=show_info)
    b1.pack()
    b1.place(x=100, y=100)
    t1 = tk.Label(w, font=('HYRunYuan-65W', 30))
    t1.pack()
    t1.place(x=10, y=10)
    show_time()
    w.mainloop()
