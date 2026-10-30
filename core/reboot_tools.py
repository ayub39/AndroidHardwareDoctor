import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, get_fastboot_path, run_cmd


class RebootTools:
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.fastboot = get_fastboot_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]

    def _adb(self, *args, timeout=5):
        return run_cmd(list(self.base_cmd) + list(args), timeout=timeout)

    def _fastboot(self, *args, timeout=8):
        cmd = [self.fastboot]
        if self.serial:
            cmd += ["-s", self.serial]
        cmd += list(args)
        return run_cmd(cmd, timeout=timeout)

    def reboot_normal(self):
        return self._adb("reboot")

    def reboot_recovery(self):
        return self._adb("reboot", "recovery")

    def reboot_bootloader(self):
        return self._adb("reboot", "bootloader")

    def reboot_edl(self):
        return self._adb("reboot", "edl")

    def fastboot_reboot(self):
        """Reboots device from Fastboot mode straight into normal Android OS."""
        return self._fastboot("reboot")

    def fastboot_set_autocharge(self, enable=True):
        """Sets off-mode-charge to 0 (auto-powers on when plugged in)."""
        val = "0" if enable else "1"
        return self._fastboot("oem", "off-mode-charge", val)

    def power_off(self):
        """Graceful shutdown with fallback."""
        result = self._adb("shell", "reboot", "-p", timeout=4)
        if not result:
            self._adb("shell", "setprop", "sys.powerctl", "shutdown", timeout=4)
        return True

    def wakeup_screen(self):
        """Wakes up / turns on screen."""
        return self._adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")

