import psutil
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import configparser
import threading
import time
import win32gui
# #获取前台窗口的句柄
# handle = win32gui.GetForegroundWindow()
# win32gui.get
# #根据前台窗口的句柄获取线程tid和进程pid
# tid, pid = win32process.GetWindowThreadProcessId(handle)
# #根据前台窗口的进程pid获取进程名称
# process_name = psutil.Process(pid).name()
# print(process_name)
a=win32gui.FindWindow(None,'')
print(a)
text=win32gui.GetWindowText(a)
print(text)