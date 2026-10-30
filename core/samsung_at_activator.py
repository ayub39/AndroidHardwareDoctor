import os
import sys
import time
import subprocess
import serial
import serial.tools.list_ports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, run_cmd


class SamsungAdbActivator:
    """
    1-Click Samsung ADB Activation Engine using Modem AT-Commands over USB COM Port.
    Inspired by technician tools (SamFW FRP Tool / Chimera / UnlockTool).
    Communicates directly with the 'SAMSUNG Mobile USB Modem' driver.
    """

    @staticmethod
    def get_samsung_modem_ports() -> list:
        """Finds all COM ports associated with Samsung Mobile USB Modem."""
        samsung_ports = []
        try:
            for port in serial.tools.list_ports.comports():
                desc = (port.description or "").lower()
                hwid = (port.hwid or "").lower()
                # VID 04E8 is Samsung Electronics
                if "samsung" in desc or "samsung" in hwid or "04e8" in hwid or "modem" in desc:
                    samsung_ports.append(port)
        except Exception:
            pass
        return samsung_ports

    def __init__(self, serial_no=None):
        self.adb = get_adb_path()
        self.serial_no = serial_no

    def execute_at_command(self, ser, cmd_str: str, wait_sec: float = 1.0) -> str:
        """Sends an AT command string to the modem port and reads back response."""
        try:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            payload = (cmd_str.strip() + "\r\n").encode("utf-8")
            ser.write(payload)
            time.sleep(wait_sec)
            out = b""
            while ser.in_waiting > 0:
                out += ser.read(ser.in_waiting)
                time.sleep(0.05)
            return out.decode("utf-8", errors="ignore").strip()
        except Exception as e:
            return f"ERR: {str(e)}"

    def activate_adb_modem(self, on_progress=None) -> tuple[bool, str]:
        """
        Executes the 1-click AT-command exploit sequence to force-enable
        USB debugging daemon on Samsung devices via MTP / Modem COM port.
        """
        if on_progress:
            on_progress("🔍 Memindai driver SAMSUNG Mobile USB Modem di Windows...")

        ports = self.get_samsung_modem_ports()
        if not ports:
            # Fallback: check all available COM ports if only 1-2 ports exist
            all_ports = list(serial.tools.list_ports.comports())
            candidate_ports = [p for p in all_ports if "com1" not in p.device.lower()]
            if not candidate_ports:
                return False, (
                    "❌ Driver SAMSUNG Mobile USB Modem tidak terdeteksi pada port COM!\n\n"
                    "Langkah Pengecekan:\n"
                    "1. Pastikan Driver Samsung USB sudah terinstal di Windows.\n"
                    "2. Hubungkan HP Samsung ke PC dalam posisi menyala normal (Mode MTP).\n"
                    "3. Jika layar masih bisa disentuh: Buka 'Panggilan Darurat' lalu ketik *#0*# untuk membuka Test Mode."
                )
            ports = candidate_ports

        target_port = ports[0]
        port_name = target_port.device
        port_desc = target_port.description

        if on_progress:
            on_progress(f"🔌 Menghubungkan ke modem Samsung pada {port_name} ({port_desc})...")

        ser = None
        # Try standard baudrates
        for baud in [115200, 9600]:
            try:
                ser = serial.Serial(port_name, baud, timeout=2)
                break
            except Exception:
                continue

        if not ser or not ser.is_open:
            return False, f"Gagal membuka port komunikasi serial pada {port_name}. Port mungkin sedang digunakan aplikasi lain."

        log_lines = []
        try:
            # 1. Handshake AT
            if on_progress:
                on_progress(f"📡 Mengirim sinyal Handshake AT ke {port_name}...")
            r_at = self.execute_at_command(ser, "AT", wait_sec=0.8)
            log_lines.append(f"AT -> {r_at}")

            # 2. Get Device Info
            r_info = self.execute_at_command(ser, "AT+DEVCONINFO", wait_sec=1.0)
            if "ERR" not in r_info and r_info:
                log_lines.append(f"INFO -> {r_info}")

            # 3. Exploit Sequences
            exploit_cmds = [
                ("AT+SWAT=1", "Mengaktifkan Software AT Mode..."),
                ("AT+ACTIVATE_ADB", "Memaksa peluncuran daemon ADB..."),
                ("AT+KICSO", "Mengalihkan konfigurasi USB ke MTP+ADB..."),
                ("AT+DUMP=1", "Memicu RIL Debugging..."),
                ("AT+FACTORST=0", "Inisialisasi Factory State...")
            ]

            for at_cmd, desc in exploit_cmds:
                if on_progress:
                    on_progress(f"⚡ {desc} ({at_cmd})")
                res = self.execute_at_command(ser, at_cmd, wait_sec=0.8)
                log_lines.append(f"{at_cmd} -> {res}")

        finally:
            try:
                ser.close()
            except Exception:
                pass

        # 4. Monitor ADB daemon for up to 15 seconds
        if on_progress:
            on_progress("⏳ Menunggu daemon ADB aktif pada perangkat (memindai 15 detik)...")

        adb_detected = False
        dev_serial = ""
        is_authorized = False

        for _ in range(15):
            time.sleep(1)
            try:
                proc = subprocess.run(
                    [self.adb, "devices"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
                for l in lines[1:]:
                    parts = l.split()
                    if len(parts) >= 2:
                        dev_serial = parts[0]
                        state = parts[1].lower()
                        if state == "device":
                            adb_detected = True
                            is_authorized = True
                            break
                        elif state == "unauthorized":
                            adb_detected = True
                            is_authorized = False
                            break
                if adb_detected:
                    break
            except Exception:
                pass

        if adb_detected:
            if is_authorized:
                return True, (
                    f"🎉 SUKSES BESAR! USB Debugging Berhasil Aktif!\n\n"
                    f"Perangkat Terdeteksi: {dev_serial} (Status: ONLINE / AUTHORIZED)\n\n"
                    f"Anda sekarang bisa langsung melakukan Penyelamatan Data, Backup Foto, WhatsApp, atau Mirroring Layar!"
                )
            else:
                return True, (
                    f"⚡ DAEMON ADB BERHASIL MENYALA!\n\n"
                    f"Perangkat Terdeteksi: {dev_serial} (Status: UNAUTHORIZED)\n\n"
                    f"Layar HP Samsung sekarang memunculkan jendela pop-up:\n"
                    f"'Izinkan Debugging USB? Kunci sidik jari RSA komputer...'\n\n"
                    f"👉 Centang kotak 'Selalu izinkan dari komputer ini' lalu klik OKE di layar HP!"
                )

        return False, (
            "⚠️ Perintah AT Exploit telah berhasil dikirim ke Modem Samsung, namun daemon ADB belum merespons.\n\n"
            "Penyebab Umum:\n"
            "1. Security Patch Samsung terbaru (akhir 2023 s/d 2026) sudah menambal celah AT Modem ini.\n"
            "2. Mode Panggilan Darurat: Jika layar masih bisa disentuh, buka Panggilan Darurat dan ketik *#0*# terlebih dahulu, lalu klik tombol ini lagi.\n"
            "3. Jika layar mati total pada patch baru: Gunakan trik pancingan LCD atau OTG keyboard."
        )
