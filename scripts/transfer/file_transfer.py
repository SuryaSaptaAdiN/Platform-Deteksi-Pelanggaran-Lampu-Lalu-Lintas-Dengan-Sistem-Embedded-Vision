# ========================================================
# 📂 PENGIRIMAN FILE HASIL PELANGGARAN KE SERVER/LAPTOP
# ========================================================

import os
import threading
import time
import queue
import paramiko
from scp import SCPClient

class FileTransferManager:
    def __init__(self, config):
        self.queue_lock = threading.Lock()
        self.transfer_queue = queue.Queue()
        self.ssh_client = self.connect_ssh(config)
        self.config = config

        self.transfer_thread = threading.Thread(target=self.process_queue)
        self.transfer_thread.daemon = True
        self.transfer_thread.start()

    def connect_ssh(self, config):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(config['host'], port=config['port'], username=config['username'], password=config['password'])
            print(f"🔌 Terhubung SSH ke {config['host']}")
            return ssh
        except Exception as e:
            print(f"❌ Gagal terhubung SSH: {e}")
            return None

    def transfer_file(self, local_path, remote_path=None):
        if not self.ssh_client:
            print("⚠️ Tidak ada koneksi SSH.")
            return

        if remote_path is None:
            remote_path = os.path.join(self.config['remote_dir'], os.path.basename(local_path))

        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(local_path, remote_path)
                print(f"✅ File terkirim ke server: {remote_path}")
        except Exception as e:
            print(f"⚠️ Gagal mengirim file: {e}")

    def add_to_queue(self, local_path):
        self.transfer_queue.put(local_path)
        print(f"📥 Ditambahkan ke antrian transfer: {local_path}")

    def process_queue(self):
        while True:
            try:
                file_path = self.transfer_queue.get()
                if file_path:
                    self.transfer_file(file_path)
                self.transfer_queue.task_done()
            except Exception as e:
                print(f"⚠️ Error saat memproses antrian: {e}")
            time.sleep(1)

    def disconnect_ssh(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("🔌 Koneksi SSH ditutup")
