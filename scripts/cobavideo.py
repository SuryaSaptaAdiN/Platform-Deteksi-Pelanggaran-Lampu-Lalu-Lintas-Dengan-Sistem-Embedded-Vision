import cv2
import time
from ultralytics import YOLO

# Load model YOLO (ganti path jika perlu)
model = YOLO("/home/surya/Desktop/PA/models/yolov11n.pt")  # atau 'yolov8n.pt', 'yolov11n.pt', dll

# Ganti dengan path video lokal Anda
video_path = "/home/surya/Desktop/PA/sample/2025-05-01 14-30-52.mkv"  # Contoh: "/home/surya/Downloads/test_video.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Gagal membuka video file.")
    exit()

# Dapatkan fps video untuk play back natural (opsional)
video_fps = cap.get(cv2.CAP_PROP_FPS)
wait_time = int(1000 / video_fps)  # Konversi ke milidetik

while True:
    start_time = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Video selesai atau frame rusak.")
        break

    # Deteksi objek dengan YOLO
    results = model.predict(source=frame, conf=0.7, imgsz=192, verbose=False)

    # Gambar hasil prediksi
    annotated_frame = results[0].plot()

    # Hitung FPS inferensi
    fps = 1.0 / (time.time() - start_time)
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Tampilkan frame
    cv2.imshow("YOLO Video Detection", annotated_frame)

    # Tekan 'q' untuk keluar atau tunggu waktu antar frame video
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

# Bersihkan
cap.release()
cv2.destroyAllWindows()
