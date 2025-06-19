# =============================================
# KONFIGURASI MODEL DAN JALUR
# =============================================

import os

MODEL_PATH = "/home/surya/Desktop/PA/models/yolov11n1.pt"
output_dir = "/home/surya/Desktop/PA/detections"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"?? Direktori {output_dir} berhasil dibuat")

sent_images_file = os.path.join(output_dir, "sent_images.json")

# =============================================
# KONFIGURASI LAMPU LALU LINTAS
# =============================================

dur_red = 30
dur_yellow = 3
dur_green = 7
cycle_time = dur_red + dur_yellow + dur_green + dur_yellow

# =============================================
# KONFIGURASI DATABASE
# =============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'trafficuser',
    'password': 'password123',
    'database': 'traffic_violation_db'
}

# =============================================
# KONFIGURASI LAPTOP UNTUK TRANSFER
# =============================================

LAPTOP_CONFIG = {
    'hostname': '192.168.43.118',
    'username': 'surya',
    'password': 'Nugraha123',
    'port': 22,
    'remote_path': 'D:/PA/Koding/traffic_violation_detection/detections',
    'timeout': 30,
    'banner_timeout': 30,
    'auth_timeout': 30,
    'keepalive_interval': 30
}

# Bisa gunakan SSH key:
# LAPTOP_CONFIG['key_filename'] = '/home/surya/.ssh/id_rsa'
# dan hapus 'password' dari config
