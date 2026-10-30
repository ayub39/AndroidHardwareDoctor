import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DIR


class ReportGenerator:
    @staticmethod
    def generate_text_report(scan_data: dict) -> str:
        t = time.strftime("%d-%m-%Y %H:%M:%S")
        lines = []
        lines.append("=" * 60)
        lines.append("        LAPORAN DIAGNOSA HARDWARE ANDROID (USB SCAN)")
        lines.append(f"        Waktu Scan: {t}")
        lines.append("=" * 60)

        # Mode ADB
        if "device_info" in scan_data:
            dev = scan_data["device_info"]
            lines.append("\n[1. INFORMASI PERANGKAT]")
            lines.append(f"  • Merk & Model     : {dev.get('brand')} {dev.get('model')}")
            lines.append(f"  • Pabrikan / Chip  : {dev.get('manufacturer')} | Chipset: {dev.get('chipset')}")
            lines.append(f"  • Versi Android    : {dev.get('android_version')} (Patch: {dev.get('security_patch')})")
            lines.append(f"  • RAM Total / Free : {dev.get('ram_total')} / Bebas: {dev.get('ram_available')}")
            lines.append(f"  • Akun Google      : {dev.get('google_accounts', '-')}")
            lines.append(f"  • Serial Number    : {dev.get('serial')}")
            lines.append(f"  • Status Baseband  : {dev.get('baseband_status')}")
            lines.append(f"  • No. IMEI         : {dev.get('imei1', '-')} | IMEI 2: {dev.get('imei2', '-')}")
            lines.append(f"  • Diagnosa Sinyal  : {dev.get('signal_diagnosis', '-')}")

            # Battery
            bat = scan_data.get("battery", {})
            lines.append("\n[2. BATERAI & SISTEM DAYA (IC CHARGE/PMIC)]")
            lines.append(f"  • Level / Tegangan : {bat.get('level')} | {bat.get('voltage')}")
            lines.append(f"  • Kesehatan Baterai: {bat.get('health_pct', 'Unknown')} ({bat.get('health', '-')})")
            lines.append(f"  • Siklus Pengecasan: {bat.get('cycle_count', '-')}")
            lines.append(f"  • Kapasitas Saat Ini: {bat.get('current_capacity', '-')} (Asli Pabrik: {bat.get('design_capacity', '-')})")
            lines.append(f"  • Penurunan Daya   : {bat.get('capacity_loss', '-')}")
            lines.append(f"  • Suhu / Charger   : {bat.get('temperature')} | {bat.get('charger')}")
            lines.append(f"  • Evaluasi Teknis  : [{bat.get('status_flag', 'OK')}] {bat.get('note')}")

            # Storage eMMC / UFS
            stor = scan_data.get("storage", {})
            lines.append("\n[3. KESEHATAN PENYIMPANAN (eMMC / UFS MEMORY)]")
            lines.append(f"  • Tingkat Keausan  : {stor.get('wear_percentage')}")
            lines.append(f"  • Cadangan Blok    : {stor.get('pre_eol_status')}")
            lines.append(f"  • Uji Baca/Tulis   : {stor.get('io_health')}")
            lines.append(f"  • Kapasitas / Sisa : {stor.get('free_space')}")
            for n in stor.get("notes", []):
                lines.append(f"    * {n}")

            # Display & Touch
            disp = scan_data.get("display", {})
            touch = scan_data.get("touchscreen", {})
            lines.append("\n[4. DISPLAY & TOUCHSCREEN CONTROLLER]")
            lines.append(f"  • Resolusi Display : {disp.get('resolution')} ({disp.get('density')})")
            lines.append(f"  • IC Controller    : {touch.get('controller')}")
            lines.append(f"  • Status Touch     : {touch.get('note')}")

            # Cameras & Sensors
            cam = scan_data.get("cameras", {})
            sen = scan_data.get("sensors", {})
            lines.append("\n[5. KAMERA & SENSOR]")
            lines.append(f"  • Modul Kamera     : {cam.get('count')} terdeteksi ({cam.get('devices')})")
            lines.append(f"  • Status Kamera    : {cam.get('note')}")
            lines.append(f"  • Sensor Aktif     : {sen.get('detected_count')} unit ({sen.get('sensors')})")

            # Connectivity
            conn = scan_data.get("connectivity", {})
            lines.append("\n[6. KONEKTIVITAS & WI-FI]")
            lines.append(f"  • Status Wi-Fi MAC : {conn.get('wifi_status')}")

            # Kernel Faults
            faults = scan_data.get("hardware_faults", [])
            lines.append("\n[7. INDIKASI KERUSAKAN HARDWARE / IC (LOG KERNEL)]")
            if faults:
                for f in faults:
                    lines.append(f"  [!] {f.get('category')}")
                    lines.append(f"      Log: {f.get('log')}")
            else:
                lines.append("  [OK] Tidak ditemukan error bus I2C/SPI fatal pada log kernel terbaru.")

        elif "mode" in scan_data and "FASTBOOT" in scan_data["mode"]:
            lines.append("\n[STATUS: PERANGKAT DALAM MODE FASTBOOT / BOOTLOADER]")
            lines.append(f"  • Product / Model  : {scan_data.get('product')}")
            lines.append(f"  • Bootloader Ver   : {scan_data.get('bootloader_version')}")
            lines.append(f"  • Status Lock      : Bootloader Unlocked = {scan_data.get('unlocked')}")
            lines.append(f"  • Tegangan Baterai : {scan_data.get('battery_voltage')}")
            for n in scan_data.get("notes", []):
                lines.append(f"    * {n}")

        lines.append("\n" + "=" * 60)
        lines.append("         * Laporan dicetak otomatis oleh Android Hardware Doctor *")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def save_report_to_file(report_text: str, filename: str = None) -> str:
        reports_dir = os.path.join(APP_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        if not filename:
            filename = os.path.join(reports_dir, f"diag_report_{int(time.time())}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_text)
            return filename
        except Exception as e:
            return ""
