import os
import subprocess
import webbrowser
import winreg

class DriverHelper:
    """
    UnlockTool-style Driver Assistant for Windows GSM Technicians.
    Checks installed drivers and provides one-click installers & diagnostics.
    """

    DRIVERS = [
        {
            "id": "qualcomm_9008",
            "name": "Qualcomm HS-USB QDLoader 9008",
            "vendor": "Qualcomm",
            "hardware_id": "USB\\VID_05C6&PID_9008",
            "description": "Wajib untuk unbrick HP chipset Snapdragon via Test Point / Emergency Download Mode.",
            "download_url": "https://developer.qualcomm.com/"
        },
        {
            "id": "mediatek_vcom",
            "name": "MediaTek USB VCOM / PreLoader / BROM",
            "vendor": "MediaTek",
            "hardware_id": "USB\\VID_0E8D&PID_0003",
            "description": "Wajib untuk flashing dan tes HP chipset MediaTek (Helio / Dimensity).",
            "download_url": "https://spflashtool.com/download/"
        },
        {
            "id": "samsung_cdc",
            "name": "Samsung Mobile USB Composite Device",
            "vendor": "Samsung Electronics",
            "hardware_id": "USB\\VID_04E8",
            "description": "Wajib untuk koneksi Odin / Download Mode dan ADB Samsung.",
            "download_url": "https://developer.samsung.com/android-usb-driver"
        },
        {
            "id": "google_adb",
            "name": "Google Android ADB & Fastboot Interface",
            "vendor": "Google",
            "hardware_id": "USB\\VID_18D1",
            "description": "Driver standar komunikasi Android Debug Bridge & Bootloader Fastboot.",
            "download_url": "https://developer.android.com/studio/run/win-usb"
        },
        {
            "id": "libusb_filter",
            "name": "LibUSB-win32 / UsbDk Filter Driver",
            "vendor": "Open Source / LibUSB",
            "hardware_id": "LIBUSB",
            "description": "Solusi ampuh mengatasi port MediaTek / 9008 yang PUTUS-NYAMBUNG saat dicolok!",
            "download_url": "https://sourceforge.net/projects/libusb-win32/"
        }
    ]

    @classmethod
    def check_driver_status(cls, driver_id: str) -> bool:
        """
        Scans Windows PNP registry for matching hardware IDs.
        """
        target = next((d for d in cls.DRIVERS if d["id"] == driver_id), None)
        if not target:
            return False

        hwid = target["hardware_id"].lower()
        if hwid == "libusb":
            # Check for libusb0.sys or usbdk in System32\drivers
            sys_root = os.environ.get("SystemRoot", "C:\\Windows")
            p1 = os.path.join(sys_root, "System32", "drivers", "libusb0.sys")
            p2 = os.path.join(sys_root, "System32", "drivers", "UsbDk.sys")
            if os.path.exists(p1) or os.path.exists(p2):
                return True

        # Check Windows Services registry (driver package installed)
        service_map = {
            "qualcomm_9008": ["qcusbser", "qcser", "qcusbtest"],
            "mediatek_vcom": ["wmt_mdm", "mtk_usb", "usb2ser"],
            "samsung_cdc": ["ssudbus", "dg_ssudbus", "ssudmdm"],
            "google_adb": ["winusb", "androidwinusb"],
            "libusb_filter": ["libusb0", "usbdk"]
        }
        for s in service_map.get(driver_id, []):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, rf"SYSTEM\CurrentControlSet\Services\{s}"):
                    return True
            except OSError:
                pass

        # Check in Windows Enum USB registry (device has been connected)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\USB") as key:
                count = winreg.QueryInfoKey(key)[0]
                for i in range(count):
                    subkey_name = winreg.EnumKey(key, i)
                    parts = hwid.split("\\")[-1].split("&")
                    if all(part in subkey_name.lower() for part in parts):
                        return True
        except Exception:
            pass

        return False

    @staticmethod
    def open_device_manager():
        """Opens Windows Device Manager (devmgmt.msc) directly."""
        try:
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "devmgmt.msc"],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except Exception:
            return False

    @staticmethod
    def open_driver_download(url: str):
        """Opens official driver download page in default browser."""
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False
