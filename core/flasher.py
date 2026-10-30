import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_fastboot_path, get_adb_path, run_cmd


class FirmwareFlasher:
    def __init__(self, serial=None):
        self.fastboot = get_fastboot_path()
        self.adb = get_adb_path()
        self.serial = serial
        self.base_fb = [self.fastboot]
        self.base_adb = [self.adb]
        if serial:
            self.base_fb += ["-s", serial]
            self.base_adb += ["-s", serial]

    # 1. FASTBOOT SINGLE PARTITION FLASH
    def flash_partition(self, partition: str, file_path: str, disable_verity: bool = False, on_log=None) -> tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, f"File image tidak ditemukan: {file_path}"

        cmd = list(self.base_fb)
        if partition.lower() == "vbmeta" and disable_verity:
            cmd += ["--disable-verity", "--disable-verification"]

        cmd += ["flash", partition, file_path]

        if on_log:
            on_log(f"Menjalankan: {' '.join(cmd)}\n")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                if on_log:
                    on_log(line)
            proc.wait()
            success = (proc.returncode == 0)
            return success, "".join(output_lines)
        except Exception as e:
            return False, str(e)

    # 2. FASTBOOT ERASE / FORMAT PARTITION
    def erase_partition(self, partition: str, on_log=None) -> tuple[bool, str]:
        cmd = list(self.base_fb) + ["erase", partition]
        if on_log:
            on_log(f"Menghapus partisi '{partition}'...\n")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                if on_log:
                    on_log(line)
            proc.wait()
            return (proc.returncode == 0), "".join(output_lines)
        except Exception as e:
            return False, str(e)

    # 3. SLOT A/B SWITCHER
    def get_current_slot(self) -> str:
        cmd = list(self.base_fb) + ["getvar", "current-slot"]
        res = run_cmd(cmd, timeout=5, capture_stderr=True)
        for line in res.splitlines():
            if "current-slot" in line.lower():
                raw = line.split(":")[-1].strip().lstrip("_")
                return raw.lower()
        return "Unknown / Single Slot (Non A/B)"

    def set_active_slot(self, slot: str, on_log=None) -> tuple[bool, str]:
        slot = slot.lower()
        if slot not in ["a", "b"]:
            return False, "Slot harus 'a' atau 'b'!"
        cmd = list(self.base_fb) + [f"--set-active={slot}"]
        if on_log:
            on_log(f"Mengubah slot aktif ke '{slot}'...\n")
        res = run_cmd(cmd, timeout=10, capture_stderr=True)
        if on_log:
            on_log(res + "\n")
        success = bool(res and "failed" not in res.lower() and "error" not in res.lower())
        return success, res

    # 4. ADB SIDELOAD (.ZIP OTA / RECOVERY FIRMWARE)
    def sideload_ota_zip(self, zip_path: str, on_log=None) -> tuple[bool, str]:
        if not os.path.exists(zip_path):
            return False, f"File zip tidak ditemukan: {zip_path}"

        cmd = list(self.base_adb) + ["sideload", zip_path]
        if on_log:
            on_log(f"Memulai ADB Sideload: {' '.join(cmd)}\nHarap tunggu proses pengiriman firmware...\n")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                if on_log:
                    on_log(line)
            proc.wait()
            success = (proc.returncode == 0)
            return success, "".join(output_lines)
        except Exception as e:
            return False, str(e)

    # 5. RUN BATCH FLASH SCRIPT (Safe execution without shell=True)
    def run_rom_flash_script(self, script_path: str, on_log=None) -> tuple[bool, str]:
        if not os.path.exists(script_path):
            return False, f"Script flash tidak ditemukan: {script_path}"

        script_dir = os.path.dirname(os.path.abspath(script_path))
        if on_log:
            on_log(f"Menjalankan script ROM resmi dari: {script_dir}\n")

        try:
            # Use cmd.exe /c to run .bat securely without shell=True command injection risks
            if script_path.lower().endswith(('.bat', '.cmd')):
                cmd = ["cmd.exe", "/c", os.path.abspath(script_path)]
            else:
                cmd = [os.path.abspath(script_path)]

            proc = subprocess.Popen(
                cmd,
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                if on_log:
                    on_log(line)
            proc.wait()
            return (proc.returncode == 0), "".join(output_lines)
        except Exception as e:
            return False, str(e)
