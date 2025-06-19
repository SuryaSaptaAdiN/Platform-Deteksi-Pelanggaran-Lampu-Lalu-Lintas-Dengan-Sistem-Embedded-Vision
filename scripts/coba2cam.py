import cv2
import time
from datetime import datetime
from ultralytics import YOLO
import numpy as np

# Load kedua model YOLO
model1 = YOLO("/home/surya/Desktop/PA/models/yolov11n.pt")  # Model pertama
model2 = YOLO("/home/surya/Desktop/PA/models/yolov11n.pt")  # Model kedua

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)

if not cap1.isOpened() or not cap2.isOpened():
    print("Error: Kamera gagal dibuka.")
    exit()

# Konfigurasi tampilan
window_name = "Dual Camera Detection"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    start_time = time.time()
    
    # Baca frame dari kedua kamera
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    
    if not ret1 or not ret2:
        print("Frame kosong atau video selesai.")
        break
    
    # Resize frame agar ukurannya sama (opsional)
    frame1 = cv2.resize(frame1, (640, 480))
    frame2 = cv2.resize(frame2, (640, 480))
    
    # Proses frame pertama dengan model1
    results1 = model1.predict(source=frame1, conf=0.5, imgsz=192, verbose=False)
    for result in results1:
        for box in result.boxes:
            cls_id = int(box.cls)
            label = model1.names[cls_id]
            conf = float(box.conf[0]) * 100
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame1, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame1, f"{label} {conf:.1f}%", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Proses frame kedua dengan model2
    results2 = model2.predict(source=frame2, conf=0.5, imgsz=192, verbose=False)
    for result in results2:
        for box in result.boxes:
            cls_id = int(box.cls)
            label = model2.names[cls_id]
            conf = float(box.conf[0]) * 100
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame2, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame2, f"{label} {conf:.1f}%", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Gabungkan kedua frame secara horizontal
    combined_frame = cv2.hconcat([frame1, frame2])
    
    # Hitung FPS
    fps = 1.0 / (time.time() - start_time)
    cv2.putText(combined_frame, f"FPS: {fps:.2f}", (10, 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Tampilkan hasil
    cv2.imshow(window_name, combined_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap1.release()
cap2.release()
cv2.destroyAllWindows()
