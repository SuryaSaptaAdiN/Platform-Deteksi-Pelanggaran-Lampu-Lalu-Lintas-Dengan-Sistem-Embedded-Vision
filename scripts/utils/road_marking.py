# =============================================
# FUNGSI DETEKSI GARIS MARKA JALAN
# =============================================

import cv2
import numpy as np
import time

cached_marka_y = None
last_marka_time = 0

def detect_road_marking(frame, marka_y_history):
    """Deteksi garis marka jalan dengan caching dan smoothing"""

    global cached_marka_y, last_marka_time

    # 1?? Ambil bagian bawah frame (ROI)
    roi = frame[frame.shape[0] // 2 :, :]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 2?? Deteksi warna putih
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([255, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    edges = cv2.Canny(mask, 50, 150)

    # 3?? Deteksi garis horizontal menggunakan Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=180, maxLineGap=20)
    marka_y = None

    if lines is not None:
        min_y = float("inf")
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            # Filter hanya garis horizontal
            if 0 < abs(angle) < 10 and length > frame.shape[1] // 3:
                if y1 < min_y:
                    min_y = y1
                    marka_y = y1 + frame.shape[0] // 2

        # 4?? Simpan history untuk smoothing
        if marka_y is not None:
            marka_y_history.append(marka_y)
            if len(marka_y_history) > 5:
                marka_y_history.pop(0)
            cached_marka_y = int(np.mean(marka_y_history))
            last_marka_time = time.time()

    # 5?? Jika gagal deteksi, gunakan cache sebelumnya = 1.5 detik
    if marka_y is None and cached_marka_y and (time.time() - last_marka_time < 1.5):
        marka_y = cached_marka_y

    return marka_y
