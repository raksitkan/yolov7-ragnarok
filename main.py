import cv2
from Windowscapture import WindowCapture
import torch
import os
import numpy as np
import warnings
import time
from click_ro import win32_clickRo,send_keys  # นำเข้า win32_clickRo จากไฟล์ click_test
import random
from time import sleep
# ปิดคำเตือน
warnings.filterwarnings("ignore", category=FutureWarning)

# เลือก GPU หรือ CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# โหลดโมเดล YOLOv7
model = torch.hub.load(
    "WongKinYiu/yolov7", "custom", "model/ragnarok_tiny.pt", force_reload=False
)
model = model.to(device)
model.conf = 0.25  # ความเชื่อมั่นขั้นต่ำ
model.iou = 0.10  # ค่า IOU Threshold

# ระบุชื่อหน้าต่างเกม
window_name = "Ragnarok"
capture = WindowCapture(window_name)
# ตัวแปรติดตามเวลาคลิกและตรวจจับ
last_click_time = 0
click_delay = 2  # หน่วงเวลาคลิก (วินาที)
last_non_player_detection_time = time.time()  # เริ่มต้นการติดตามเวลาตรวจจับคลาสอื่น
SLEEPWALK = 0.5  # เวลาในการหน่วงหลังการเดิน

# เริ่มลูปการจับภาพและตรวจจับวัตถุ
while True:
    # จับภาพจากหน้าต่างเกม
    screenshot = capture.screenshot(method="win32")

    # แปลงภาพเป็น RGB สำหรับโมเดล
    img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

    # ใช้โมเดลตรวจจับวัตถุ
    with torch.no_grad():
        results = model(img_rgb)

    # ดึงข้อมูลการตรวจจับ
    detections = results.pandas().xyxy[0]  # ผลลัพธ์ในรูป DataFrame

    # พิกัดสำหรับ player (ต้นทางของเส้น)
    player_x, player_y = 412, 300 # เก็บพิกัดของ player

    # รายการมอนสเตอร์ที่ตรวจจับได้
    monsters = []

    # วนลูปวัตถุที่ตรวจจับได้
    for _, row in detections.iterrows():
        x_min, y_min, x_max, y_max = (
            int(row["xmin"]),
            int(row["ymin"]),
            int(row["xmax"]),
            int(row["ymax"]),
        )
        class_id = int(row["class"])  # ดึง class ID ของวัตถุ
        confidence = row["confidence"]  # ดึงค่าความมั่นใจ
        class_name = model.names[class_id]  # ชื่อคลาสของวัตถุ

        # คำนวณจุดศูนย์กลางของกรอบ
        object_center_x = (x_min + x_max) // 2
        object_center_y = (y_min + y_max) // 2

        # กรณีคลาสเป็น "player" ให้บันทึกพิกัดศูนย์กลางไว้
        if class_id == 0:  # player
            player_x, player_y = object_center_x, object_center_y

            # วาดกรอบและชื่อคลาสบน player
            cv2.rectangle(screenshot, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(
                screenshot,
                f"{class_name} {confidence:.2f}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
        else:
            # กรณีคลาสอื่นที่ไม่ใช่ "player"
            monsters.append((object_center_x, object_center_y, class_name, confidence))
            # print(f"เจอ {class_name} ตำแหน่ง x {object_center_x} ตำแหน่ง y {object_center_y}")
            # วาดกรอบและชื่อคลาสบนวัตถุ
            cv2.rectangle(screenshot, (x_min, y_min), (x_max, y_max), (255, 0, 255), 2)
            cv2.putText(
                screenshot,
                f"{class_name} {confidence:.2f}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 0, 255),
                2,
            )

    # คำนวณและคลิกมอนสเตอร์ที่ใกล้ที่สุด
    if player_x is not None and player_y is not None and monsters:
        nearest_monster = min(
            monsters, key=lambda m: (m[0] - player_x) ** 2 + (m[1] - player_y) ** 2
        )

        nearest_x, nearest_y, _, _ = nearest_monster
        if time.time() - last_click_time > click_delay:
            print(f" โจมตี {class_name} ตำแหน่ง x {nearest_x} ตำแหน่ง y {nearest_y}")
            # win32_clickRo(nearest_x, nearest_y)
            # win32_clickRo(nearest_x, nearest_y)
            last_click_time = time.time()  # อัปเดตเวลาคลิกล่าสุด

    # แสดงภาพที่มีการตรวจจับและเวลาที่นับ
    elapsed_time = time.time() - last_non_player_detection_time
    if elapsed_time >= 5:
        print("ไม่พบคลาสอื่นใน 5 วินาที")
        send_keys("F1")
        last_non_player_detection_time = time.time()  # รีเซ็ตเวลาตรวจจับล่าสุด

    cv2.putText(
        screenshot,
        f"Time since last detection: {elapsed_time:.2f} sec",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )
    cv2.imshow("Detection", screenshot)

    # กด 'q' เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ทำความสะอาดทรัพยากร
capture.release()  # ปิดการจับภาพ
cv2.destroyAllWindows()
