# =============================================
# MONITORING SISTEM CPU, RAM, GPU, SUHU, POWER
# =============================================

import time
import numpy as np
import psutil
from collections import defaultdict, deque
import GPUtil

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

        self.current_stats = {
            'cpu_percent': 0,
            'ram_percent': 0,
            'ram_mb': 0,
            'gpu_percent': 0,
            'gpu_memory': 0,
            'temperature': 0,
            'power_watts': 0
        }

        self.cpu_history = deque(maxlen=10)
        self.ram_history = deque(maxlen=10)
        self.temp_history = deque(maxlen=10)

        print("📊 System Monitor initialized")

    def get_cpu_temperature(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except:
            try:
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
        base_power = 2.5
        cpu_power = (cpu_percent / 100) * 3.0
        gpu_power = (gpu_percent / 100) * 1.5
        return base_power + cpu_power + gpu_power

    def update_stats(self, light_status, fps):
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_history.append(cpu_percent)

            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_mb = ram.used / (1024 * 1024)
            self.ram_history.append(ram_percent)

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

            temperature = self.get_cpu_temperature()
            self.temp_history.append(temperature)

            power_watts = self.estimate_power_consumption(cpu_percent, gpu_percent)

            self.current_stats = {
                'cpu_percent': np.mean(self.cpu_history),
                'ram_percent': np.mean(self.ram_history),
                'ram_mb': ram_mb,
                'gpu_percent': gpu_percent,
                'gpu_memory': gpu_memory,
                'temperature': np.mean(self.temp_history),
                'power_watts': power_watts
            }

            for key in ['fps', 'cpu', 'ram', 'gpu', 'temperature', 'power']:
                self.stats[light_status][key].append(self.current_stats[key if key != 'cpu' else 'cpu_percent'])
                self.stats['OVERALL'][key].append(self.current_stats[key if key != 'cpu' else 'cpu_percent'])

        except Exception as e:
            print(f"⚠️ Error updating system stats: {e}")

    def get_current_stats(self):
        return self.current_stats

    def print_final_report(self):
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
            avg_fps = np.mean(data['fps'])
            avg_cpu = np.mean(data['cpu'])
            avg_ram = np.mean(data['ram'])
            avg_gpu = np.mean(data['gpu']) if data['gpu'] else 0
            avg_temp = np.mean(data['temperature'])
            avg_power = np.mean(data['power'])

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
