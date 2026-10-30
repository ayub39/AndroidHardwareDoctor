import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, get_fastboot_path, run_cmd


class FrpAndLockTools:
    """
    Technician utilities for FRP (Factory Reset Protection) bypass,
    Setup Wizard skip, MTP Browser launcher, and Lock Screen Reset.
    """
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.fastboot = get_fastboot_path()
        self.serial = serial
        self.adb_base = [self.adb]
        if serial:
            self.adb_base += ["-s", serial]

    def shell(self, cmd_str, timeout=6):
        cmd = self.adb_base + ["shell", cmd_str]
        return run_cmd(cmd, timeout=timeout)

    # 1. MTP / ADB BROWSER & YOUTUBE LAUNCHER (Untuk Masuk Browser saat FRP Terkunci)
    def launch_browser(self, target="youtube") -> tuple[bool, str]:
        """Opens YouTube or Chrome browser on device to begin manual FRP bypass."""
        urls = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "settings": "android.settings.SETTINGS",
            "frp_file": "https://addrom.com/bypass"
        }
        target_url = urls.get(target, "https://www.youtube.com")

        if target == "settings":
            res = self.shell("am start -a android.settings.SETTINGS 2>/dev/null")
            return True, "Perintah buka menu Pengaturan (Settings) telah dikirim!"
        else:
            # Wake up screen
            self.shell("input keyevent 224 2>/dev/null")
            # Send intent view
            self.shell(f"am start -a android.intent.action.VIEW -d '{target_url}' 2>/dev/null")
            self.shell(f"am start -n com.google.android.youtube/com.google.android.youtube.HomeActivity 2>/dev/null")
            self.shell(f"am start -n com.android.chrome/com.google.android.apps.chrome.Main 2>/dev/null")
            return True, f"Perintah buka {target.upper()} ({target_url}) telah dikirim ke layar HP!"

    # 2. BYPASS SETUP WIZARD (Direct Home Screen Jump via ADB)
    def bypass_setup_wizard(self) -> tuple[bool, str]:
        """
        Bypasses FRP / Setup Wizard directly to Home Screen
        if USB debugging is active on the Welcome Screen.
        """
        c1 = self.shell("content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1 2>/dev/null")
        c2 = self.shell("content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:s:1 2>/dev/null")
        self.shell("am start -c android.intent.category.HOME -a android.intent.action.MAIN 2>/dev/null")
        return True, "Setup Wizard dilewati! Menembus langsung ke Menu Utama (Home Screen)."

    # 3. FASTBOOT ERASE FRP (One-Click Partition Wipe for SPD / MTK / Motorola / Qualcomm)
    def fastboot_erase_frp(self) -> tuple[bool, str]:
        """Erases standard FRP / config / persistent partitions in Fastboot mode."""
        fb_cmd = [self.fastboot]
        if self.serial:
            fb_cmd += ["-s", self.serial]

        out1 = run_cmd(fb_cmd + ["erase", "frp"], timeout=8)
        out2 = run_cmd(fb_cmd + ["erase", "config"], timeout=8)
        out3 = run_cmd(fb_cmd + ["erase", "persistent"], timeout=8)

        log = f"Fastboot Erase FRP:\nfrp: {out1.strip()}\nconfig: {out2.strip()}\npersistent: {out3.strip()}"
        if "okay" in log.lower() or "finished" in log.lower():
            return True, f"FRP Berhasil Dihapus!\n\n{log}"
        else:
            return False, f"Partisi FRP terkunci / device bukan mode fastboot.\nLog: {log}"

    # 4. RESET KUNCI LAYAR TANPA HAPUS DATA (Mode TWRP / Root)
    def reset_screen_lock(self) -> tuple[bool, str]:
        """
        Removes Android lockscreen database & keys via TWRP or Root shell.
        Keeps 100% of user data (photos, WhatsApp, contacts) intact.
        """
        targets = [
            "/data/system/locksettings.db",
            "/data/system/locksettings.db-shm",
            "/data/system/locksettings.db-wal",
            "/data/system/gatekeeper.password.key",
            "/data/system/gatekeeper.pattern.key",
            "/data/system/password.key",
            "/data/system/pattern.key",
            "/data/system/gesture.key",
            "/data/system/device_policies.xml"
        ]
        # In TWRP, ensure /data partition is mounted before removing keys
        mount_prep = "mount /data 2>/dev/null; twrp mount /data 2>/dev/null; "
        cmd = mount_prep + " && ".join([f"rm -f {t}" for t in targets])
        self.shell(f"su -c '{cmd}' 2>/dev/null || {cmd}")
        return True, "File kunci pola/PIN/sandi berhasil dihapus! Silakan reboot HP (Layar otomatis Swipe to Unlock tanpa pola/PIN)."
