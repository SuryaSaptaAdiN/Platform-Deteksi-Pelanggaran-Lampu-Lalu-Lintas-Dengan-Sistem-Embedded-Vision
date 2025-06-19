# =============================================
# FUNGSI SIMPAN DATA KE DATABASE
# =============================================

import os
import mysql.connector
from config.settings import DB_CONFIG

# Koneksi database global
try:
    db = mysql.connector.connect(**DB_CONFIG)
    print("? Koneksi database berhasil (utils/save_db.py)")
except mysql.connector.Error as e:
    print(f"? Gagal koneksi database: {e}")
    db = None

def save_to_database(label, timestamp, image_path, fps, metadata, file_transfer):
    """Simpan data pelanggaran ke database dan kirim ke laptop"""

    if db is None:
        print("?? Tidak ada koneksi database aktif")
        return

    try:
        cursor = db.cursor()
        image_name = os.path.basename(image_path)

        # Cek apakah gambar sudah ada
        query_check = "SELECT COUNT(*) FROM violations WHERE image_path = %s"
        cursor.execute(query_check, (image_name,))
        result = cursor.fetchone()

        if result[0] == 0:
            # Simpan ke database
            query_insert = "INSERT INTO violations (label, timestamp, image_path) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (label, timestamp, image_name))
            db.commit()
            print(f"? Data tersimpan: {label}, {timestamp}, {image_name} | FPS: {fps:.2f}")

            # Kirim file ke laptop
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
            print(f"?? Duplikasi: {image_name} sudah ada di database")

        cursor.close()

    except mysql.connector.Error as e:
        print(f"? Error saat menyimpan ke database: {e}")
