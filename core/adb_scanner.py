import os
import sys
import re
import time

# Ensure root folder is accessible for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, run_cmd

class AdbHardwareScanner:
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]

    def shell(self, cmd_str, timeout=8):
        cmd = self.base_cmd + ["shell", cmd_str]
        return run_cmd(cmd, timeout=timeout)

    def root_shell(self, cmd_str, timeout=5):
        """Attempts running command via su if device is rooted, falls back to non-root shell."""
        try:
            res = self.shell(f"su -c '{cmd_str}' 2>/dev/null", timeout=timeout)
            if res and not any(err in res.lower() for err in ["not found", "permission denied", "inaccessible"]):
                return res
        except Exception:
            pass
        return self.shell(cmd_str, timeout=timeout)

    def scan_all(self):
        """Performs full automated diagnostic and returns structured report."""
        report = {
            "device_info": self.get_device_info(),
            "battery": self.scan_battery(),
            "storage": self.scan_storage(),
            "display": self.scan_display(),
            "touchscreen": self.scan_touchscreen(),
            "cameras": self.scan_cameras(),
            "sensors": self.scan_sensors(),
            "connectivity": self.scan_connectivity(),
            "hardware_faults": self.scan_kernel_hardware_faults()
        }
        return report

    def get_device_info(self):
        brand = self.shell("getprop ro.product.brand") or "Unknown"
        model = self.shell("getprop ro.product.model") or "Unknown"
        manufacturer = self.shell("getprop ro.product.manufacturer") or "Unknown"
        board = self.shell("getprop ro.board.platform") or self.shell("getprop ro.hardware")
        android_ver = self.shell("getprop ro.build.version.release") or "Unknown"
        security_patch = self.shell("getprop ro.build.version.security_patch") or "Unknown"
        serial = self.shell("getprop ro.serialno") or self.serial
        baseband = self.shell("getprop gsm.version.baseband") or "Unknown"

        # Memory / RAM Info
        meminfo = self.shell("cat /proc/meminfo")
        total_ram_mb = 0
        free_ram_mb = 0
        if meminfo:
            for line in meminfo.splitlines():
                if "MemTotal" in line:
                    val = re.findall(r"\d+", line)
                    if val:
                        total_ram_mb = int(val[0]) // 1024
                elif "MemAvailable" in line or "MemFree" in line:
                    val = re.findall(r"\d+", line)
                    if val and free_ram_mb == 0:
                        free_ram_mb = int(val[0]) // 1024

        baseband_status = "NORMAL"
        if not baseband or baseband.lower() in ["unknown", "", "none"]:
            baseband_status = "FAULT / NULL (IC Baseband / Modem bermasalah)"

        # Extract IMEI 1 & IMEI 2 via multi-method fallback
        imeis = []
        for prop in ["ro.ril.oem.imei", "ro.ril.oem.imei1", "ro.ril.oem.imei2", 
                     "persist.radio.imei", "persist.radio.imei1", "persist.radio.imei2",
                     "ro.ril.miui.imei0", "ro.ril.miui.imei1",
                     "gsm.baseband.imei", "gsm.baseband.imei1", "gsm.baseband.imei2",
                     "ril.imei", "ril.imei1", "ril.imei2"]:
            val = self.shell(f"getprop {prop}")
            if val and val.strip().isdigit() and len(val.strip()) >= 14 and val.strip()[:15] not in imeis:
                imeis.append(val.strip()[:15])

        if not imeis:
            for sub_code in [1, 2]:
                res = self.shell(f"service call iphonesubinfo {sub_code}")
                if res and "Parcel" in res:
                    raw_ascii = re.findall(r"'([^']+)'", res)
                    if raw_ascii:
                        digits = re.sub(r"[^\d]", "", "".join(raw_ascii))
                        if len(digits) >= 14 and digits[:15] not in imeis:
                            imeis.append(digits[:15])

        if not imeis:
            dump_sub = self.shell("dumpsys iphonesubinfo")
            if dump_sub:
                found = re.findall(r"(?:Device ID|IMEI|imei)\s*=\s*(\d{14,16})", dump_sub, re.I)
                for f in found:
                    if f[:15] not in imeis:
                        imeis.append(f[:15])

        imei1 = imeis[0] if len(imeis) > 0 else "Tidak Terbaca / NULL"
        imei2 = imeis[1] if len(imeis) > 1 else ("-" if len(imeis) == 1 else "Tidak Terbaca / NULL")

        if not baseband or baseband.lower() in ["unknown", "", "none"] or (imei1 == "Tidak Terbaca / NULL" and "FAULT" in baseband_status):
            signal_diag = "🚨 RUSAK (IC Baseband / EFS NVRAM Hilang / Radio Mati)"
        elif imei1 != "Tidak Terbaca / NULL":
            signal_diag = "✅ HARDWARE BASEBAND NORMAL (IC RF & Modem Terbaca)"
        else:
            signal_diag = "⚠️ STATUS TERBATAS (Cek SIM Card / Izin Radio)"

        # Extract Logged-in Google / Gmail Accounts
        google_accounts = []
        try:
            from core.data_rescue import DataRescueManager
            rescue = DataRescueManager(serial=self.serial)
            acc_data = rescue.get_accounts()
            google_accounts = acc_data.get("google", [])
        except Exception:
            google_accounts = []

        return {
            "brand": brand.title(),
            "model": model,
            "manufacturer": manufacturer.title(),
            "chipset": board.upper() if board else "Unknown",
            "android_version": android_ver,
            "security_patch": security_patch,
            "serial": serial,
            "ram_total": f"{total_ram_mb} MB ({round(total_ram_mb/1024, 1)} GB)" if total_ram_mb else "Unknown",
            "ram_available": f"{free_ram_mb} MB" if free_ram_mb else "Unknown",
            "baseband": baseband,
            "baseband_status": baseband_status,
            "imei1": imei1,
            "imei2": imei2,
            "signal_diagnosis": signal_diag,
            "google_accounts": ", ".join(google_accounts) if google_accounts else "Tidak Terdeteksi / Belum Login",
            "google_accounts_list": google_accounts
        }

    def scan_battery(self):
        dump = self.shell("dumpsys battery")
        dump_bstats = self.shell("dumpsys batterystats") or ""

        # Check sysfs cycle nodes if accessible
        sysfs_cycles = self.shell("cat /sys/class/power_supply/battery/cycle_count 2>/dev/null") or \
                       self.shell("cat /sys/class/power_supply/battery/battery_cycle 2>/dev/null") or \
                       self.shell("cat /sys/class/power_supply/bms/cycle_count 2>/dev/null") or \
                       self.shell("cat /sys/class/power_supply/battery/fg_cycle 2>/dev/null")

        info = {
            "level": "Unknown",
            "voltage": "Unknown",
            "temperature": "Unknown",
            "health": "GOOD (Bagus)",
            "status": "Unknown",
            "charger": "None",
            "design_capacity": "Unknown",
            "current_capacity": "Unknown",
            "capacity_loss": "Unknown",
            "health_pct": "Unknown",
            "cycle_count": "Tidak Terbaca (Akses Non-Root)",
            "status_flag": "OK",
            "note": "Kondisi baterai & IC charging normal."
        }
        if not dump:
            info["status_flag"] = "UNKNOWN"
            info["note"] = "Tidak dapat membaca subsistem baterai."
            return info

        health_map = {
            "1": "UNKNOWN",
            "2": "GOOD (Bagus)",
            "3": "OVERHEAT (Kepanasan)",
            "4": "DEAD (Drop / Rusak)",
            "5": "OVER_VOLTAGE (Tegangan Terlalu Tinggi)",
            "6": "UNSPECIFIED_FAILURE (Kerusakan IC Baterai)",
            "7": "COLD (Terlalu Dingin)"
        }

        status_map = {
            "1": "UNKNOWN",
            "2": "CHARGING (Mengisi Daya)",
            "3": "DISCHARGING (Tidak Di-charge)",
            "4": "NOT_CHARGING (Dicolok tapi Tidak Mengisi)",
            "5": "FULL (Penuh)"
        }

        level_num = None
        charge_counter_uah = None
        samsung_usage = None
        samsung_asoc = None
        std_cycle = None

        for line in dump.splitlines():
            line = line.strip()
            if ":" not in line:
                continue
            k, v = [x.strip() for x in line.split(":", 1)]
            k_lower = k.lower()
            if k_lower == "level":
                try:
                    level_num = int(v)
                    info["level"] = f"{level_num}%"
                except ValueError:
                    info["level"] = f"{v}%"
            elif k_lower == "voltage":
                try:
                    mv = float(v)
                    volts = round(mv / 1000.0, 2)
                    info["voltage"] = f"{volts} V ({int(mv)} mV)"
                except (ValueError, TypeError):
                    info["voltage"] = f"{v} mV"
            elif k_lower == "temperature":
                try:
                    celsius = round(float(v) / 10.0, 1)
                    info["temperature"] = f"{celsius} °C"
                    if celsius < 0 or celsius > 52:
                        info["status_flag"] = "WARNING"
                        info["note"] = f"Suhu abnormal ({celsius}°C)! Jalur thermistor atau IC Charger bermasalah."
                except (ValueError, TypeError):
                    info["temperature"] = f"{v}"
            elif k_lower == "health":
                info["health"] = health_map.get(v, v)
                if v in ["3", "4", "5", "6"]:
                    info["status_flag"] = "ALERT"
                    info["note"] = f"Indikasi kerusakan baterai/daya: {info['health']}"
            elif k_lower == "status":
                info["status"] = status_map.get(v, v)
                if v == "4":
                    info["status_flag"] = "WARNING"
                    info["note"] = "Dicolok tapi tidak mengisi (Indikasi jalur VBUS/IC Charging drop)."
            elif k_lower in ["ac powered", "usb powered", "wireless powered"]:
                if v.lower() == "true":
                    info["charger"] = k.replace(" powered", "").upper()
            elif k_lower == "charge counter":
                try:
                    charge_counter_uah = int(v)
                except ValueError:
                    pass
            elif "msavedbatteryusage" in k_lower:
                try:
                    samsung_usage = int(v)
                except ValueError:
                    pass
            elif "msavedbatteryasoc" in k_lower:
                try:
                    samsung_asoc = int(v)
                except ValueError:
                    pass
            elif "cycle" in k_lower:
                try:
                    digits = re.sub(r'[^\d]', '', v)
                    if digits:
                        std_cycle = int(digits)
                except ValueError:
                    pass

        # Extract Design Capacity & Current Estimated Capacity from batterystats
        design_mah = None
        est_mah = None
        bstats_cycle = None

        if dump_bstats:
            m_cap = re.search(r'Capacity:\s*(\d+)', dump_bstats)
            if m_cap:
                design_mah = int(m_cap.group(1))

            m_est = re.search(r'Estimated battery capacity:\s*([\d\.]+)\s*mAh', dump_bstats, re.I)
            if m_est:
                est_mah = int(float(m_est.group(1)))
            else:
                m_learn = re.search(r'Last learned battery capacity:\s*([\d\.]+)\s*mAh', dump_bstats, re.I)
                if m_learn:
                    est_mah = int(float(m_learn.group(1)))

            m_c = re.search(r'(?:cycle\s*count|battery\s*cycle|cycle\s*counter)\s*:\s*(\d+)', dump_bstats, re.I)
            if m_c:
                try:
                    bstats_cycle = int(m_c.group(1))
                except ValueError:
                    pass

        # Fallback from charge_counter if level >= 10%
        if not est_mah and charge_counter_uah and level_num and level_num >= 10:
            est_mah = int((charge_counter_uah / 1000.0) / (level_num / 100.0))

        # Fallback to sysfs nodes for design & full capacity
        if not design_mah:
            sysfs_design = self.shell("cat /sys/class/power_supply/battery/charge_full_design 2>/dev/null") or \
                           self.shell("cat /sys/class/power_supply/bms/charge_full_design 2>/dev/null")
            if sysfs_design and sysfs_design.strip().isdigit():
                val = int(sysfs_design.strip())
                if val > 100000:
                    design_mah = val // 1000
                elif 500 <= val <= 20000:
                    design_mah = val

        if not est_mah:
            sysfs_full = self.shell("cat /sys/class/power_supply/battery/charge_full 2>/dev/null") or \
                         self.shell("cat /sys/class/power_supply/bms/charge_full 2>/dev/null")
            if sysfs_full and sysfs_full.strip().isdigit():
                val = int(sysfs_full.strip())
                if val > 100000:
                    est_mah = val // 1000
                elif 500 <= val <= 20000:
                    est_mah = val

        # Query cycle count via multi-level priority
        cmd_cycle = None
        cmd_out = self.shell("cmd battery get cycle_count 2>/dev/null")
        if cmd_out and cmd_out.strip().isdigit() and int(cmd_out.strip()) > 0:
            cmd_cycle = int(cmd_out.strip())

        cycle_val = None
        if samsung_usage is not None:
            cycle_val = samsung_usage // 100
        elif std_cycle is not None and std_cycle > 0:
            cycle_val = std_cycle
        elif bstats_cycle is not None and bstats_cycle > 0:
            cycle_val = bstats_cycle
        elif cmd_cycle is not None and cmd_cycle > 0:
            cycle_val = cmd_cycle
        elif sysfs_cycles and sysfs_cycles.strip().isdigit() and int(sysfs_cycles.strip()) > 0:
            cycle_val = int(sysfs_cycles.strip())
        else:
            root_cycle = self.root_shell("cat /sys/class/power_supply/battery/cycle_count 2>/dev/null")
            if root_cycle and root_cycle.strip().isdigit() and int(root_cycle.strip()) > 0:
                cycle_val = int(root_cycle.strip())

        if cycle_val is not None:
            info["cycle_count"] = f"{cycle_val} Kali Cas"
        else:
            info["cycle_count"] = "Terkunci Vendor OS (Non-Root)"

        # Calculate Health Percentage & Capacity Loss
        health_num = None
        if samsung_asoc is not None and 40 <= samsung_asoc <= 100:
            health_num = samsung_asoc
        elif est_mah and design_mah and design_mah > 0:
            health_num = min(100, round((est_mah / design_mah) * 100, 1))

        if design_mah:
            info["design_capacity"] = f"{design_mah} mAh"

        if est_mah:
            info["current_capacity"] = f"{est_mah} mAh"

        if design_mah and est_mah:
            diff = design_mah - est_mah
            if diff > 0:
                diff_pct = round((diff / design_mah) * 100, 1)
                info["capacity_loss"] = f"-{diff} mAh (Turun {diff_pct}%)"
            else:
                info["capacity_loss"] = "0 mAh (Masih 100% Penuh)"

        if health_num is not None:
            info["health_pct"] = f"{health_num}%"
            if health_num >= 85:
                info["note"] = f"Kesehatan baterai {health_num}% (Sangat Prima / Baterai Awet)."
            elif health_num >= 75:
                info["status_flag"] = "WARNING"
                info["note"] = f"Kesehatan baterai {health_num}% (Mulai Menurun / Pemakaian Wajar)."
            else:
                info["status_flag"] = "ALERT"
                info["note"] = f"Kesehatan baterai {health_num}% (DROP! Disarankan Ganti Baterai Baru)."

        return info

    def scan_storage(self):
        """Scans eMMC / UFS health & storage partitions."""
        info = {
            "type": "eMMC / UFS",
            "wear_level": "Normal",
            "wear_percentage": "Terproteksi Android 10+ (Non-Root)",
            "pre_eol_status": "Cadangan Blok Aman",
            "io_health": "OK",
            "free_space": "Unknown",
            "status_flag": "OK",
            "notes": []
        }

        # Check eMMC / UFS life time estimation (supports Root + Non-Root paths)
        raw_life = self.root_shell("cat /sys/block/mmcblk0/device/life_time 2>/dev/null") or \
                   self.root_shell("cat /sys/class/block/mmcblk0/device/life_time 2>/dev/null") or \
                   self.root_shell("cat /sys/block/sda/device/life_time 2>/dev/null") or \
                   self.root_shell("cat /sys/block/sda/device/health_descriptor/life_time_estimation_a 2>/dev/null")
        
        wear_dict = {
            "0x01": "0% - 10% (Sangat Sehat)",
            "0x02": "10% - 20% (Sehat)",
            "0x03": "20% - 30% (Normal)",
            "0x04": "30% - 40% (Normal)",
            "0x05": "40% - 50% (Normal)",
            "0x06": "50% - 60% (Sedang)",
            "0x07": "60% - 70% (Mulai Menua)",
            "0x08": "70% - 80% (Peringatan / Aus)",
            "0x09": "80% - 90% (Kritis / Hampir Habis)",
            "0x0a": "90% - 100% (SEKARAT / SEGERA MATI)",
            "0x0b": "Melebihi Batas Umur (RUSAK/BAD BLOCK)"
        }

        if raw_life:
            parts = raw_life.split()
            typ_a = parts[0] if len(parts) > 0 else ""
            typ_b = parts[1] if len(parts) > 1 else ""
            key = typ_a.lower() if typ_a else typ_b.lower()
            if key in wear_dict:
                info["wear_percentage"] = wear_dict[key]
                if key in ["0x09", "0x0a", "0x0b"]:
                    info["status_flag"] = "ALERT"
                    info["notes"].append("eMMC/UFS sudah aus parah! Ini penyebab umum HP restart/bootloop atau mati mendadak.")
                elif key in ["0x07", "0x08"]:
                    info["status_flag"] = "WARNING"
                    info["notes"].append("eMMC/UFS mulai menunjukkan keausan signifikan.")

        # Check Pre-EOL (End of Life) for eMMC and UFS
        pre_eol = self.root_shell("cat /sys/block/mmcblk0/device/pre_eol_info 2>/dev/null") or \
                  self.root_shell("cat /sys/block/sda/device/pre_eol_info 2>/dev/null")
        if pre_eol:
            if "0x01" in pre_eol:
                info["pre_eol_status"] = "Normal (Cadangan blok aman)"
            elif "0x02" in pre_eol:
                info["pre_eol_status"] = "Warning (80% Blok cadangan terpakai)"
                info["status_flag"] = "WARNING"
            elif "0x03" in pre_eol:
                info["pre_eol_status"] = "Urgent (Blok cadangan habis! Rawan rusak total)"
                info["status_flag"] = "ALERT"

        # Check I/O Health (Write & Read test in /data/local/tmp)
        io_test = self.shell("echo 'DIAGNOSTIC_IO_TEST' > /data/local/tmp/diag_test.tmp && cat /data/local/tmp/diag_test.tmp && rm /data/local/tmp/diag_test.tmp")
        if "DIAGNOSTIC_IO_TEST" in io_test:
            info["io_health"] = "Normal (Read & Write Lancar)"
        else:
            info["io_health"] = "Gagal Menulis (Partisi Read-Only / I-O Error)"
            info["status_flag"] = "ALERT"
            info["notes"].append("Partisi penyimpanan menolak operasi tulis (Read-Only)! Indikasi kerusakan memori.")

        # Check storage capacity
        df_out = self.shell("df -h /data")
        if df_out:
            lines = df_out.splitlines()
            if len(lines) >= 2:
                cols = lines[1].split()
                if len(cols) >= 4:
                    info["free_space"] = f"Total: {cols[1]}, Terpakai: {cols[2]}, Bebas: {cols[3]}"

        if not info["notes"]:
            info["notes"].append("Kesehatan chip penyimpanan dalam batas aman.")

        return info

    def scan_display(self):
        wm_size = self.shell("wm size") or ""
        wm_density = self.shell("wm density") or ""
        resolution = "Unknown"
        if "size:" in wm_size:
            resolution = wm_size.split("size:")[-1].strip()

        density = "Unknown"
        if "density:" in wm_density:
            density = wm_density.split("density:")[-1].strip() + " dpi"

        return {
            "resolution": resolution,
            "density": density,
            "status_flag": "OK",
            "note": "Resolusi dan rendering driver display terdeteksi."
        }

    def scan_touchscreen(self):
        inputs = self.shell("cat /proc/bus/input/devices") or ""
        touch_chips = ["goodix", "synaptics", "focaltech", "fts", "novatek", "ilitek", "touch", "touchscreen", "atmel"]
        detected_touch = []

        current_name = ""
        for line in inputs.splitlines():
            line = line.strip()
            if line.startswith("N: Name="):
                current_name = line.replace('N: Name=', '').replace('"', '')
                for chip in touch_chips:
                    if chip in current_name.lower():
                        detected_touch.append(current_name)
                        break

        if detected_touch:
            return {
                "controller": detected_touch[0],
                "status_flag": "OK",
                "note": f"Driver IC Touch terdeteksi ({detected_touch[0]})."
            }
        else:
            return {
                "controller": "Tidak Terdaftar di Bus Input",
                "status_flag": "WARNING",
                "note": "Chip Touch Controller tidak merespon di kernel (Fleksibel lepas / IC Touch mati)."
            }

    def scan_cameras(self):
        dump = self.shell("dumpsys media.camera") or ""
        num_cams = 0
        devices = []
        
        # Parse camera count
        cam_matches = re.findall(r"Camera ID:? (\d+)", dump, re.IGNORECASE)
        if not cam_matches:
            # Alternate pattern
            cam_matches = re.findall(r"Device (\d+) is", dump)
        
        if cam_matches:
            unique_cams = sorted(list(set(cam_matches)))
            num_cams = len(unique_cams)
            devices = [f"Camera ID {cid}" for cid in unique_cams]

        if num_cams > 0:
            return {
                "count": num_cams,
                "devices": ", ".join(devices),
                "status_flag": "OK",
                "note": f"Terdeteksi {num_cams} modul kamera aktif."
            }
        else:
            return {
                "count": 0,
                "devices": "Tidak ada kamera aktif",
                "status_flag": "ALERT",
                "note": "Layanan kamera tidak mendeteksi sensor kamera sama sekali (Modul putus/IC kamera error)."
            }

    def scan_sensors(self):
        dump = self.shell("dumpsys sensorservice") or ""
        sensor_list = []
        key_sensors = {
            "accelerometer": "Akselerometer (Kemiringan)",
            "gyroscope": "Giroskop",
            "proximity": "Proximity (Sensor Jarak)",
            "light": "Light (Sensor Cahaya)",
            "magnetic": "Magnetometer / Kompas",
            "barometer": "Barometer"
        }
        detected = []
        for line in dump.splitlines():
            line_lower = line.lower()
            for key, label in key_sensors.items():
                if key in line_lower and label not in detected:
                    detected.append(label)

        if len(detected) >= 2:
            return {
                "detected_count": len(detected),
                "sensors": ", ".join(detected),
                "status_flag": "OK",
                "note": f"{len(detected)} sensor terpasang & merespon."
            }
        else:
            return {
                "detected_count": len(detected),
                "sensors": ", ".join(detected) if detected else "Tidak terdeteksi",
                "status_flag": "WARNING",
                "note": "Jumlah sensor minim / Sensor Service tidak merespon bus I2C."
            }

    def scan_connectivity(self):
        wifi_mac = self.shell("cat /sys/class/net/wlan0/address 2>/dev/null") or ""
        wifi_mac = wifi_mac.strip()
        status_flag = "OK"
        notes = []

        if not wifi_mac:
            # Check dumpsys wifi
            wifi_dump = self.shell("dumpsys wifi")
            if "MAC:" in wifi_dump:
                m = re.search(r"([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})", wifi_dump)
                if m:
                    wifi_mac = m.group(1)

        if wifi_mac in ["02:00:00:00:00:00", "00:00:00:00:00:00", ""]:
            wifi_status = "Bermasalah / Dummy MAC"
            status_flag = "WARNING"
            notes.append("Alamat MAC Wi-Fi tidak valid. Kemungkinan chip Wi-Fi/NVRAM rusak.")
        else:
            wifi_status = f"Valid ({wifi_mac})"
            notes.append("Modul Wi-Fi terhubung dengan alamat MAC valid.")

        return {
            "wifi_mac": wifi_mac if wifi_mac else "Tidak terbaca",
            "wifi_status": wifi_status,
            "status_flag": status_flag,
            "note": "; ".join(notes)
        }

    def scan_kernel_hardware_faults(self):
        """Scans dmesg / logcat for hardware bus errors (I2C, SPI, PMIC, Sensor failure)."""
        # Try dmesg first
        logs = self.shell("dmesg 2>/dev/null")
        if not logs or len(logs) < 100:
            # Fallback to recent logcat
            logs = self.shell("logcat -d -t 250 2>/dev/null")

        fault_keywords = [
            ("i2c", "Komunikasi Bus I2C Gagal / IC tidak merespon"),
            ("spi", "Komunikasi Bus SPI Timeout"),
            ("probe failed", "Driver gagal menginisiasi IC Hardware"),
            ("thermal trip", "Proteksi Panas Berlebih / Sensor Suhu Drop"),
            ("mmcblk", "Kesalahan Input/Output Chip Memori (eMMC/UFS I/O Error)"),
            ("panic", "Kernel Panic / Crash Sistem"),
            ("camera", "Error pada Jalur Sensor Kamera"),
            ("audio", "Error pada Inisialisasi Audio Codec")
        ]

        found_issues = []
        if logs:
            for line in logs.splitlines()[-200:]: # Check last 200 lines
                line_lower = line.lower()
                for kw, desc in fault_keywords:
                    if kw in line_lower and any(err in line_lower for err in ["error", "fail", "timeout", "abort", "fault"]):
                        clean_line = line.strip()[:100]
                        found_issues.append({
                            "category": desc,
                            "log": clean_line
                        })
                        break

        # Deduplicate issues by category
        seen = set()
        deduped = []
        for issue in found_issues:
            if issue["category"] not in seen:
                seen.add(issue["category"])
                deduped.append(issue)

        return deduped
