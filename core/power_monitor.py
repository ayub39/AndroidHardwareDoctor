import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, run_cmd


class PowerMonitor:
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]

    def _shell(self, cmd_str, timeout=6):
        return run_cmd(self.base_cmd + ["shell", cmd_str], timeout=timeout)

    def read_live_power(self) -> dict:
        """Reads real-time mA, voltage, temperature, and charging speed evaluation."""
        info = {
            "current_ma": 0,
            "raw_current": 0,
            "voltage_v": 0.0,
            "voltage_mv": 0,
            "temperature_c": 0.0,
            "level": 0,
            "status": "Unknown",
            "is_charging": False,
            "charge_speed": "Tidak Terdeteksi"
        }

        current_raw = self._shell(
            "cat /sys/class/power_supply/battery/current_now 2>/dev/null || "
            "cat /sys/class/power_supply/bms/current_now 2>/dev/null || "
            "cat /sys/class/power_supply/usb/current_now 2>/dev/null"
        )
        battery_dump = self._shell("dumpsys battery")

        current_ma = 0
        if current_raw and current_raw.strip().lstrip("-").isdigit():
            try:
                raw_val = int(current_raw.strip())
                if abs(raw_val) > 50000:
                    current_ma = raw_val // 1000  # uA -> mA
                else:
                    current_ma = raw_val
            except (ValueError, TypeError):
                current_ma = 0

        voltage_mv = 0
        temp_raw = 0
        level = 0
        status_code = "3"

        if battery_dump:
            for line in battery_dump.splitlines():
                line = line.strip()
                if ":" not in line:
                    continue
                try:
                    k, v = [x.strip() for x in line.split(":", 1)]
                    k_lower = k.lower()
                    if k_lower == "level":
                        level = int(v) if v.isdigit() else 0
                    elif k_lower == "voltage":
                        voltage_mv = int(v) if v.isdigit() else 0
                    elif k_lower == "temperature":
                        temp_raw = int(v) if v.isdigit() else 0
                    elif k_lower == "status":
                        status_code = v
                except (ValueError, TypeError):
                    continue

        status_map = {
            "1": "Unknown",
            "2": "Charging (Mengisi Daya)",
            "3": "Discharging (Tidak Di-charge)",
            "4": "Not Charging (Dicolok, Tidak Masuk)",
            "5": "Full (Penuh)"
        }
        status_str = status_map.get(status_code, status_code)
        is_charging = (status_code == "2")
        temp_c = round(temp_raw / 10.0, 1) if temp_raw else 0.0
        voltage_v = round(voltage_mv / 1000.0, 2) if voltage_mv else 0.0
        abs_ma = abs(current_ma)

        charge_speed = "Normal"
        if is_charging:
            if abs_ma >= 1800:
                charge_speed = "⚡ Fast / Quick Charging (>1.8A)"
            elif abs_ma >= 800:
                charge_speed = "✅ Standard Charging (0.8A–1.8A)"
            elif abs_ma > 50:
                charge_speed = "⚠️ Slow Charging (<0.8A) — Indikasi Port/Kabel Drop"
            else:
                charge_speed = "🛑 Arus Masuk 0mA / Sangat Lemah"
        else:
            charge_speed = f"Konsumsi Daya HP ({abs_ma} mA)"

        info.update({
            "current_ma": abs_ma,
            "raw_current": current_ma,
            "voltage_v": voltage_v,
            "voltage_mv": voltage_mv,
            "temperature_c": temp_c,
            "level": level,
            "status": status_str,
            "is_charging": is_charging,
            "charge_speed": charge_speed
        })
        return info
