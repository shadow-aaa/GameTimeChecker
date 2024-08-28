import psutil
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import configparser
import threading
import time
import win32gui
import win32process

# 读取配置文件中的游戏进程路径
def load_process_paths_from_config():
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    if 'Games' in config:
        return config['Games']
    return {}

# 保存新的游戏进程路径到配置文件
def save_process_path_to_config(process_path ):
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    if 'Games' not in config:
        config['Games'] = {}
    config['Games'] [process_path]= ''  
    with open('appconfig.ini', 'w') as configfile:
        config.write(configfile)

# 获取窗口句柄对应的进程ID
def get_pid_from_hwnd(hwnd):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid

# 获取所有具有窗口的进程路径和标题
def get_windowed_processes():
    windowed_processes = {}

    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
            pid = get_pid_from_hwnd(hwnd)
            try:
                process = psutil.Process(pid)
                exe_path = process.exe()
                window_title = win32gui.GetWindowText(hwnd)
                if window_title not in windowed_processes:
                    windowed_processes[window_title] = exe_path
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    win32gui.EnumWindows(enum_windows_callback, None)
    return windowed_processes

# 弹出询问窗口让用户输入游戏时长
def ask_play_time(window_title):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    play_time = simpledialog.askfloat("游戏时长", f"窗口'{window_title}'启动，\n请输入想玩的小时数（可以是小数）：")
    root.destroy()
    return play_time

# 计时器到时提醒
def timer(process_path, play_time):
    time.sleep(play_time * 3600)  # 小时转为秒
    messagebox.showinfo("提醒", f"'{process_path}' 时间到了！")

# 添加新游戏进程到配置文件
def add_new_game():
    windowed_processes = get_windowed_processes()
    if windowed_processes:
        root = tk.Tk()
        root.title("选择游戏窗口")
        
        def on_select(event):
            selected_title = combobox.get()
            if selected_title in windowed_processes:
                selected_path = windowed_processes[selected_title]
                save_process_path_to_config(selected_path)
                root.destroy()
            else:
                messagebox.showwarning("警告", "请选择一个有效的窗口。")
        
        tk.Label(root, text="选择窗口标题:").pack(pady=10)
        combobox = ttk.Combobox(root, values=list(windowed_processes.keys()), width=80)
        combobox.pack(pady=10)
        combobox.bind("<<ComboboxSelected>>", on_select)
        
        select_button = tk.Button(root, text="确定选择", command=lambda: on_select(None))
        select_button.pack(pady=10)
        
        root.mainloop()
    else:
        messagebox.showwarning("警告", "未检测到任何具有窗口的进程。")

# 检测目标进程路径是否正在运行
def check_process_paths(target_paths):
    current_paths = set()
    for proc in psutil.process_iter(['pid', 'exe']):
        try:
            if proc.info['exe']:
                current_paths.add(proc.info['exe'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    for path in target_paths:
        if path in current_paths:
            return path
    return None

# 主程序逻辑
def main():
    # 加载配置文件中已有的游戏进程路径
    process_paths = load_process_paths_from_config()
    
    # 创建一个按钮来录入新游戏进程
    root = tk.Tk()
    root.title("游戏时长管理")
    
    def on_add_button_click():
        add_new_game()
    
    add_button = tk.Button(root, text="录入新游戏窗口", command=on_add_button_click)
    add_button.pack(pady=20)
    
    def check_game_process():
        process_paths = load_process_paths_from_config()
        running_path = check_process_paths(process_paths.values())
        if running_path:
            for title, path in process_paths.items():
                if path == running_path:
                    play_time = ask_play_time(title)
                    if play_time:
                        threading.Thread(target=timer, args=(running_path, play_time)).start()
                    break
        
        root.after(60000, check_game_process)  # 每分钟检测一次
    
    check_game_process()
    root.mainloop()

if __name__ == '__main__':
    main()
