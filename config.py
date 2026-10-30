import os
import shutil
import subprocess

# Base directory aplikasi (selalu relatif ke lokasi file ini, bukan CWD)
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Common paths where Android platform-tools might be installed (Local bin first for safety)
POSSIBLE_ADB_PATHS = [
    os.path.join(APP_DIR, "bin", "adb.exe"),
    r"C:\platform-tools\adb.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Android\Sdk\platform-tools\adb.exe"),
]

POSSIBLE_FASTBOOT_PATHS = [
    os.path.join(APP_DIR, "bin", "fastboot.exe"),
    r"C:\platform-tools\fastboot.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Android\Sdk\platform-tools\fastboot.exe"),
]

def _is_working_binary(exe_path: str, test_arg: str = "version") -> bool:
    """Verifies that the binary exists and executes cleanly without 0xc0000005 crash."""
    if not exe_path or not os.path.exists(exe_path):
        return False
    try:
        res = subprocess.run(
            [exe_path, test_arg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return res.returncode == 0
    except Exception:
        return False

def get_adb_path() -> str:
    # 1. Check priority paths with health test
    for p in POSSIBLE_ADB_PATHS:
        if p and os.path.exists(p) and _is_working_binary(p, "version"):
            return p
    # 2. Check system PATH
    which_adb = shutil.which("adb")
    if which_adb and _is_working_binary(which_adb, "version"):
        return which_adb
    return "adb"

def get_fastboot_path() -> str:
    # 1. Check priority paths with health test (--version for fastboot)
    for p in POSSIBLE_FASTBOOT_PATHS:
        if p and os.path.exists(p) and _is_working_binary(p, "--version"):
            return p
    # 2. Check system PATH
    which_fastboot = shutil.which("fastboot")
    if which_fastboot and _is_working_binary(which_fastboot, "--version"):
        return which_fastboot
    return "fastboot"

def check_adb_available() -> bool:
    """Returns True if ADB binary is accessible."""
    adb = get_adb_path()
    try:
        subprocess.run(
            [adb, "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False

def run_cmd(args, timeout=10, capture_stderr=True) -> str:
    """
    Executes command and returns stripped stdout (+ stderr if capture_stderr=True).
    Safe against timeouts and decode errors.
    Returns empty string on error (never raises).
    """
    try:
        stderr_target = subprocess.STDOUT if capture_stderr else subprocess.PIPE
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=stderr_target,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            encoding='utf-8',
            errors='ignore'
        )
        return proc.stdout.strip() if proc.stdout else ""
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""
