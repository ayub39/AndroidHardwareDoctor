import os
import sys
import threading
import subprocess
import re
import zlib
import struct
import http.server
import socketserver

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, run_cmd, APP_DIR


class HardwareTester:
    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]
        self._key_listener_proc = None
        self._key_listener_thread = None
        self._listening = False
        self.last_key_error = None
        self._touch_listener_proc = None
        self._touch_listener_thread = None
        self._touch_listening = False
        self.last_touch_error = None

    def shell(self, cmd_str, timeout=6):
        cmd = self.base_cmd + ["shell", cmd_str]
        return run_cmd(cmd, timeout=timeout)

    # 1. VIBRATOR TEST (Supports Android 8 through 15 + Sysfs + MIUI/OneUI)
    def test_vibrator(self, duration_ms=1500) -> tuple[bool, str]:
        """
        Triggers vibration across all Android versions:
        - Android 12+ (vibrator_manager)
        - Android 8-11 (vibrator)
        - Kernel sysfs nodes (Qualcomm / MTK / Exynos)
        """
        # Wake up screen to prevent OS power-saver from swallowing vibration
        self.shell("input keyevent 224 2>/dev/null")

        # 1. Android 12, 13, 14, 15 (vibrator_manager)
        res_vm = self.shell(f"cmd vibrator_manager synced -f oneshot {duration_ms} 255 2>/dev/null")
        if not res_vm or "error" in res_vm.lower() or "not found" in res_vm.lower():
            self.shell(f"cmd vibrator_manager vibrate {duration_ms} 2>/dev/null")

        # 2. Android 8, 9, 10, 11 (vibrator)
        res_v = self.shell(f"cmd vibrator vibrate {duration_ms} 2>/dev/null")
        if not res_v or "error" in res_v.lower():
            self.shell(f"cmd vibrator waveform 0 {duration_ms} 2>/dev/null")

        # 3. Direct Hardware Sysfs Trigger (Root & Non-Root fallback)
        self.shell(f"echo {duration_ms} > /sys/class/timed_output/vibrator/enable 2>/dev/null")
        self.shell(f"echo {duration_ms} > /sys/class/leds/vibrator/duration 2>/dev/null; echo 1 > /sys/class/leds/vibrator/activate 2>/dev/null")
        self.shell(f"su -c 'echo {duration_ms} > /sys/class/timed_output/vibrator/enable' 2>/dev/null")
        self.shell(f"su -c 'echo {duration_ms} > /sys/class/leds/vibrator/duration; echo 1 > /sys/class/leds/vibrator/activate' 2>/dev/null")

        return True, "Sinyal getar telah dikirim ke perangkat (vibrator_manager & sysfs)."

    # 2. FLASHLIGHT / TORCH TEST (Hardware sysfs + Quick Settings auto-expand)
    def toggle_torch(self, state=True) -> tuple[bool, str]:
        """
        Toggles flashlight via kernel sysfs LED nodes (rooted / factory devices)
        and exposes Quick Settings Flashlight tile on screen (non-rooted devices).
        """
        torch_nodes = [
            "/sys/class/leds/torch-light/brightness",
            "/sys/class/leds/flashlight/brightness",
            "/sys/class/leds/led:flash_torch/brightness",
            "/sys/class/leds/led:torch_0/brightness",
            "/sys/class/leds/led:torch_1/brightness",
            "/sys/class/leds/torch/brightness",
            "/sys/class/leds/flash/brightness",
            "/sys/devices/virtual/camera/flash/rear_flash"
        ]

        if state:
            # Wake up display
            self.shell("input keyevent 224 2>/dev/null")

            # Try direct hardware sysfs write
            for node in torch_nodes:
                self.shell(f"echo 255 > {node} 2>/dev/null || echo 1 > {node} 2>/dev/null || su -c 'echo 255 > {node}' 2>/dev/null")

            # Expand Quick Settings panel on screen so technician can tap Torch icon with 1 click
            self.shell("cmd statusbar expand-settings 2>/dev/null || service call statusbar 2 2>/dev/null")

            return True, "LED Sysfs dipicu & panel Quick Settings dibuka di layar HP."
        else:
            # Turn off sysfs nodes
            for node in torch_nodes:
                self.shell(f"echo 0 > {node} 2>/dev/null || su -c 'echo 0 > {node}' 2>/dev/null")

            # Collapse status bar
            self.shell("cmd statusbar collapse 2>/dev/null || service call statusbar 1 2>/dev/null")

            return True, "Senter dimatikan."

    # 3. SPEAKER / AUDIO TEST (Unmute + Dynamic audio search)
    def test_speaker(self) -> tuple[bool, str]:
        """Plays a test tone or ringtone through device speaker."""
        # Unmute and set max media + ring volume
        self.shell("media volume --stream 3 --set 15 2>/dev/null; media volume --stream 2 --set 15 2>/dev/null; input keyevent 24; input keyevent 24")

        # Dynamically discover any built-in system ogg file
        found = self.shell(
            "find /system/media/audio /product/media/audio /system/product/media/audio -type f -name '*.ogg' 2>/dev/null | head -n 1"
        )
        audio_target = found.strip() if found and found.strip() else "/system/media/audio/ringtones/Default.ogg"

        self.shell(
            f"am start -a android.intent.action.VIEW -d file://{audio_target} -t audio/ogg -f 1 2>/dev/null"
        )
        return True, f"Memutar audio uji ({os.path.basename(audio_target)})."

    # 3b. EARPIECE TEST (Speaker Telinga Telepon Atas)
    def test_earpiece(self) -> tuple[bool, str]:
        """Plays test audio through front ear speaker (Voice Call stream 0)."""
        self.shell("media volume --stream 0 --set 15 2>/dev/null")
        self.shell("cmd audio set-speakerphone-on false 2>/dev/null; service call audio 21 i32 0 2>/dev/null")

        found = self.shell(
            "find /system/media/audio /product/media/audio -type f -name '*.ogg' 2>/dev/null | head -n 1"
        )
        audio_target = found.strip() if found and found.strip() else "/system/media/audio/ringtones/Default.ogg"

        self.shell(f"stagefright -a -o {audio_target} 2>/dev/null || am start -a android.intent.action.VIEW -d file://{audio_target} -t audio/ogg -f 1 2>/dev/null")
        return True, "Sinyal suara dikirim ke Earpiece (Speaker Atas). Dekatkan HP ke telinga."

    # 3c. MIC TEST & LOOPBACK (Microphone Recording + Auto Playback)
    def test_mic_loopback(self) -> tuple[bool, str]:
        """Records 3 seconds from microphone and plays it back immediately to test IC Codec & Mic."""
        wav_path = "/data/local/tmp/mic_test.wav"
        self.shell(f"rm -f {wav_path} 2>/dev/null")

        # Record 3 seconds via tinycap with safe POSIX PID capture
        rec_cmd = (
            f"(tinycap {wav_path} -d 0 -c 1 -r 16000 -b 16 -p 1024 -n 4 & "
            f"PID=$!; sleep 3; kill -9 $PID 2>/dev/null; pkill -9 tinycap 2>/dev/null; killall -9 tinycap 2>/dev/null) 2>/dev/null"
        )
        self.shell(rec_cmd, timeout=6)

        chk = self.shell(f"ls -l {wav_path} 2>/dev/null")
        is_empty = True
        if chk and "No such file" not in chk:
            parts = chk.split()
            if len(parts) > 4 and parts[4].isdigit() and int(parts[4]) > 1000:
                is_empty = False

        if is_empty:
            self.shell("am start -a android.provider.MediaStore.RECORD_SOUND 2>/dev/null")
            return True, "Aplikasi perekam suara dibuka di layar HP. Ucapkan suara untuk tes mic."

        self.shell("media volume --stream 3 --set 15 2>/dev/null")
        self.shell(f"stagefright -a -o {wav_path} 2>/dev/null || am start -a android.intent.action.VIEW -d file://{wav_path} -t audio/wav -f 1 2>/dev/null")
        return True, "Mic berhasil merekam 3 detik & memutar balik suara ke speaker utama!"

    # 4. LCD SOLID COLOR TEST (PNG generation + Gallery / Photo Viewer full screen)
    def test_lcd_color(self, hex_color="#FF0000") -> tuple[bool, str]:
        """
        Generates a 100% solid color PNG and displays it edge-to-edge
        via native Gallery viewer for foolproof dead pixel detection.
        """
        clean_hex = re.sub(r'[^0-9a-fA-F]', '', hex_color)[:6].upper()
        if len(clean_hex) != 6:
            clean_hex = "FF0000"

        r = int(clean_hex[0:2], 16)
        g = int(clean_hex[2:4], 16)
        b = int(clean_hex[4:6], 16)

        # Generate minimal pure PNG in memory
        png_data = self._generate_solid_png(r, g, b, 400, 400)

        # Write to local cache folder
        cache_dir = os.path.join(APP_DIR, "data")
        os.makedirs(cache_dir, exist_ok=True)
        local_png = os.path.join(cache_dir, f"color_{clean_hex}.png")
        try:
            with open(local_png, "wb") as f:
                f.write(png_data)
        except OSError:
            pass

        # Wake up screen
        self.shell("input keyevent 224 2>/dev/null")

        # Push to phone storage
        remote_png = f"/sdcard/Download/screen_test_{clean_hex}.png"
        push_cmd = self.base_cmd + ["push", local_png, remote_png]
        run_cmd(push_cmd, timeout=8)

        # Trigger media scanner & open in full screen Gallery / Photos
        self.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_png} 2>/dev/null")
        self.shell(f"am start -a android.intent.action.VIEW -d file://{remote_png} -t image/png -f 1 2>/dev/null")

        # HTML offline file fallback in browser
        html_content = f"<html><body style='background:#{clean_hex};margin:0;padding:0;width:100vw;height:100vh;overflow:hidden;'></body></html>"
        self.shell(f"echo \"{html_content}\" > /sdcard/Download/screen_{clean_hex}.html 2>/dev/null")

        return True, f"Menampilkan warna solid #{clean_hex} di layar HP via Galeri Foto."

    @staticmethod
    def _generate_solid_png(r: int, g: int, b: int, width: int = 400, height: int = 400) -> bytes:
        """Pure Python PNG generator with no external PIL dependencies."""
        raw = b''.join([b'\x00' + bytes([r, g, b]) * width for _ in range(height)])
        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

    # 5. PHYSICAL KEY EVENT LISTENER
    def start_key_listener(self, on_key_detected):
        """
        Listens to physical buttons (Power, Vol+, Vol-) in background thread.
        on_key_detected(key_name, action): Callback function.
        """
        if self._listening:
            return

        self._listening = True
        self.last_key_error = None

        def worker():
            cmd = self.base_cmd + ["shell", "getevent", "-l"]
            try:
                self._key_listener_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                for line in self._key_listener_proc.stdout:
                    if not self._listening:
                        break
                    line = line.strip().lower()
                    if "key_" in line:
                        action = "DOWN" if "down" in line else ("UP" if "up" in line else "PRESS")
                        if "volumeup" in line:
                            on_key_detected("VOLUME_UP", action)
                        elif "volumedown" in line:
                            on_key_detected("VOLUME_DOWN", action)
                        elif "power" in line:
                            on_key_detected("POWER", action)
            except Exception as e:
                self.last_key_error = str(e)
            finally:
                self._listening = False

        self._key_listener_thread = threading.Thread(target=worker, daemon=True)
        self._key_listener_thread.start()

    def stop_key_listener(self):
        self._listening = False
        if self._key_listener_proc:
            try:
                self._key_listener_proc.terminate()
            except Exception:
                pass
            self._key_listener_proc = None
        if self._key_listener_thread and self._key_listener_thread.is_alive():
            self._key_listener_thread.join(timeout=1.5)
        self._key_listener_thread = None

    # -------------------------------------------------------------
    # 6. TOUCHSCREEN DIGITIZER & DEAD-ZONE TEST SUITE
    # -------------------------------------------------------------
    def set_pointer_location(self, enable=True) -> tuple[bool, str]:
        """
        Enables or disables Android's native Pointer Location and Touch Trail overlay.
        Allows technicians to visually draw across the screen to detect dead touch zones,
        line breaks, or ghost touches.
        """
        val = "1" if enable else "0"
        self.shell(f"settings put system pointer_location {val} 2>/dev/null")
        self.shell(f"settings put system show_touches {val} 2>/dev/null")
        self.shell(f"su -c 'settings put system pointer_location {val}; settings put system show_touches {val}' 2>/dev/null")

        # Wake up screen to show overlay immediately
        self.shell("input keyevent 224 2>/dev/null")

        if enable:
            return True, "Jejak Koordinat Sentuh (Pointer Location) AKTIF! Silakan usap seluruh layar HP."
        else:
            return True, "Jejak Koordinat Sentuh (Pointer Location) DIMATIKAN."

    def get_pointer_location_state(self) -> bool:
        """Checks if pointer_location is currently active on the device."""
        res = self.shell("settings get system pointer_location 2>/dev/null")
        return bool(res and res.strip() == "1")

    # --- EMBEDDED HTTP SERVER FOR TOUCH GRID (BYPASS ERR_ACCESS_DENIED) ---
    _httpd_server = None
    _httpd_port = 8999

    @classmethod
    def _start_touch_http_server(cls, html_content: str, base_port: int = 8999) -> int:
        if cls._httpd_server is not None:
            return cls._httpd_port

        class _TouchHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(html_content.encode("utf-8"))

            def log_message(self, format, *args):
                pass  # suppress console logging

        for p in [base_port, 9099, 8888, 7777]:
            try:
                cls._httpd_server = socketserver.TCPServer(("127.0.0.1", p), _TouchHandler)
                cls._httpd_port = p
                t = threading.Thread(target=cls._httpd_server.serve_forever, daemon=True)
                t.start()
                break
            except Exception:
                continue

        return cls._httpd_port

    @staticmethod
    def _get_touch_grid_html() -> str:
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no'>"
            "<title>Touch Matrix Test</title><style>"
            "* {box-sizing:border-box;margin:0;padding:0;touch-action:none;user-select:none;}"
            "body {background:#121212;color:#fff;font-family:sans-serif;width:100vw;height:100vh;overflow:hidden;display:flex;flex-direction:column;}"
            "#header {padding:10px 14px;background:#1B1B26;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;font-size:13px;}"
            "#status {font-weight:bold;color:#00FFAA;}"
            ".btn {background:#37474F;color:#fff;border:none;padding:6px 14px;border-radius:4px;font-weight:bold;cursor:pointer;}"
            "#grid {flex:1;display:grid;grid-template-columns:repeat(10,1fr);grid-template-rows:repeat(18,1fr);gap:2px;padding:3px;background:#000;}"
            ".box {background:#21252B;border-radius:2px;}"
            ".box.touched {background:#00E676;}"
            "#modal {display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.88);flex-direction:column;justify-content:center;align-items:center;z-index:99;text-align:center;}"
            "#modal.show {display:flex;}"
            "#modal h1 {color:#00E676;font-size:26px;margin-bottom:12px;}"
            "#modal p {color:#CCC;font-size:15px;margin-bottom:20px;line-height:1.5;}"
            "</style></head><body>"
            "<div id='header'>"
            "<div>👆 <b>UJI LAYAR SENTUH</b> | <span id='status'>Usap semua kotak (0%)</span></div>"
            "<button class='btn' onclick='reset()'>Reset</button>"
            "</div>"
            "<div id='grid'></div>"
            "<div id='modal'>"
            "<h1>🎉 100% LULUS UJI!</h1>"
            "<p>Semua area layar sentuh merespon sempurna.<br>Tidak ada titik mati (dead zone) atau ghost touch.</p>"
            "<button class='btn' style='background:#00C853;padding:10px 24px;font-size:16px;' onclick='reset()'>Tes Ulang</button>"
            "</div>"
            "<script>"
            "const grid=document.getElementById('grid'),stat=document.getElementById('status'),modal=document.getElementById('modal');"
            "const total=180;let count=0;const boxes=[];"
            "for(let i=0;i<total;i++){const b=document.createElement('div');b.className='box';grid.appendChild(b);boxes.push(b);}"
            "function hit(x,y){const el=document.elementFromPoint(x,y);"
            "if(el&&el.classList.contains('box')&&!el.classList.contains('touched')){"
            "el.classList.add('touched');count++;"
            "const pct=Math.round((count/total)*100);"
            "stat.innerText='Terisi '+count+'/'+total+' ('+pct+'%)';"
            "if(navigator.vibrate)navigator.vibrate(10);"
            "if(count>=total){modal.classList.add('show');if(navigator.vibrate)navigator.vibrate([40,60,40]);}"
            "}}"
            "function onPtr(e){if(e.touches){for(let i=0;i<e.touches.length;i++)hit(e.touches[i].clientX,e.touches[i].clientY);}"
            "else if(e.buttons>0||e.type==='pointerdown')hit(e.clientX,e.clientY);}"
            "grid.addEventListener('pointerdown',onPtr);"
            "grid.addEventListener('pointermove',onPtr);"
            "grid.addEventListener('touchstart',onPtr,{passive:true});"
            "grid.addEventListener('touchmove',onPtr,{passive:true});"
            "function reset(){boxes.forEach(b=>b.classList.remove('touched'));count=0;stat.innerText='Usap semua kotak (0%)';modal.classList.remove('show');}"
            "</script></body></html>"
        )

    def launch_touch_grid_test(self) -> tuple[bool, str]:
        """
        Launches the interactive HTML5 Touch Matrix Grid test on the device.
        Uses an embedded local HTTP server + ADB reverse port forwarding to
        completely bypass Chrome's 'ERR_ACCESS_DENIED' on file:/// URLs.
        Also pushes local fallback and grants storage permissions.
        """
        html_code = self._get_touch_grid_html()

        # 1. Start embedded HTTP server on PC
        port = self._start_touch_http_server(html_code, base_port=8999)

        # 2. Reverse port forward: device localhost:port -> PC localhost:port
        rev_cmd = self.base_cmd + ["reverse", f"tcp:{port}", f"tcp:{port}"]
        run_cmd(rev_cmd, timeout=5)

        # Wake up screen
        self.shell("input keyevent 224 2>/dev/null")

        # 3. Launch HTTP URL on device (Bypasses ERR_ACCESS_DENIED 100%)
        http_url = f"http://localhost:{port}/touch_grid_test.html"
        self.shell(f"am start -a android.intent.action.VIEW -d '{http_url}' 2>/dev/null")

        # 4. Fallback: Also push local file & grant permissions
        remote_path = "/sdcard/Download/touch_grid_test.html"
        cache_dir = os.path.join(APP_DIR, "data")
        os.makedirs(cache_dir, exist_ok=True)
        local_html = os.path.join(cache_dir, "touch_grid_test.html")
        try:
            with open(local_html, "w", encoding="utf-8") as f:
                f.write(html_code)
            run_cmd(self.base_cmd + ["push", local_html, remote_path], timeout=6)
        except Exception:
            pass

        # Auto-grant storage to Chrome & HTMLViewer just in case
        self.shell("pm grant com.android.chrome android.permission.READ_EXTERNAL_STORAGE 2>/dev/null")
        self.shell("appops set com.android.chrome MANAGE_EXTERNAL_STORAGE allow 2>/dev/null")

        return True, f"Papan kisi sentuh interaktif (Matrix Grid) dibuka via server lokal ({http_url})!\nAkses ditolak teratasi."

    def detect_device_brand(self) -> str:
        """Detects manufacturer or brand of connected device."""
        brand = (self.shell("getprop ro.product.brand 2>/dev/null") or "").strip().lower()
        manuf = (self.shell("getprop ro.product.manufacturer 2>/dev/null") or "").strip().lower()
        combined = f"{brand} {manuf}"
        if any(b in combined for b in ["xiaomi", "redmi", "poco"]):
            return "xiaomi"
        elif "samsung" in combined:
            return "samsung"
        elif any(b in combined for b in ["oppo", "realme", "oneplus"]):
            return "oppo"
        elif "vivo" in combined or "iqoo" in combined:
            return "vivo"
        elif any(b in combined for b in ["infinix", "tecno", "itel", "transsion"]):
            return "transsion"
        return "universal"

    def launch_factory_touch_test(self, target_brand="auto") -> tuple[bool, str]:
        """
        Launches manufacturer hardware diagnostic test screen
        (Xiaomi CIT, Samsung *#0*#, Oppo EngineerMode, Vivo Factory, etc.).
        Uses both broadcast secret codes and telephony dialer intents to bypass
        'Permission Denial' on unexported CIT activities.
        """
        if not target_brand or target_brand == "auto":
            brand = self.detect_device_brand()
        else:
            brand = target_brand.lower()

        self.shell("input keyevent 224 2>/dev/null")  # wake screen

        executed_info = []

        if brand == "xiaomi":
            # 1. Telephony Secret Code Broadcast (Bypasses Permission Denial on CIT)
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://6484 2>/dev/null")
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://64663 2>/dev/null")
            # 2. Direct activities (for rooted / older MIUI)
            self.shell("am start -n com.miui.cit/.citActivity 2>/dev/null")
            self.shell("am start -n com.miui.cit/com.miui.cit.MainActivity 2>/dev/null")
            self.shell("am start -n com.miui.cit/.MainActivity 2>/dev/null")
            self.shell("am start -n com.miui.cit/.TestListActivity 2>/dev/null")
            # 3. Dialer fallback (buka dialer dengan nomor *#*#6484#*#*)
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%23*%236484%23*%23*' 2>/dev/null")
            executed_info.append("Xiaomi CIT (*#*#6484#*#*)")

        elif brand == "samsung":
            # 1. Secret code broadcast
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://0 2>/dev/null")
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://7353 2>/dev/null")
            # 2. ServiceMode activities
            self.shell("am start -a android.intent.action.MAIN -n com.sec.android.app.servicemodeapp/.ServiceModeApp 2>/dev/null")
            self.shell("am start -a android.intent.action.MAIN -n com.sec.android.RilServiceModeApp/.ServiceModeApp 2>/dev/null")
            # 3. Dialer fallback
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%230*%23' 2>/dev/null")
            executed_info.append("Samsung Hardware Test (*#0*# / *#7353#)")

        elif brand == "oppo":
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://899 2>/dev/null")
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://808 2>/dev/null")
            self.shell("am start -n com.oppo.engineermode/.EngineerMode 2>/dev/null")
            self.shell("am start -n com.coloros.engineermode/.EngineerMode 2>/dev/null")
            self.shell("am start -n com.oplus.engineermode/.EngineerMode 2>/dev/null")
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%23899%23' 2>/dev/null")
            executed_info.append("Oppo/Realme Engineer Mode (*#899#)")

        elif brand == "vivo":
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://558 2>/dev/null")
            self.shell("am start -n com.bbk.engineermode/.EngineerMode 2>/dev/null")
            self.shell("am start -n com.vivo.engineermode/.EngineerMode 2>/dev/null")
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%23558%23' 2>/dev/null")
            executed_info.append("Vivo Factory Test (*#558#)")

        elif brand == "transsion":
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://9646633 2>/dev/null")
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://83781 2>/dev/null")
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%23*%2383781%23*%23*' 2>/dev/null")
            executed_info.append("Infinix/Tecno Engineer Mode (*#*#83781#*#*)")

        else:
            # Universal Android testing
            self.shell("am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://4636 2>/dev/null")
            self.shell("am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.settings/.TestingSettings 2>/dev/null")
            self.shell("am start -a android.intent.action.DIAL -d 'tel:*%23*%234636%23*%23*' 2>/dev/null")
            executed_info.append("Android Testing Menu (*#*#4636#*#*)")

        return True, f"Menu tes pabrik [{', '.join(executed_info)}] telah dikirim ke perangkat!"

    def start_touch_listener(self, on_touch_data):
        """
        Listens to touch digitizer events (X, Y coordinates, touch pressure)
        via getevent in a background thread and dispatches live telemetry to PC.
        on_touch_data(x: int, y: int, is_down: bool, event_count: int)
        """
        if self._touch_listening:
            return

        self._touch_listening = True
        self.last_touch_error = None

        def worker():
            cmd = self.base_cmd + ["shell", "getevent", "-l"]
            try:
                self._touch_listener_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                cur_x = 0
                cur_y = 0
                is_down = False
                event_cnt = 0

                for line in self._touch_listener_proc.stdout:
                    if not self._touch_listening:
                        break
                    line = line.strip().lower()
                    if "abs_mt_position_x" in line:
                        parts = line.split()
                        val_hex = parts[-1]
                        try:
                            cur_x = int(val_hex, 16)
                            event_cnt += 1
                        except ValueError:
                            pass
                    elif "abs_mt_position_y" in line:
                        parts = line.split()
                        val_hex = parts[-1]
                        try:
                            cur_y = int(val_hex, 16)
                            event_cnt += 1
                        except ValueError:
                            pass
                    elif "btn_touch" in line:
                        if "down" in line:
                            is_down = True
                        elif "up" in line:
                            is_down = False
                        event_cnt += 1

                    if "syn_report" in line and (cur_x > 0 or cur_y > 0):
                        on_touch_data(cur_x, cur_y, is_down, event_cnt)
            except Exception as e:
                self.last_touch_error = str(e)
            finally:
                self._touch_listening = False

        self._touch_listener_thread = threading.Thread(target=worker, daemon=True)
        self._touch_listener_thread.start()

    def stop_touch_listener(self):
        self._touch_listening = False
        if self._touch_listener_proc:
            try:
                self._touch_listener_proc.terminate()
            except Exception:
                pass
            self._touch_listener_proc = None
        if self._touch_listener_thread and self._touch_listener_thread.is_alive():
            self._touch_listener_thread.join(timeout=1.5)
        self._touch_listener_thread = None
