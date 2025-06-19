import cv2
import time
import os
import numpy as np
import mysql.connector
from datetime import datetime
from ultralytics import YOLO
import paramiko
import threading
from queue import Queue
import json
import hashlib
import psutil
import GPUtil
from collections import defaultdict, deque

# =============================================
# KELAS SYSTEM MONITOR (TAMBAHAN BARU)
# =============================================
class SystemMonitor:
    def __init__(self):
        self.stats = {
            'RED': defaultdict(list),
            'YELLOW': defaultdict(list), 
            'GREEN': defaultdict(list),
            'OVERALL': defaultdict(list)
        }
        self.start_time = time.time()
        self.last_update = time.time()
        
        # Untuk tracking real-time
        self.current_stats = {
            'cpu_percent': 0,
            'ram_percent': 0,
            'ram_mb': 0,
            'gpu_percent': 0,
            'gpu_memory': 0,
            'temperature': 0,
            'power_watts': 0
        }
        
        # Deque untuk smoothing data
        self.cpu_history = deque(maxlen=10)
        self.ram_history = deque(maxlen=10)
        self.temp_history = deque(maxlen=10)
        
        print("📊 System Monitor initialized")
    
    def get_cpu_temperature(self):
        """Dapatkan suhu CPU (khusus untuk Raspberry Pi)"""
        try:
            # Untuk Raspberry Pi
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except:
            try:
                # Untuk sistem lain
                temps = psutil.sensors_temperatures()
                if 'cpu_thermal' in temps:
                    return temps['cpu_thermal'][0].current
                elif 'coretemp' in temps:
                    return temps['coretemp'][0].current
                else:
                    return 0
            except:
                return 0
    
    def estimate_power_consumption(self, cpu_percent, gpu_percent=0):
        """Estimasi konsumsi daya berdasarkan penggunaan CPU/GPU"""
        # Estimasi untuk Raspberry Pi 4 (dalam Watts)
        base_power = 2.5  # Idle power
        cpu_power = (cpu_percent / 100) * 3.0  # Max CPU power ~3W
        gpu_power = (gpu_percent / 100) * 1.5  # Max GPU power ~1.5W
        
        return base_power + cpu_power + gpu_power
    
    def update_stats(self, light_status, fps):
        """Update statistik sistem"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_history.append(cpu_percent)
            
            # RAM Usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_mb = ram.used / (1024 * 1024)
            self.ram_history.append(ram_percent)
            
            # GPU Usage (jika tersedia)
            gpu_percent = 0
            gpu_memory = 0
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_percent = gpu.load * 100
                    gpu_memory = gpu.memoryUsed
            except:
                pass
            
            # Temperature
            temperature = self.get_cpu_temperature()
            self.temp_history.append(temperature)
            
            # Power Consumption
            power_watts = self.estimate_power_consumption(cpu_percent, gpu_percent)
            
            # Update current stats (smoothed)
            self.current_stats = {
                'cpu_percent': np.mean(self.cpu_history) if self.cpu_history else cpu_percent,
                'ram_percent': np.mean(self.ram_history) if self.ram_history else ram_percent,
                'ram_mb': ram_mb,
                'gpu_percent': gpu_percent,
                'gpu_memory': gpu_memory,
                'temperature': np.mean(self.temp_history) if self.temp_history else temperature,
                'power_watts': power_watts
            }
            
            # Simpan ke statistik per status lampu
            self.stats[light_status]['fps'].append(fps)
            self.stats[light_status]['cpu'].append(cpu_percent)
            self.stats[light_status]['ram'].append(ram_percent)
            self.stats[light_status]['gpu'].append(gpu_percent)
            self.stats[light_status]['temperature'].append(temperature)
            self.stats[light_status]['power'].append(power_watts)
            
            # Simpan ke statistik keseluruhan
            self.stats['OVERALL']['fps'].append(fps)
            self.stats['OVERALL']['cpu'].append(cpu_percent)
            self.stats['OVERALL']['ram'].append(ram_percent)
            self.stats['OVERALL']['gpu'].append(gpu_percent)
            self.stats['OVERALL']['temperature'].append(temperature)
            self.stats['OVERALL']['power'].append(power_watts)
            
        except Exception as e:
            print(f"⚠️ Error updating system stats: {e}")
    
    def get_current_stats(self):
        """Dapatkan statistik saat ini"""
        return self.current_stats
    
    def print_final_report(self):
        """Cetak laporan akhir dengan rata-rata"""
        print("\n" + "="*80)
        print("📈 LAPORAN AKHIR SISTEM MONITORING")
        print("="*80)
        
        runtime = time.time() - self.start_time
        print(f"⏱️  Total Runtime: {runtime/60:.2f} menit ({runtime:.2f} detik)")
        
        for status in ['RED', 'YELLOW', 'GREEN', 'OVERALL']:
            data = self.stats[status]
            if not data.get('fps'):
                continue
                
            print(f"\n🚦 Status: {status}")
            print("-" * 40)
            
            # Hitung rata-rata
            avg_fps = np.mean(data['fps'])
            avg_cpu = np.mean(data['cpu'])
            avg_ram = np.mean(data['ram'])
            avg_gpu = np.mean(data['gpu']) if data['gpu'] else 0
            avg_temp = np.mean(data['temperature'])
            avg_power = np.mean(data['power'])
            
            # Hitung min/max
            min_fps, max_fps = np.min(data['fps']), np.max(data['fps'])
            min_cpu, max_cpu = np.min(data['cpu']), np.max(data['cpu'])
            min_temp, max_temp = np.min(data['temperature']), np.max(data['temperature'])
            
            print(f"   FPS      : {avg_fps:.2f} (min: {min_fps:.2f}, max: {max_fps:.2f})")
            print(f"   CPU      : {avg_cpu:.1f}% (min: {min_cpu:.1f}%, max: {max_cpu:.1f}%)")
            print(f"   RAM      : {avg_ram:.1f}%")
            print(f"   GPU      : {avg_gpu:.1f}%")
            print(f"   Temp     : {avg_temp:.1f}°C (min: {min_temp:.1f}°C, max: {max_temp:.1f}°C)")
            print(f"   Power    : {avg_power:.2f}W")
            print(f"   Samples  : {len(data['fps'])}")
        
        print("\n" + "="*80)

# =============================================
# KONFIGURASI DATABASE
# =============================================
try:
    db = mysql.connector.connect(
        host="localhost",
        user="trafficuser",
        password="password123",
        database="traffic_violation_db"
    )
    print("✅ Koneksi database berhasil")
except mysql.connector.Error as e:
    print(f"❌ Error koneksi database: {e}")
    exit()

# =============================================
# KONFIGURASI TRANSFER FILE (SSH/SFTP)
# =============================================
LAPTOP_CONFIG = {
    'hostname': '192.168.43.118',  # IP address laptop PC Anda
    'username': 'surya',   # Username laptop PC
    'password': 'Nugraha123',   # atau gunakan key_filename untuk SSH key
    'port': 22,
    'remote_path': 'D:/PA/Koding/traffic_violation_detection/detections',  # Path folder detections di laptop
    'timeout': 30,
    'banner_timeout': 30,
    'auth_timeout': 30,
    'keepalive_interval': 30
}

# Alternative: gunakan SSH key (lebih aman)
# LAPTOP_CONFIG['key_filename'] = '/home/surya/.ssh/id_rsa'
# dan hapus 'password' dari config

# =============================================
# KONFIGURASI DIREKTORI
# =============================================
output_dir = "/home/surya/Desktop/PA/detections"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"📁 Direktori {output_dir} berhasil dibuat")

# File untuk tracking gambar yang sudah dikirim
sent_images_file = os.path.join(output_dir, "sent_images.json")

# =============================================
# KELAS TRANSFER MANAGER
# =============================================
class FileTransferManager:
    def __init__(self, config):
        self.config = config
        self.transfer_queue = Queue()
        self.sent_images = self.load_sent_images()
        self.ssh_client = None
        self.sftp_client = None
        
        # Start transfer thread
        self.transfer_thread = threading.Thread(target=self._transfer_worker, daemon=True)
        self.transfer_thread.start()
        print("🚀 File Transfer Manager dimulai")
    
    def load_sent_images(self):
        """Load daftar gambar yang sudah dikirim"""
        try:
            if os.path.exists(sent_images_file):
                with open(sent_images_file, 'r') as f:
                    return set(json.load(f))
            return set()
        except:
            return set()
    
    def save_sent_images(self):
        """Simpan daftar gambar yang sudah dikirim"""
        try:
            with open(sent_images_file, 'w') as f:
                json.dump(list(self.sent_images), f)
        except Exception as e:
            print(f"⚠️ Error saving sent images list: {e}")
    
    def get_file_hash(self, filepath):
        """Generate hash untuk file (untuk deteksi duplikasi)"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def connect_ssh(self):
        """Buat koneksi SSH/SFTP"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect dengan password atau key
            if 'key_filename' in self.config:
                self.ssh_client.connect(
                    hostname=self.config['hostname'],
                    username=self.config['username'],
                    key_filename=self.config['key_filename'],
                    port=self.config['port'],
                    timeout=self.config['timeout']
                )
            else:
                self.ssh_client.connect(
                    hostname=self.config['hostname'],
                    username=self.config['username'],
                    password=self.config['password'],
                    port=self.config['port'],
                    timeout=self.config['timeout']
                )
            
            self.sftp_client = self.ssh_client.open_sftp()
            return True
            
        except Exception as e:
            print(f"❌ Error koneksi SSH: {e}")
            return False
    
    def disconnect_ssh(self):
        """Tutup koneksi SSH/SFTP"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
        except:
            pass
    
    def add_to_queue(self, image_path, metadata=None):
        """Tambahkan file ke queue transfer"""
        if os.path.exists(image_path):
            file_hash = self.get_file_hash(image_path)
            filename = os.path.basename(image_path)
            
            # Cek apakah file sudah pernah dikirim (berdasarkan hash)
            if file_hash and file_hash not in self.sent_images:
                transfer_data = {
                    'local_path': image_path,
                    'filename': filename,
                    'file_hash': file_hash,
                    'metadata': metadata or {},
                    'timestamp': datetime.now().isoformat()
                }
                self.transfer_queue.put(transfer_data)
                print(f"📤 File ditambahkan ke queue: {filename}")
            else:
                print(f"⚠️ File sudah pernah dikirim: {filename}")
    
    def _transfer_worker(self):
        """Worker thread untuk transfer file"""
        while True:
            try:
                # Ambil dari queue (blocking)
                transfer_data = self.transfer_queue.get(timeout=1)
                
                # Lakukan transfer
                success = self._transfer_file(transfer_data)
                
                if success:
                    # Tandai sebagai sudah dikirim
                    self.sent_images.add(transfer_data['file_hash'])
                    self.save_sent_images()
                    print(f"✅ Transfer berhasil: {transfer_data['filename']}")
                else:
                    print(f"❌ Transfer gagal: {transfer_data['filename']}")
                
                # Tandai task selesai
                self.transfer_queue.task_done()
                
            except:
                # Queue kosong, tunggu sebentar
                time.sleep(0.1)
    
    def _transfer_file(self, transfer_data):
        """Transfer file ke laptop"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Buat koneksi jika belum ada
                if not self.ssh_client or not self.ssh_client.get_transport().is_active():
                    if not self.connect_ssh():
                        continue
                
                # Transfer file
                local_path = transfer_data['local_path']
                remote_path = os.path.join(self.config['remote_path'], transfer_data['filename'])
                
                # Buat direktori remote jika belum ada
                try:
                    remote_dir = os.path.dirname(remote_path)
                    self.ssh_client.exec_command(f'mkdir -p {remote_dir}')
                except:
                    pass
                
                # Upload file
                self.sftp_client.put(local_path, remote_path)
                
                # Juga kirim metadata sebagai file JSON (opsional)
                if transfer_data['metadata']:
                    metadata_path = remote_path.replace('.jpg', '_metadata.json')
                    metadata_content = json.dumps(transfer_data['metadata'], indent=2)
                    
                    # Buat temporary file untuk metadata
                    temp_metadata_path = local_path.replace('.jpg', '_temp_metadata.json')
                    with open(temp_metadata_path, 'w') as f:
                        f.write(metadata_content)
                    
                    self.sftp_client.put(temp_metadata_path, metadata_path)
                    os.remove(temp_metadata_path)  # Hapus file temp
                
                return True
                
            except Exception as e:
                print(f"❌ Transfer attempt {attempt + 1} failed: {e}")
                self.disconnect_ssh()
                time.sleep(2)  # Wait before retry
        
        return False

# =============================================
# VARIABEL GLOBAL
# =============================================
# Load model YOLO
model = YOLO("/home/surya/Desktop/PA/models/yolov11n1.pt")
print("🤖 Model YOLO berhasil dimuat")

# Initialize File Transfer Manager
file_transfer = FileTransferManager(LAPTOP_CONFIG)

# Initialize System Monitor (TAMBAHAN BARU)
system_monitor = SystemMonitor()

# Kamera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Kamera gagal dibuka.")
    exit()

# Set awal timing
start_cycle = time.time()

# Anti-duplikasi dan caching
saved_images = set()
marka_y_history = []
cached_marka_y = None
last_marka_time = 0

# Konfigurasi durasi tiap warna (detik)
dur_red = 30
dur_yellow = 3
dur_green = 7
cycle_time = dur_red + dur_yellow + dur_green + dur_yellow  # Total 43 detik

print(f"🚦 Siklus lampu: Merah({dur_red}s) → Kuning({dur_yellow}s) → Hijau({dur_green}s) → Kuning({dur_yellow}s)")

# =============================================
# FUNGSI CALLBACK DATABASE
# =============================================
def save_to_database(label, timestamp, image_path, fps, metadata=None):
    """Fungsi callback untuk menyimpan data ke database dengan anti-duplikasi"""
    try:
        cursor = db.cursor()
        
        # Ambil hanya nama file (tanpa path)
        image_name = os.path.basename(image_path)
        
        # Cek apakah gambar sudah ada di database
        query_check = "SELECT COUNT(*) FROM violations WHERE image_path = %s"
        cursor.execute(query_check, (image_name,))
        result = cursor.fetchone()
        
        if result[0] == 0:  # Jika belum ada, simpan ke database
            query_insert = "INSERT INTO violations (label, timestamp, image_path) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (label, timestamp, image_name))
            db.commit()
            print(f"✅ Data tersimpan: {label}, {timestamp}, {image_name} | FPS: {fps:.2f}")
            
            # KIRIM FILE KE LAPTOP SECARA OTOMATIS
            transfer_metadata = {
                'label': label,
                'timestamp': timestamp,
                'fps': fps,
                'violation_type': 'red_light_violation',
                'location': 'Traffic Light Camera 1'
            }
            if metadata:
                transfer_metadata.update(metadata)
            
            file_transfer.add_to_queue(image_path, transfer_metadata)
            
        else:
            print(f"⚠️ Duplikasi terdeteksi, tidak menyimpan ulang: {image_name}")
        
        cursor.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Error database: {e}")

# =============================================
# FUNGSI STATUS LAMPU LOOPING
# =============================================
def get_looping_light_status():
    """Menentukan status lampu berdasarkan waktu looping"""
    elapsed = int(time.time() - start_cycle) % cycle_time
    
    if elapsed < dur_red:
        return "RED"
    elif elapsed < dur_red + dur_yellow:
        return "YELLOW"
    elif elapsed < dur_red + dur_yellow + dur_green:
        return "GREEN"
    else:
        return "YELLOW"

# =============================================
# FUNGSI DETEKSI GARIS MARKA
# =============================================
def detect_road_marking(frame):
    """Deteksi garis marka jalan dengan caching dan smoothing"""
    global cached_marka_y, last_marka_time, marka_y_history
    
    # 1️⃣ Ambil setengah bawah frame sebagai ROI
    roi = frame[frame.shape[0] // 2 :, :]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # 2️⃣ Deteksi warna putih
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([255, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    edges = cv2.Canny(mask, 50, 150)
    
    # 3️⃣ Deteksi garis putih horizontal dengan HoughLinesP
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=180, maxLineGap=20)
    marka_y = None
    
    if lines is not None:
        min_y = float("inf")
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Filter garis horizontal yang panjang
            if 0 < abs(angle) < 10 and length > frame.shape[1] // 3:
                if y1 < min_y:
                    min_y = y1
                    marka_y = y1 + frame.shape[0] // 2  # Sesuaikan dengan ROI
        
        # 4️⃣ Simpan ke history untuk smoothing
        if marka_y is not None:
            marka_y_history.append(marka_y)
            if len(marka_y_history) > 5:
                marka_y_history.pop(0)
            cached_marka_y = int(np.mean(marka_y_history))
            last_marka_time = time.time()
    
    # 5️⃣ Jika tidak terdeteksi, gunakan cache selama ≤ 1.5 detik
    if marka_y is None and cached_marka_y and (time.time() - last_marka_time < 1.5):
        marka_y = cached_marka_y
    
    return marka_y

# =============================================
# MAIN LOOP
# =============================================
print("🚀 Sistem deteksi pelanggaran dimulai...")
print("📋 Tekan 'q' untuk keluar")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame kosong. Cek koneksi kamera.")
        break
    
    start_time = time.time()
    
    # 1️⃣ Dapatkan status lampu
    status = get_looping_light_status()
    
    # 2️⃣ Deteksi garis marka
    marka_y = detect_road_marking(frame)
    
    # 3️⃣ Gambar garis marka jika ada
    if marka_y:
        cv2.line(frame, (0, marka_y), (frame.shape[1], marka_y), (0, 255, 0), 2)
    
    # 4️⃣ Deteksi kendaraan saat lampu merah
    if status == "RED":
        print("🚦 Lampu merah, deteksi kendaraan...")
        
        # Prediksi dengan model YOLO
        results = model.predict(source=frame, conf=0.6, imgsz=320, verbose=False)
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls)
                label = model.names[cls_id]
                confidence = float(box.conf[0]) * 100
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                mid_y = (y1 + y2) // 2
                
                # 5️⃣ Cek apakah tengah bounding box melewati garis marka
                if marka_y and mid_y > marka_y:
                    print(f"🚨 Pelanggaran: {label} melewati marka!")
                    
                    # Gambar bounding box merah untuk pelanggaran
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{label} {confidence:.1f}%", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    # 6️⃣ Simpan gambar dan data pelanggaran
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    image_path = os.path.join(output_dir, filename)
                    
                    # Hitung FPS untuk callback
                    fps = 1.0 / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
                    
                    # Anti-duplikasi check
                    if image_path not in saved_images:
                        # Simpan gambar
                        cv2.imwrite(image_path, frame)
                        
                        # Metadata tambahan untuk transfer
                        additional_metadata = {
                            'confidence': confidence,
                            'bounding_box': [x1, y1, x2, y2],
                            'vehicle_position': mid_y,
                            'road_marking_position': marka_y
                        }
                        
                        # Simpan ke database dan kirim ke laptop
                        save_to_database(label, timestamp, image_path, fps, additional_metadata)
                        
                        # Tambah ke set anti-duplikasi
                        saved_images.add(image_path)
                    else:
                        print(f"⚠️ Gambar sudah tersimpan sebelumnya: {filename}")
    
    # 7️⃣ Hitung dan update sistem monitoring (TAMBAHAN BARU)
    fps = 1.0 / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
    system_monitor.update_stats(status, fps)
    current_stats = system_monitor.get_current_stats()
    
    # 8️⃣ Display info di frame (DIPERLUAS DENGAN MONITORING)
    y_pos = 30
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    y_pos += 30
    cv2.putText(frame, f"Lampu: {status}", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    y_pos += 30
    cv2.putText(frame, f"CPU: {current_stats['cpu_percent']:.1f}%", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    cv2.putText(frame, f"RAM: {current_stats['ram_percent']:.1f}%", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    cv2.putText(frame, f"GPU: {current_stats['gpu_percent']:.1f}%", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    cv2.putText(frame, f"Temp: {current_stats['temperature']:.1f}C", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    cv2.putText(frame, f"Power: {current_stats['power_watts']:.1f}W", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    # Tampilkan status transfer
    queue_size = file_transfer.transfer_queue.qsize()
    y_pos += 30
    cv2.putText(frame, f"Queue: {queue_size}", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Tampilkan waktu siklus
    elapsed = int(time.time() - start_cycle) % cycle_time
    y_pos += 30
    cv2.putText(frame, f"Siklus: {elapsed}s", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # 9️⃣ Tampilkan hasil
    cv2.imshow("Sistem Deteksi Pelanggaran - Raspberry Pi", frame)
    
    # Print status ke terminal setiap 30 frame (untuk tidak spam)
    if int(time.time() * 2) % 30 == 0:  # Setiap ~15 detik
        print(f"🔄 Status: {status} | FPS: {fps:.2f} | Marka: {'✓' if marka_y else '✗'} | Queue: {queue_size}")
        print(f"📊 CPU: {current_stats['cpu_percent']:.1f}% | RAM: {current_stats['ram_percent']:.1f}% | Temp: {current_stats['temperature']:.1f}°C | Power: {current_stats['power_watts']:.1f}W")
    
    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Sistem dihentikan oleh user")
        break

# =============================================
# CLEANUP DAN LAPORAN AKHIR
# =============================================
print("🧹 Membersihkan resource...")

# Tunggu transfer queue kosong
print("⏳ Menunggu transfer selesai...")
file_transfer.transfer_queue.join()
file_transfer.disconnect_ssh()

cap.release()
cv2.destroyAllWindows()

# CETAK LAPORAN AKHIR SISTEM MONITORING (TAMBAHAN BARU)
system_monitor.print_final_report()

# Tutup koneksi database
try:
    db.close()
    print("✅ Koneksi database ditutup")
except:
    print("⚠️ Error saat menutup database")

print("👋 Program selesai")
