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

# 创建系统托盘图标
def create_image():
    # 创建一个简单的黑白托盘图标
    width = 64
    height = 64
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill="black")
    return image

def on_quit(icon, item):
    icon.stop()

def show_app_window():
    root.deiconify()

def hide_app_window():
    root.withdraw()

def monitor_process(pid, run_time, title):
    start_time = time.time()
    while True:
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

    # 启动后台线程监控进程
    threading.Thread(target=monitor_process, args=(pid, run_time, selected_title)).start()

    # 创建托盘图标
    menu = Menu(MenuItem('显示主界面', show_app_window), MenuItem('退出', on_quit))
    icon = Icon("进程监控", create_image(), "进程监控", menu)
    icon.run_detached()

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
tk.Button(root, text="确认", command=on_select_title).pack(pady=10)

# 启动Tkinter主循环
root.mainloop()
