import win32gui, win32ui
import numpy as np
from ctypes import windll
import pygetwindow as gw
import pyautogui 
import cv2 as cv

class WindowCapture:
    def __init__(self, window_name):
        # Find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))
        
        # ใช้ pygetwindow ดึงข้อมูลหน้าต่างเพิ่มเติม
        self.win = gw.getWindowsWithTitle(window_name)
        if not self.win:
            raise Exception('Window not found with pygetwindow: {}'.format(window_name))
        self.win = self.win[0]  # ใช้หน้าต่างตัวแรกที่เจอ

        # คำนวณขอบเขตภายในหน้าต่าง (Client Area)
        self._calculate_client_area()

    def _calculate_client_area(self):
        """คำนวณขอบเขตภายในหน้าต่าง (ไม่รวมขอบและส่วนหัว)"""
        window_rect = win32gui.GetWindowRect(self.hwnd)  # ขอบเขตทั้งหมดของหน้าต่าง
        client_rect = win32gui.GetClientRect(self.hwnd)  # ขอบเขตเนื้อหาภายใน

        # ตำแหน่งเริ่มต้นของ client area
        border_width = (window_rect[2] - window_rect[0] - client_rect[2]) // 2
        title_bar_height = (window_rect[3] - window_rect[1] - client_rect[3] - border_width)

        self.left = window_rect[0] + border_width
        self.top = window_rect[1] + title_bar_height
        self.width = client_rect[2]
        self.height = client_rect[3]

    def screenshot_with_pyautogui(self):
        """จับภาพหน้าต่างโดยใช้ pyautogui และแก้ไขสี"""
        # ระบุขอบเขตของหน้าต่าง (ตำแหน่ง x, y, กว้าง, สูง)
        region = (self.left, self.top, self.width, self.height)
        
        # ถ่ายภาพหน้าจอเฉพาะบริเวณหน้าต่าง
        screenshot = pyautogui.screenshot(region=region)
        
        # แปลงเป็น NumPy array
        screenshot = np.array(screenshot)
        
        # แก้ไขสี (จาก RGB → BGR) สำหรับ OpenCV
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
        
        return screenshot

    def screenshot_with_win32(self):
        """จับภาพหน้าต่างโดยใช้ win32 API"""
        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
        save_dc.SelectObject(bitmap)
        
        # If Special K is running, this number is 3. If not, 1
        result = windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 3)
        if result != 1:
            raise Exception("Failed to capture window using PrintWindow")

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        img = img[..., :3]
        img = np.ascontiguousarray(img)  # Make image C_CONTIGUOUS and drop alpha channel
        
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwnd_dc)
        
        return img

    def screenshot(self, method="win32"):
        """เลือกวิธีการจับภาพหน้าจอ"""
        if method == "pyautogui":
            return self.screenshot_with_pyautogui()
        elif method == "win32":
            return self.screenshot_with_win32()
        else:
            raise ValueError("Invalid screenshot method. Choose 'pyautogui' or 'win32'.")

# # ตัวอย่างการใช้งาน
# if __name__ == "__main__":
#     window_name = "Your Window Name"
#     capture = WindowCapture(window_name)
    
#     # จับภาพด้วย pyautogui
#     img_pyautogui = capture.screenshot(method="pyautogui")
#     cv.imwrite("pyautogui_capture.png", img_pyautogui)
    
#     # จับภาพด้วย win32
#     img_win32 = capture.screenshot(method="win32")
#     cv.imwrite("win32_capture.png", img_win32)
    
#     print("Captured images successfully!")
