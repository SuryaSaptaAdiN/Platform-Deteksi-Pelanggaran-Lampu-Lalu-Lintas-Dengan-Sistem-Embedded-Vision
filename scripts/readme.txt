# Platform Deteksi Pelanggaran Lampu Lalu Lintas dengan Embedded Vision

## Deskripsi
Program ini menggunakan kamera untuk mendeteksi kendaraan yang melanggar lampu merah berdasarkan posisi kendaraan terhadap garis marka jalan. Deteksi menggunakan model YOLOv11 yang telah dilatih, dengan fitur monitoring sistem, penyimpanan data pelanggaran ke database MySQL, dan pengiriman hasil (gambar + metadata) ke server laptop via SSH/SFTP.

## Struktur Folder
- main.py              : File utama untuk menjalankan program
- config/
    - settings.py      : Konfigurasi variabel global, jalur model, dan database
- utils/
    - light_status.py  : Fungsi menentukan status lampu lalu lintas berdasarkan waktu
    - road_marking.py  : Fungsi deteksi garis marka jalan dengan smoothing
    - save_db.py       : Fungsi penyimpanan data pelanggaran ke database
    - system_monitor.py: Kelas monitoring CPU, RAM, GPU, suhu, dan power
- transfer/
    - file_transfer.py : Kelas pengelola antrian dan pengiriman file ke server
- models/
    - yolov11n1.pt     : Model YOLOv11 yang digunakan untuk deteksi objek
- detections/          : Folder penyimpanan hasil tangkapan pelanggaran

## Cara Menjalankan
1. Pastikan Python 3.8+ dan semua dependensi sudah terinstall (opencv-python, ultralytics, mysql-connector-python, paramiko, psutil, numpy, GPUtil)
2. Pastikan database MySQL sudah dikonfigurasi sesuai di `config/settings.py`
3. Jalankan program utama:
    ```
    python3 main.py
    ```
4. Tekan 'q' untuk keluar dari program

## Catatan
- Koneksi SSH diatur di `config/settings.py`
- Folder hasil tangkapan otomatis dibuat di lokasi yang ditentukan
- Sistem monitoring berjalan paralel untuk memantau performa hardware

## Pengembangan Selanjutnya
- Penambahan UI untuk monitoring hasil secara real-time
- Optimasi performa model dan deteksi multi-kamera
- Integrasi notifikasi pelanggaran otomatis via email atau SMS

---

Semoga membantu! Kalau ada yang ingin diperbaiki atau ditambahkan, beri tahu ya.
