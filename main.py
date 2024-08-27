import psutil
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import configparser
import threading
import time

# 读取配置文件中的游戏进程路径
def load_process_paths_from_config():
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    if 'Games' in config:
        return config['Games']
    return {}

# 保存新的游戏进程路径到配置文件
def save_process_path_to_config(process_path):
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    if 'Games' not in config:
        config['Games'] = {}
    config['Games'][process_path] = ''  # 只保存进程路径
    with open('appconfig.ini', 'w') as configfile:
        config.write(configfile)

# 获取所有具有窗口的进程名称和路径
def get_windowed_processes():
    windowed_processes = {}
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] and proc.info['name']:
                windowed_processes[proc.info['name']] = proc.info['exe']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return windowed_processes

# 弹出询问窗口让用户输入游戏时长
def ask_play_time(process_name):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    play_time = simpledialog.askfloat("游戏时长", f"进程'{process_name}'启动，\n请输入想玩的小时数（可以是小数）：")
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
        root.title("选择游戏进程")
        
        def on_select(event):
            selected_name = combobox.get()
            if selected_name in windowed_processes:
                selected_path = windowed_processes[selected_name]
                save_process_path_to_config(selected_path)
                root.destroy()
            else:
                messagebox.showwarning("警告", "请选择一个有效的进程。")
        
        tk.Label(root, text="选择进程名称:").pack(pady=10)
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
    
    add_button = tk.Button(root, text="录入新游戏进程", command=on_add_button_click)
    add_button.pack(pady=20)
    
    def check_game_process():
        process_paths = load_process_paths_from_config()
        running_path = check_process_paths(process_paths.keys())
        if running_path:
            play_time = ask_play_time(running_path)
            if play_time:
                threading.Thread(target=timer, args=(running_path, play_time)).start()
        
        root.after(60000, check_game_process)  # 每分钟检测一次
    
    check_game_process()
    root.mainloop()

if __name__ == '__main__':
    main()
