import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_fastboot_path, run_cmd


class FastbootScanner:
    def __init__(self, serial=None):
        self.fastboot = get_fastboot_path()
        self.serial = serial
        self.base_cmd = [self.fastboot]
        if serial:
            self.base_cmd += ["-s", serial]

    def scan(self):
        output = run_cmd(self.base_cmd + ["getvar", "all"], timeout=6, capture_stderr=True)
        if not output:
            output = run_cmd(self.base_cmd + ["getvar", "product"], timeout=3, capture_stderr=True)

        vars_dict = {}
        if output:
            for line in output.splitlines():
                line = line.strip()
                cleaned = re.sub(r"^\(bootloader\)\s*", "", line)
                if ":" in cleaned:
                    k, v = cleaned.split(":", 1)
                    vars_dict[k.strip().lower()] = v.strip()

        product = vars_dict.get("product", "Unknown")
        bootloader_ver = vars_dict.get("version-bootloader", "Unknown")
        baseband_ver = vars_dict.get("version-baseband", "Unknown")
        unlocked = vars_dict.get("unlocked", "Unknown")
        secure = vars_dict.get("secure", "Unknown")
        battery_voltage = vars_dict.get("battery-voltage", "Unknown")

        diag_notes = []
        status_flag = "OK"

        if battery_voltage != "Unknown":
            # Handle both "3850mV", "3850", or "3.85V"
            try:
                if "." in battery_voltage:
                    volts = float(re.findall(r"\d+\.\d+", battery_voltage)[0])
                    mv = int(volts * 1000)
                else:
                    mv = int(re.findall(r"\d+", battery_voltage)[0])

                if mv < 3500:
                    status_flag = "WARNING"
                    diag_notes.append(f"Tegangan baterai rendah ({mv} mV)! Cas terlebih dahulu sebelum flashing.")
                else:
                    diag_notes.append(f"Tegangan baterai aman ({mv} mV).")
            except (IndexError, ValueError):
                pass

        if unlocked.lower() in ["yes", "true"]:
            diag_notes.append("Bootloader Terbuka (Unlocked) — Siap flash custom firmware/recovery.")
        elif unlocked.lower() in ["no", "false"]:
            diag_notes.append("Bootloader Terkunci (Locked) — Perlu unlock auth resmi untuk flash partisi selain stock.")

        return {
            "mode": "FASTBOOT (Bootloader)",
            "product": product,
            "bootloader_version": bootloader_ver,
            "baseband_version": baseband_ver,
            "unlocked": unlocked,
            "secure": secure,
            "battery_voltage": battery_voltage,
            "status_flag": status_flag,
            "notes": diag_notes,
            "raw_vars": vars_dict
        }
