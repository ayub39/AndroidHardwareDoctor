import os
import sys
import shutil
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, APP_DIR


class ScreenMirrorManager:
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]

    def has_scrcpy(self) -> bool:
        """Checks if scrcpy is installed in PATH or local directory."""
        if shutil.which("scrcpy"):
            return True
        local_scrcpy = os.path.join(APP_DIR, "bin", "scrcpy.exe")
        return os.path.exists(local_scrcpy)

    def launch_scrcpy(self) -> tuple[bool, str]:
        """Launches scrcpy if available."""
        exe = shutil.which("scrcpy")
        if not exe:
            local_scrcpy = os.path.join(APP_DIR, "bin", "scrcpy.exe")
            if os.path.exists(local_scrcpy):
                exe = local_scrcpy

        if not exe:
            return False, "scrcpy.exe belum terpasang di sistem. Letakkan file scrcpy.exe di folder bin."

        cmd = [exe]
        if self.serial:
            cmd += ["-s", self.serial]
        try:
            # scrcpy is a graphical SDL app; do not suppress its window with CREATE_NO_WINDOW
            subprocess.Popen(cmd)
            return True, "Scrcpy berhasil dijalankan!"
        except Exception as e:
            return False, str(e)

    def take_screenshot(self, save_dir=None) -> str:
        """Captures phone screen and saves as PNG."""
        if not save_dir:
            save_dir = os.path.join(APP_DIR, "screenshots")
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"screen_{int(time.time())}.png")
        cmd = self.base_cmd + ["exec-out", "screencap", "-p"]
        try:
            with open(filename, "wb") as f:
                subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=8,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
            if os.path.exists(filename) and os.path.getsize(filename) > 1000:
                return filename
            elif os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception:
                    pass
        except Exception:
            pass
        return ""

    def backup_photos(self, dest_folder=None) -> tuple[bool, str]:
        """Backs up all JPG photos from all directories across device storage."""
        try:
            from core.data_rescue import DataRescueManager
            rescue = DataRescueManager(serial=self.serial)
            ok, msg, _ = rescue.backup_all_jpg(dest_folder=dest_folder)
            return ok, msg
        except Exception as e:
            return False, f"Gagal backup: {str(e)}"
