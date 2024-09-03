import psutil
import pygetwindow as gw
import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import win32gui
import win32process
import sys

# 创建系统托盘图标
def create_image():
    width = 64
    height = 64
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill="black")
    return image

def on_quit(icon, item=None):
    if hasattr(hide_app_window, "icon"):
        hide_app_window.icon.stop()  # 停止托盘图标
    root.quit()  # 退出Tkinter主循环
    sys.exit(0)  # 退出程序

def show_app_window(icon, item=None):
    root.deiconify()
    if hasattr(hide_app_window, "icon"):
        icon.stop()

def hide_app_window():
    root.withdraw()
    # 确保托盘图标仍然显示
    if not hasattr(hide_app_window, "icon"):
        menu = Menu(MenuItem('显示主界面', show_app_window), MenuItem('退出', on_quit))
        hide_app_window.icon = Icon("进程监控", create_image(), "进程监控", menu)
        hide_app_window.icon.run_detached()
    else:
        hide_app_window.icon.run_detached()

def on_double_click(icon, item=None):
    show_app_window(icon)

def monitor_process(pid, run_time, title, stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        current_time = time.time()
        elapsed_time = (current_time - start_time) / 60  # 转换为分钟
        if elapsed_time > run_time:
            if psutil.pid_exists(pid):
                root.after(0, lambda: messagebox.showwarning("时间到", f"{title} 运行超时！"))
            break
        time.sleep(60)

def on_select_title():
    selected_title = title_var.get()

    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, selected_title)
    if hwnd == 0:
        messagebox.showerror("错误", "无法找到与所选标题对应的窗口")
        return

    # 获取进程ID
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    if pid is None:
        messagebox.showerror("错误", "无法找到与所选标题对应的进程")
        return

    # 输入监控时间
    run_time = simpledialog.askfloat("输入时间", "请输入运行时间（分钟）：", minvalue=0.1)
    
    if run_time is None:
        return  # 用户取消输入时间

    # 隐藏窗口并置于系统托盘
    hide_app_window()

    # 创建一个线程停止事件
    stop_event = threading.Event()

    # 启动后台线程监控进程
    threading.Thread(target=monitor_process, args=(pid, run_time, selected_title, stop_event)).start()

# 获取当前所有窗口的标题
window_titles = [title for title in gw.getAllTitles() if title]

# 创建主窗口
root = tk.Tk()
root.title("进程监控")
root.geometry("300x150")

# 创建下拉框选择窗口标题
title_var = tk.StringVar(root)
title_var.set(window_titles[0])  # 设置默认选项

tk.Label(root, text="请选择要监控的窗口标题：").pack(pady=10)
title_dropdown = tk.OptionMenu(root, title_var, *window_titles)
title_dropdown.pack(pady=10)

# 确认按钮
confirm_button = tk.Button(root, text="确认", command=on_select_title)
confirm_button.pack(pady=10)

# 绑定最小化按钮行为
root.bind("<Unmap>", lambda event: hide_app_window() if root.state() == 'iconic' else None)

# 保持关闭按钮默认行为，退出程序
root.protocol("WM_DELETE_WINDOW", lambda: on_quit(hide_app_window.icon))

# 启动托盘图标并绑定双击事件
if not hasattr(hide_app_window, "icon"):
    menu = Menu(MenuItem('显示主界面', show_app_window), MenuItem('退出', on_quit))
    hide_app_window.icon = Icon("进程监控", create_image(), "进程监控", menu)
    hide_app_window.icon.run_detached(on_double_click)

# 启动Tkinter主循环
root.mainloop()
