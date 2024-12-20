
def c_cickRo(x,y):
    from ctypes import windll, POINTER, c_long,c_wchar_p
    import win32api
    from time import sleep
    # ระบุ path ของไลบรารี AutoItX3_x64.dll หรือ AutoItX3.dll
    path = r".\AutoItX3_x64.dll"
    # โหลดไลบรารี AutoItX3_x64.dll หรือ AutoItX3.dll
    autoit = windll.LoadLibrary(path)
    # ดึงค่า x และ y ของตำแหน่งปัจจุบันของเมาส์
    # พิมพ์ค่า x และ y ที่ได้
    print(f"Current Mouse Position: ({x}, {y})")
    autoit.AU3_MouseClick(None, int(x), int(y), 1, 1, 0)
    #autoit.AU3_Send("{ENTER}", 0)
    #autoit.AU3_Send("{F1}", 0)





#################################
import win32api
import win32con
import win32gui
from time import sleep
from keyboardData import VK_CODE
# game_windows = 'Ragnarok Landverse'
game_windows = 'Ragnarok'

def send_keys(key,hold_duration=0.1):
    hwnd = win32gui.FindWindow(game_windows, game_windows)
    keycode = VK_CODE[key]
    #print(VK_CODE[key])
    #OX70 คือ F11 เอามาจาก 
    #http://www.kbdedit.com/manual/low_level_vk_list.html
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN,keycode, 0)
    sleep(hold_duration)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP,keycode, 0)

def control_click(x,y):
    hwnd = win32gui.FindWindow(game_windows, game_windows)
    l_param = win32api.MAKELONG(x,y)
    win32gui.SendMessage(hwnd,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,l_param)
    sleep(0.1)
    win32gui.SendMessage(hwnd,win32con.WM_LBUTTONUP,win32con.MK_LBUTTON,l_param)
    
# def send_input(hwid, msg):
#     for c in msg:
#         if c == "\n":
#             win32api.SendMessage(hwid, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
#             sleep(0.1)
#             win32api.SendMessage(hwid, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
#         else:
#             win32api.SendMessage(hwid, win32con.WM_CHAR, ord(c), 0) 

def win32_clickRo(x, y,):
    hwnd = win32gui.FindWindow(game_windows, game_windows)
    rect = win32gui.GetWindowRect(hwnd)
    screen_x = rect[0] + x
    screen_y = rect[1] + y
    win32api.SetCursorPos((screen_x, screen_y))
    sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
    sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
