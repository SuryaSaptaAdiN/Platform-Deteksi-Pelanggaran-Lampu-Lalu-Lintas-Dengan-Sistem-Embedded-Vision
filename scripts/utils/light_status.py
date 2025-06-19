# =============================================
# FUNGSI STATUS LAMPU LOOPING
# =============================================

from config.settings import dur_red, dur_yellow, dur_green, cycle_time
import time

def get_looping_light_status(start_cycle):
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
