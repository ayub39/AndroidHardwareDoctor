import os
import sys

# Ensure root folder is accessible for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, get_fastboot_path, run_cmd

# Graceful import for pyserial
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class DeviceDetector:
    @staticmethod
    def detect_adb():
        adb = get_adb_path()
        output = run_cmd([adb, "devices", "-l"], timeout=4)
        devices = []
        if not output:
            return devices

        lines = output.splitlines()
        valid_states = {"device", "unauthorized", "recovery", "sideload", "offline", "authorizing", "connecting"}
        for line in lines:
            line = line.strip()
            if not line or "List of devices" in line or line.startswith("*"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            serial_no = parts[0]
            state = parts[1].lower()
            if state not in valid_states:
                continue

            # Parse extra fields like model:xxx, product:xxx
            extra_info = {}
            for item in parts[2:]:
                if ":" in item:
                    k, v = item.split(":", 1)
                    extra_info[k] = v

            devices.append({
                "mode": "ADB",
                "serial": serial_no,
                "state": state,  # 'device', 'unauthorized', 'recovery', 'sideload', 'offline'
                "model": extra_info.get("model", "Android Device"),
                "product": extra_info.get("product", ""),
                "device": extra_info.get("device", ""),
            })
        return devices

    @staticmethod
    def detect_fastboot():
        fastboot = get_fastboot_path()
        output = run_cmd([fastboot, "devices"], timeout=3, capture_stderr=False)
        devices = []
        if not output:
            return devices

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1].lower().startswith("fastboot"):
                is_fastbootd = "fastbootd" in parts[1].lower()
                devices.append({
                    "mode": "FASTBOOT",
                    "serial": parts[0],
                    "state": "fastbootd" if is_fastbootd else "fastboot",
                    "model": "Fastbootd Mode (Userspace)" if is_fastbootd else "Bootloader / Fastboot Mode"
                })
        return devices

    @staticmethod
    def detect_com_ports():
        """Scans COM ports for low-level recovery ports (EDL 9008, MTK BROM, etc.)"""
        if not SERIAL_AVAILABLE:
            return []

        try:
            ports = serial.tools.list_ports.comports()
        except Exception:
            return []

        detected = []
        for p in ports:
            desc = p.description or ""
            hwid = p.hwid or ""
            desc_lower = desc.lower()
            hwid_lower = hwid.lower()

            # Qualcomm EDL 9008
            if "9008" in desc or "05c6:9008" in hwid_lower or "qdloader" in desc_lower:
                detected.append({
                    "mode": "EDL_QUALCOMM",
                    "port": p.device,
                    "description": desc,
                    "title": "Qualcomm HS-USB QDLoader 9008",
                    "diagnosis": "Mode Darurat EDL Qualcomm aktif. Kemungkinan: eMMC/UFS mati/korup, atau bootloader terhapus total (Hardbrick)."
                })
            # MediaTek BROM / Preloader
            elif "0e8d" in hwid_lower or "mediatek" in desc_lower or "mtk" in desc_lower:
                detected.append({
                    "mode": "MTK_BROM",
                    "port": p.device,
                    "description": desc,
                    "title": "MediaTek USB / PreLoader Port",
                    "diagnosis": "Mode Darurat MediaTek (BROM / Preloader). CPU aktif, siap flashing atau tes memori."
                })
            # Spreadtrum / Unisoc (VID 1782 + PID spesifik)
            elif ("1782" in hwid_lower and ("d00d" in hwid_lower or "4d00" in hwid_lower)) or \
                 "sprd" in desc_lower or "unisoc" in desc_lower:
                detected.append({
                    "mode": "UNISOC_DIAG",
                    "port": p.device,
                    "description": desc,
                    "title": "Unisoc / Spreadtrum Diag Port",
                    "diagnosis": "Mode Diagnostik Unisoc/Spreadtrum terdeteksi."
                })
        return detected

    @classmethod
    def get_connected_status(cls):
        """Returns primary active device status."""
        try:
            adb_devs = cls.detect_adb()
            if adb_devs:
                return {"status": "CONNECTED", "type": "ADB", "device": adb_devs[0]}

            fastboot_devs = cls.detect_fastboot()
            if fastboot_devs:
                return {"status": "CONNECTED", "type": "FASTBOOT", "device": fastboot_devs[0]}

            com_devs = cls.detect_com_ports()
            if com_devs:
                return {"status": "CONNECTED", "type": "COM", "device": com_devs[0]}
        except Exception:
            pass

        return {"status": "DISCONNECTED", "type": "NONE", "device": None}
