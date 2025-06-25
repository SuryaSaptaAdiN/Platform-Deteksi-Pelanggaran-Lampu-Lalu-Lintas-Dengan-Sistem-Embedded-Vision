# 🚦 Platform Deteksi Pelanggaran Lampu Lalu Lintas Dengan Sistem Embedded Vision

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![YOLOv11](https://img.shields.io/badge/YOLO-v11-yellow.svg)](https://github.com/ultralytics/ultralytics)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

## 📋 Deskripsi

Platform deteksi pelanggaran lampu lalu lintas berbasis computer vision yang menggunakan sistem embedded (Raspberry Pi) untuk mendeteksi kendaraan yang melanggar lampu merah berdasarkan deteksi garis marka melintang. Sistem ini dilengkapi dengan monitoring performa real-time, transfer file otomatis, dan sistem database untuk penyimpanan data pelanggaran.

### ✨ Fitur Utama

- 🚗 **Deteksi Kendaraan Real-time**: Menggunakan model YOLOv11 untuk deteksi berbagai jenis kendaraan
- 🛣️ **Deteksi Garis Marka**: Algoritma computer vision untuk mendeteksi garis marka melintang jalan
- 🚦 **Simulasi Lampu Lalu Lintas**: Sistem looping otomatis untuk simulasi siklus lampu lalu lintas
- 📊 **Monitoring Sistem**: Monitor CPU, RAM, GPU, suhu, dan konsumsi daya secara real-time
- 📤 **Transfer File Otomatis**: Upload gambar pelanggaran ke server melalui SSH/SFTP
- 🗄️ **Database Integration**: Penyimpanan data pelanggaran ke MySQL database
- 🔄 **Anti-Duplikasi**: Sistem pencegahan duplikasi data dan gambar
- 📈 **Laporan Performa**: Laporan statistik performa sistem setelah eksekusi

## 🛠️ Teknologi yang Digunakan

### Hardware
- **Raspberry Pi 5** (8GB RAM minimum)
- **Camera Module** atau USB Camera
- **MicroSD Card** (32GB minimum, Class 10)

### Software Stack
- **Python 3.8+**
- **OpenCV 4.5+** - Computer vision dan image processing
- **YOLOv11 (Ultralytics)** - Object detection
- **MySQL 8.0+** - Database management
- **Paramiko** - SSH/SFTP file transfer
- **NumPy** - Numerical computing
- **psutil** - System monitoring
- **GPUtil** - GPU monitoring

## 🔧 Instalasi dan Setup

### 1. Persiapan Environment

#### Instalasi Miniconda (Raspberry Pi)
```bash
# Download Miniconda untuk ARM64
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh

# Install Miniconda
bash Miniconda3-latest-Linux-aarch64.sh

# Restart terminal atau jalankan:
source ~/.bashrc
```

#### Membuat Environment Conda
```bash
# Buat environment baru
conda create -n traffic_detection python=3.8 -y

# Aktivasi environment
conda activate traffic_detection
```

### 2. Instalasi Dependencies

```bash
# Install paket utama melalui conda
conda install -c conda-forge opencv numpy -y

# Install paket melalui pip
pip install ultralytics
pip install mysql-connector-python
pip install paramiko
pip install psutil
pip install GPUtil
```

### 3. Setup Database MySQL

#### Instalasi MySQL Server
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server -y

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### Konfigurasi Database
```sql
-- Login ke MySQL sebagai root
sudo mysql -u root -p

-- Buat database
CREATE DATABASE traffic_violation_db;

-- Buat user khusus
CREATE USER 'trafficuser'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON traffic_violation_db.* TO 'trafficuser'@'localhost';
FLUSH PRIVILEGES;

-- Gunakan database
USE traffic_violation_db;

-- Buat tabel violations
CREATE TABLE violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Setup SSH Server (untuk transfer file)

#### Raspberry Pi (Client)
```bash
# Install SSH client (biasanya sudah terinstall)
sudo apt install openssh-client -y
```

#### Laptop/PC Tujuan (Server)
```bash
# Windows: Install OpenSSH Server melalui Windows Features
# atau download dari Microsoft Store

# Linux: Install OpenSSH Server
sudo apt install openssh-server -y
sudo systemctl start ssh
sudo systemctl enable ssh

# Cek status
sudo systemctl status ssh
```

### 5. Download Model YOLO

```bash
# Buat direktori models
mkdir -p ~/Desktop/PA/models

# Download model YOLOv11 nano (opsional, akan otomatis download saat pertama kali run)
# Model akan tersimpan di ~/.ultralytics/
```

## ⚙️ Konfigurasi

### 1. Konfigurasi Database
Edit bagian konfigurasi database dalam script:
```python
db = mysql.connector.connect(
    host="localhost",           # IP database server
    user="trafficuser",         # Username database
    password="password123",     # Password database
    database="traffic_violation_db"  # Nama database
)
```

### 2. Konfigurasi Transfer File SSH/SFTP
Edit konfigurasi `LAPTOP_CONFIG`:
```python
LAPTOP_CONFIG = {
    'hostname': '192.168.43.118',    # IP address laptop tujuan
    'username': 'surya',             # Username laptop
    'password': 'Nugraha123',        # Password laptop
    'port': 22,                      # Port SSH (default 22)
    'remote_path': 'D:/PA/Koding/traffic_violation_detection/detections',  # Path tujuan
    'timeout': 30,
    'banner_timeout': 30,
    'auth_timeout': 30,
    'keepalive_interval': 30
}
```

### 3. Konfigurasi Path
```python
# Path output gambar hasil deteksi
output_dir = "/home/surya/Desktop/PA/detections"

# Path model YOLO
model_path = "/home/surya/Desktop/PA/models/yolov11n1.pt"
```

### 4. Konfigurasi Siklus Lampu Lalu Lintas
```python
# Durasi tiap warna lampu (dalam detik)
dur_red = 60      # Lampu merah
dur_yellow = 1    # Lampu kuning
dur_green = 1     # Lampu hijau
```

## 🚀 Cara Menjalankan

### 1. Persiapan
```bash
# Aktivasi environment conda
conda activate traffic_detection

# Pastikan direktori output ada
mkdir -p ~/Desktop/PA/detections
mkdir -p ~/Desktop/PA/models

# Pastikan kamera terhubung
lsusb  # untuk USB camera
# atau
vcgencmd get_camera  # untuk Raspberry Pi camera module
```

### 2. Menjalankan Program
```bash
# Clone repository
git clone https://github.com/SuryaSaptaAdiN/Platform-Deteksi-Pelanggaran-Lampu-Lalu-Lintas-Dengan-Sistem-Embedded-Vision.git

# Masuk ke direktori
cd Platform-Deteksi-Pelanggaran-Lampu-Lalu-Lintas-Dengan-Sistem-Embedded-Vision

# Jalankan program
python traffic_violation_detection.py
```

### 3. Kontrol Program
- **Tekan 'q'** untuk menghentikan program
- **Monitor real-time** ditampilkan di jendela video dan terminal
- **Data pelanggaran** otomatis tersimpan ke database dan dikirim ke laptop

## 📊 Fitur Monitoring Sistem

Program dilengkapi dengan **SystemMonitor** class yang memantau:

### Metrics yang Dipantau:
- **CPU Usage** - Persentase penggunaan CPU
- **RAM Usage** - Persentase dan penggunaan memori dalam MB
- **GPU Usage** - Persentase penggunaan GPU (jika tersedia)
- **Temperature** - Suhu CPU dalam Celsius
- **Power Consumption** - Estimasi konsumsi daya dalam Watt
- **FPS** - Frame per second dari video processing
- **Transfer Queue** - Jumlah file dalam antrian transfer

### Laporan Statistik:
Program menghasilkan laporan lengkap berdasarkan status lampu:
- Statistik per status lampu (RED, YELLOW, GREEN)
- Rata-rata, minimum, dan maksimum untuk setiap metric
- Total runtime dan jumlah sample data

## 🗂️ Struktur Output

### 1. File Gambar
```
~/Desktop/PA/detections/
├── car_20241225_143022.jpg          # Gambar pelanggaran
├── motorcycle_20241225_143045.jpg   # Format: {label}_{timestamp}.jpg
└── sent_images.json                 # Log file yang sudah dikirim
```

### 2. Database
```sql
-- Tabel violations
+----+-------+---------------------+---------------------------+---------------------+
| id | label | timestamp           | image_path                | created_at          |
+----+-------+---------------------+---------------------------+---------------------+
| 1  | car   | 2024-12-25 14:30:22 | car_20241225_143022.jpg   | 2024-12-25 14:30:22|
| 2  | bike  | 2024-12-25 14:30:45 | bike_20241225_143045.jpg  | 2024-12-25 14:30:45|
+----+-------+---------------------+---------------------------+---------------------+
```

### 3. Metadata Transfer
Setiap gambar dikirim bersama file metadata JSON:
```json
{
  "label": "car",
  "timestamp": "2024-12-25 14:30:22",
  "fps": 15.23,
  "confidence": 85.6,
  "bounding_box": [120, 150, 250, 300],
  "vehicle_position": 225,
  "road_marking_position": 200,
  "violation_type": "red_light_violation",
  "location": "Traffic Light Camera 1"
}
```

## 🎯 Cara Kerja Algoritma

### 1. Deteksi Garis Marka
```python
def detect_road_marking(frame):
    # 1. Ambil ROI (Region of Interest) setengah bawah frame
    roi = frame[frame.shape[0] // 2 :, :]
    
    # 2. Konversi ke HSV untuk deteksi warna putih
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # 3. Threshold untuk warna putih
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([255, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 4. Edge detection
    edges = cv2.Canny(mask, 50, 150)
    
    # 5. Hough Line Transform untuk deteksi garis horizontal
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 
                           minLineLength=180, maxLineGap=20)
    
    # 6. Filter garis horizontal dengan smoothing
    # ... (implementasi lengkap dalam kode)
```

### 2. Logika Deteksi Pelanggaran
```python
# 1. Deteksi kendaraan dengan YOLO
results = model.predict(source=frame, conf=0.6, imgsz=320)

# 2. Untuk setiap kendaraan yang terdeteksi
for box in result.boxes:
    # 3. Hitung posisi tengah kendaraan
    mid_y = (y1 + y2) // 2
    
    # 4. Cek apakah kendaraan melewati garis marka saat lampu merah
    if marka_y and mid_y > marka_y and light_status == "RED":
        # 5. PELANGGARAN TERDETEKSI!
        save_violation(...)
```

### 3. Siklus Lampu Lalu Lintas
```python
def get_looping_light_status():
    elapsed = int(time.time() - start_cycle) % cycle_time
    
    if elapsed < dur_red:
        return "RED"
    elif elapsed < dur_red + dur_yellow:
        return "YELLOW"
    elif elapsed < dur_red + dur_yellow + dur_green:
        return "GREEN"
    else:
        return "YELLOW"  # Kuning sebelum kembali ke merah
```

## 🔍 Troubleshooting

### 1. Masalah Kamera
```bash
# Cek kamera tersedia
ls /dev/video*

# Test kamera dengan fswebcam
sudo apt install fswebcam
fswebcam test.jpg

# Untuk Raspberry Pi Camera
sudo raspi-config
# Pilih Interface Options > Camera > Enable
```

### 2. Masalah Database
```bash
# Cek status MySQL
sudo systemctl status mysql

# Reset password MySQL
sudo mysql_secure_installation

# Test koneksi
mysql -u trafficuser -p traffic_violation_db
```

### 3. Masalah SSH/Transfer File
```bash
# Test koneksi SSH
ssh username@ip_address

# Cek SSH service di laptop tujuan
sudo systemctl status ssh  # Linux
# atau cek OpenSSH Server di Windows Services
```

### 4. Masalah Performa
```bash
# Monitor resource Raspberry Pi
htop
# atau
top

# Cek suhu Raspberry Pi
vcgencmd measure_temp

# Overclock Raspberry Pi (opsional, hati-hati dengan suhu)
sudo raspi-config
# Advanced Options > Overclock
```

### 5. Error Dependencies
```bash
# Reinstall dependencies
pip install --upgrade ultralytics opencv-python

# Untuk error libGL
sudo apt install libgl1-mesa-glx libglib2.0-0

# Untuk error libgthread
sudo apt install libgthread-2.0-0
```

## 📈 Optimasi Performa

### 1. Pengaturan Model YOLO
```python
# Gunakan model yang lebih kecil untuk Raspberry Pi
model = YOLO("yolov11n.pt")    # Nano (tercepat)
# model = YOLO("yolov11s.pt")  # Small
# model = YOLO("yolov11m.pt")  # Medium (lebih akurat tapi lambat)

# Sesuaikan inference settings
results = model.predict(
    source=frame, 
    conf=0.6,        # Confidence threshold
    imgsz=320,       # Input size (lebih kecil = lebih cepat)
    verbose=False    # Disable logging untuk performa
)
```

### 2. Optimasi OpenCV
```python
# Set buffer size kamera
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Set resolusi kamera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

### 3. Memory Management
```python
# Batasi history untuk mengurangi memory usage
marka_y_history = deque(maxlen=5)  # Hanya simpan 5 data terakhir
saved_images = set()  # Gunakan set untuk O(1) lookup
```

## 🤝 Kontribusi

1. Fork repository ini
2. Buat branch fitur baru (`git checkout -b feature/amazing-feature`)
3. Commit perubahan (`git commit -m 'Add some amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request

## 📝 Rencana Pengembangan

- [ ] **Web Dashboard** - Interface web untuk monitoring real-time
- [ ] **Mobile App** - Aplikasi mobile untuk notifikasi
- [ ] **Multiple Camera Support** - Dukungan multiple kamera
- [ ] **AI Model Training** - Custom model untuk kondisi Indonesia
- [ ] **Cloud Integration** - Upload ke cloud storage
- [ ] **Analytics Dashboard** - Analisis data pelanggaran
- [ ] **License Plate Recognition** - Deteksi plat nomor kendaraan

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Tim Pengembang

- **Surya Sapta Adi Nugraha** - *Initial work* - [SuryaSaptaAdiN](https://github.com/SuryaSaptaAdiN)

## 📞 Kontak

Surya Sapta Adi Nugraha - [@SuryaSaptaAdiN](https://github.com/SuryaSaptaAdiN)

Project Link: [https://github.com/SuryaSaptaAdiN/Platform-Deteksi-Pelanggaran-Lampu-Lalu-Lintas-Dengan-Sistem-Embedded-Vision](https://github.com/SuryaSaptaAdiN/Platform-Deteksi-Pelanggaran-Lampu-Lalu-Lintas-Dengan-Sistem-Embedded-Vision)

## 🙏 Acknowledgments

- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics) - Object detection framework
- [OpenCV](https://opencv.org/) - Computer vision library
- [Raspberry Pi Foundation](https://www.raspberrypi.org/) - Hardware platform
- [MySQL](https://www.mysql.com/) - Database management system

---

⭐ Jangan lupa untuk memberikan star jika project ini membantu Anda!
