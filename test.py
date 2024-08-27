import psutil
import win32process
import win32gui

#获取前台窗口的句柄
handle = win32gui.GetForegroundWindow()
win32gui.get
#根据前台窗口的句柄获取线程tid和进程pid
tid, pid = win32process.GetWindowThreadProcessId(handle)

#根据前台窗口的进程pid获取进程名称
process_name = psutil.Process(pid).name()
