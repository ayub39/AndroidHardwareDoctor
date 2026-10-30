import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.device_detector import DeviceDetector
from core.adb_scanner import AdbHardwareScanner
from core.fastboot_scanner import FastbootScanner
from core.report_generator import ReportGenerator
from core.hardware_tester import HardwareTester
from core.reboot_tools import RebootTools
from core.power_monitor import PowerMonitor
from core.screen_mirror import ScreenMirrorManager
from core.receipt_generator import ReceiptGenerator
from core.dead_phone_diagnoser import DeadPhoneDiagnoser
from core.service_database import ServiceDatabase
from core.flasher import FirmwareFlasher
from core.testpoint_db import TestPointDatabase
from core.power_on_db import PowerOnDatabase
from core.driver_helper import DriverHelper
from core.data_rescue import DataRescueManager
from core.frp_tools import FrpAndLockTools
from core.samsung_at_activator import SamsungAdbActivator
from config import get_adb_path, APP_DIR

# Modern Dark Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AndroidHardwareDoctorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Android Hardware Doctor Pro v2.0 - Stasiun Servis HP Mati & Hidup")
        self.geometry("1100x800")
        self.minsize(980, 700)

        self.current_device = None
        self.last_scan_data = None
        self.is_scanning = False
        self.monitoring_usb = True
        self.hardware_tester = None
        self.power_monitor = None
        self.screen_mirror = None
        self.reboot_tools = None
        self.flasher = None
        self.data_rescue = None
        self._last_detected_accounts = None
        self._device_lock = threading.Lock()

        # Handle window close gracefully
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Init Database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "service_records.db")
        self.db = ServiceDatabase(db_path=db_path)

        self._build_header()
        self._build_tabs()
        self._build_footer()

        # Background Daemons
        self.usb_thread = threading.Thread(target=self._monitor_usb_devices, daemon=True)
        self.usb_thread.start()

        self.power_thread = threading.Thread(target=self._monitor_live_power, daemon=True)
        self.power_thread.start()

    # -------------------------------------------------------------
    # 1. TOP HEADER & CONNECTION BADGE
    # -------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=10, fg_color="#181824")
        header.pack(fill="x", padx=15, pady=(10, 4))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=15, pady=8)

        title_lbl = ctk.CTkLabel(
            title_box, 
            text="⚡ ANDROID HARDWARE DOCTOR PRO", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00D2FF"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box, 
            text="Stasiun Diagnosa Terpadu: HP Mati Total (Matot/Konslet) & HP Hidup/Normal", 
            font=ctk.CTkFont(size=12),
            text_color="#A0A0B0"
        )
        sub_lbl.pack(anchor="w")

        self.conn_pill = ctk.CTkLabel(
            header,
            text="🔴 Menunggu Sambungan Kabel USB...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B6B",
            fg_color="#2A2030",
            corner_radius=20,
            padx=16,
            pady=8
        )
        self.conn_pill.pack(side="right", padx=15, pady=8)

    # -------------------------------------------------------------
    # 2. TABVIEW
    # -------------------------------------------------------------
    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10, fg_color="#13131A")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=4)

        self.tab_diag = self.tabview.add("🔍 HP Hidup")
        self.tab_dead = self.tabview.add("💀 HP Matot")
        self.tab_tp = self.tabview.add("📍 Test Point (TP)")
        self.tab_flash = self.tabview.add("⚡ Flashing")
        self.tab_driver = self.tabview.add("🔌 Driver USB")
        self.tab_tests = self.tabview.add("🛠️ Alat Uji")
        self.tab_reboot = self.tabview.add("🔄 Reboot")
        self.tab_mirror = self.tabview.add("📦 Data Rescue")
        self.tab_tickets = self.tabview.add("📋 Buku Servis")
        self.tab_receipt = self.tabview.add("📄 Cetak Nota")

        self._build_tab_diagnosa()
        self._build_tab_dead_phone()
        self._build_tab_testpoints()
        self._build_tab_flasher()
        self._build_tab_drivers()
        self._build_tab_tests()
        self._build_tab_reboot()
        self._build_tab_mirror()
        self._build_tab_tickets()
        self._build_tab_receipt()

    # -------------------------------------------------------------
    # TAB 1: HP HIDUP (ADB & FASTBOOT)
    # -------------------------------------------------------------
    def _build_tab_diagnosa(self):
        toolbar = ctk.CTkFrame(self.tab_diag, corner_radius=8, fg_color="#1E1E2F")
        toolbar.pack(fill="x", padx=10, pady=(4, 6))

        self.btn_scan = ctk.CTkButton(
            toolbar,
            text="🔍 MULAI SCAN HARDWARE LENGKAP",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#007ACC",
            hover_color="#005999",
            height=36,
            command=self.start_scan
        )
        self.btn_scan.pack(side="left", padx=10, pady=8)

        self.btn_save_txt = ctk.CTkButton(
            toolbar,
            text="💾 Simpan TXT",
            font=ctk.CTkFont(size=12),
            fg_color="#2D3250",
            hover_color="#424769",
            height=36,
            command=self.save_txt_report,
            state="disabled"
        )
        self.btn_save_txt.pack(side="left", padx=6, pady=8)

        btn_curr_guide = ctk.CTkButton(
            toolbar,
            text="📊 Kamus Arus USB",
            width=135,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#37474F",
            hover_color="#263238",
            command=self._show_usb_current_guide
        )
        btn_curr_guide.pack(side="right", padx=(0, 15), pady=8)

        self.lbl_live_power = ctk.CTkLabel(
            toolbar,
            text="⚡ Arus: -- mA | Voltase: -- V",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#FFAA00"
        )
        self.lbl_live_power.pack(side="right", padx=(0, 10), pady=8)

        scroll = ctk.CTkScrollableFrame(self.tab_diag, corner_radius=8, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=4)

        r1 = ctk.CTkFrame(scroll, fg_color="transparent")
        r1.pack(fill="x", pady=4)
        r1.columnconfigure((0, 1), weight=1, uniform="card_col")

        self.card_dev = self._create_card(r1, "📱 IDENTITAS PERANGKAT", 0, 0)
        self.card_bat = self._create_card(r1, "🔋 BATERAI & SISTEM DAYA", 0, 1)

        r2 = ctk.CTkFrame(scroll, fg_color="transparent")
        r2.pack(fill="x", pady=4)
        r2.columnconfigure((0, 1), weight=1, uniform="card_col")

        self.card_stor = self._create_card(r2, "💾 KESEHATAN MEMORI (eMMC / UFS)", 0, 0)
        self.card_periph = self._create_card(r2, "🖥️ DISPLAY, TOUCH IC & KAMERA", 0, 1)

        fault_frame = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#1B1B26")
        fault_frame.pack(fill="x", pady=6)
        
        lbl_f_title = ctk.CTkLabel(
            fault_frame,
            text="⚠️ ANALISIS KERUSAKAN IC & BUS HARDWARE (LOG KERNEL)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFAA00"
        )
        lbl_f_title.pack(anchor="w", padx=12, pady=(10, 4))

        self.txt_faults = ctk.CTkTextbox(
            fault_frame,
            height=120,
            fg_color="#0F0F15",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#E0E0E0"
        )
        self.txt_faults.pack(fill="x", padx=12, pady=(4, 12))
        self.txt_faults.insert("1.0", "Tekan 'MULAI SCAN HARDWARE LENGKAP' untuk membaca diagnosa.")
        self.txt_faults.configure(state="disabled")

    # -------------------------------------------------------------
    # TAB 2: HP MATI TOTAL (HARDWARE TRIAGE)
    # -------------------------------------------------------------
    def _build_tab_dead_phone(self):
        container = ctk.CTkScrollableFrame(self.tab_dead, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=10)

        # Header Info
        header_box = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        header_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_box,
            text="💀 PANDUAN DIAGNOSA HP MATI TOTAL (MATOT / KONSLET)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FF5555"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            header_box,
            text="Gunakan modul ini saat HP pasien mati total, layar gelap, atau tidak ada getaran sama sekali saat dicolok.",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0B0"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # Input Area: Pilih Respon Arus Ampere
        select_box = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        select_box.pack(fill="x", pady=6)

        ctk.CTkLabel(
            select_box,
            text="1. Pilih Respon Arus USB (Angka di USB Doctor / Ammeter):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(12, 6))

        self.ampere_options = [
            ("0.00A", "⚡ 0.00 A (Nol Total / Listrik Sama Sekali Tidak Masuk)"),
            ("0.01A-0.08A", "❄️ 0.01 A - 0.08 A Diam (Arus Dingin / CPU Belum Bangkit)"),
            ("0.10A-0.28A", "🌡️ 0.10 A - 0.28 A Gantung (Arus Hangat / Stuck Boot)"),
            ("0.40A-0.90A", "💾 0.40 A - 0.90 A Stuck (CPU Hidup / eMMC-UFS Rusak atau Lepas)"),
            ("PULSE_LOOP", "🔄 Arus Berdenyut (Loop: 0.0A -> 0.3A -> 0.0A Berulang)"),
            ("SHORT_OVER_1A", "🚨 > 1.0 A Langsung (KONSLET TOTAL / SHORT Jalur VPH_PWR / VDD)")
        ]

        self.selected_ampere = tk.StringVar(value="0.00A")
        for val, label in self.ampere_options:
            r = ctk.CTkRadioButton(
                select_box,
                text=label,
                value=val,
                variable=self.selected_ampere,
                font=ctk.CTkFont(size=12),
                command=self._on_dead_diagnose_calculate
            )
            r.pack(anchor="w", padx=25, pady=4)

        btn_calc = ctk.CTkButton(
            select_box,
            text="🔍 ANALISIS KERUSAKAN HP MATI SEKARANG",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            height=36,
            command=self._on_dead_diagnose_calculate
        )
        btn_calc.pack(anchor="w", padx=15, pady=(12, 15))

        # Card 2: Battery Voltage Doctor & Jump Start Guide
        bat_box = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        bat_box.pack(fill="x", pady=6)

        ctk.CTkLabel(
            bat_box,
            text="2. 🔋 Dokter Baterai: Cek Hasil Tegangan Voltmeter & Panduan Suntik",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00FFAA"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            bat_box,
            text="Masukkan angka voltase yang terbaca di multimeter lu (Contoh: 3.66). Tool akan menganalisis apakah baterai kuat booting atau wajib disuntik!",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0B0"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        row_v = ctk.CTkFrame(bat_box, fg_color="transparent")
        row_v.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(row_v, text="Tegangan Baterai (Volt):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.entry_bat_volt = ctk.CTkEntry(row_v, width=120, placeholder_text="Contoh: 3.66")
        self.entry_bat_volt.insert(0, "3.66")
        self.entry_bat_volt.pack(side="left", padx=10)

        ctk.CTkButton(
            row_v,
            text="🔍 ANALISIS TEGANGAN BATERAI",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#007ACC",
            command=self._on_evaluate_battery_volt
        ).pack(side="left", padx=6)

        # Voltage Result Card
        self.volt_res_box = ctk.CTkFrame(bat_box, corner_radius=6, fg_color="#12121C")
        self.volt_res_box.pack(fill="x", padx=15, pady=(8, 15))

        self.lbl_volt_badge = ctk.CTkLabel(
            self.volt_res_box,
            text="[ HASIL EVALUASI BATERAI ]",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFAA00"
        )
        self.lbl_volt_badge.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_volt_desc = ctk.CTkLabel(
            self.volt_res_box,
            text="Keterangan kondisi baterai...",
            font=ctk.CTkFont(size=12),
            text_color="#D0D0E0",
            wraplength=820,
            justify="left"
        )
        self.lbl_volt_desc.pack(anchor="w", padx=12, pady=2)

        self.txt_volt_sol = ctk.CTkLabel(
            self.volt_res_box,
            text="Rekomendasi teknisi...",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#00FFAA",
            justify="left"
        )
        self.txt_volt_sol.pack(anchor="w", padx=12, pady=(4, 12))

        # Result Area
        self.dead_res_frame = ctk.CTkFrame(container, corner_radius=8, fg_color="#181824")
        self.dead_res_frame.pack(fill="x", pady=8)

        self.lbl_dead_title = ctk.CTkLabel(
            self.dead_res_frame,
            text="HASIL ANALISIS DIAGNOSA KERUSAKAN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFAA00"
        )
        self.lbl_dead_title.pack(anchor="w", padx=15, pady=(12, 4))

        self.lbl_dead_suspect = ctk.CTkLabel(
            self.dead_res_frame,
            text="Komponen Tersangka: -",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FF5555"
        )
        self.lbl_dead_suspect.pack(anchor="w", padx=15, pady=2)

        self.lbl_dead_desc = ctk.CTkLabel(
            self.dead_res_frame,
            text="Penjelasan teknis akan muncul di sini.",
            font=ctk.CTkFont(size=12),
            text_color="#B0B0C0",
            wraplength=850,
            justify="left"
        )
        self.lbl_dead_desc.pack(anchor="w", padx=15, pady=4)

        self.lbl_dead_chipset = ctk.CTkLabel(
            self.dead_res_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00FFAA",
            wraplength=850,
            justify="left"
        )
        self.lbl_dead_chipset.pack(anchor="w", padx=15, pady=4)

        # Probing Checklist
        ctk.CTkLabel(
            self.dead_res_frame,
            text="📐 Langkah Pengukuran Multimeter & Solusi (Borneo Guide):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(8, 4))

        self.txt_dead_probing = ctk.CTkLabel(
            self.dead_res_frame,
            text="-",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#E0E0E0",
            justify="left"
        )
        self.txt_dead_probing.pack(anchor="w", padx=15, pady=(0, 15))

        # Initial trigger
        self._on_dead_diagnose_calculate()
        self._on_evaluate_battery_volt()

    def _on_evaluate_battery_volt(self):
        v_str = self.entry_bat_volt.get().strip().replace(",", ".")
        try:
            val = float(v_str)
        except ValueError:
            messagebox.showwarning("Input Salah", "Masukkan angka voltase yang valid (Contoh: 3.66)!")
            return

        res = DeadPhoneDiagnoser.evaluate_battery_voltage(val)
        self.lbl_volt_badge.configure(text=f"STATUS: {res['badge']}", text_color=res["color"])
        self.lbl_volt_desc.configure(text=f"Analisa: {res['diagnosis']}")
        self.txt_volt_sol.configure(text=f"Rekomendasi Teknisi:\n{res['solution']}")

    def _on_dead_diagnose_calculate(self):
        amp_key = self.selected_ampere.get()
        usb_mode = "DISCONNECTED"
        if self.current_device:
            usb_mode = self.current_device.get("mode", "DISCONNECTED")

        diag = DeadPhoneDiagnoser.diagnose_dead_phone(ampere_key=amp_key, usb_mode=usb_mode)

        self.lbl_dead_title.configure(text=f"HASIL ANALISIS: {diag['title']}")
        self.lbl_dead_suspect.configure(text=f"🎯 Komponen Tersangka: {diag['primary_suspect']}")
        self.lbl_dead_desc.configure(text=f"Keterangan Teknis: {diag['explanation']}")
        self.lbl_dead_chipset.configure(text=diag['chipset_diagnosis'])
        self.txt_dead_probing.configure(text="\n".join(diag['probing_points']))

    # -------------------------------------------------------------
    # TAB 3: BUKU KASUS SERVIS KONTER (DATABASE PASIEN)
    # -------------------------------------------------------------
    def _build_tab_tickets(self):
        container = ctk.CTkFrame(self.tab_tickets, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top Bar (Search & Filter)
        top_bar = ctk.CTkFrame(container, fg_color="#1B1B26")
        top_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(top_bar, text="🔍 Cari Pasien:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(12, 6), pady=8)

        self.entry_search = ctk.CTkEntry(top_bar, placeholder_text="Nama / No. HP / Model HP...", width=220)
        self.entry_search.pack(side="left", padx=4, pady=8)
        self.entry_search.bind("<Return>", lambda e: self._refresh_tickets())

        ctk.CTkButton(top_bar, text="Cari", width=70, fg_color="#007ACC", command=self._refresh_tickets).pack(side="left", padx=6, pady=8)

        ctk.CTkLabel(top_bar, text="Filter Status:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 6), pady=8)
        self.cb_filter_status = ctk.CTkComboBox(
            top_bar,
            values=["SEMUA", "MASUK", "DIKERJAKAN", "TUNGGU_PART", "SELESAI", "DIAMBIL"],
            width=130,
            command=lambda v: self._refresh_tickets()
        )
        self.cb_filter_status.set("SEMUA")
        self.cb_filter_status.pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            top_bar,
            text="➕ Tambah Servis Baru",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self._open_new_ticket_modal
        ).pack(side="right", padx=12, pady=8)

        # Tickets Scrollable List
        self.ticket_scroll = ctk.CTkScrollableFrame(container, corner_radius=8, fg_color="#101018")
        self.ticket_scroll.pack(fill="both", expand=True)

        self._refresh_tickets()

    def _refresh_tickets(self):
        for widget in self.ticket_scroll.winfo_children():
            widget.destroy()

        q = self.entry_search.get().strip() if hasattr(self, 'entry_search') else ""
        status_filter = self.cb_filter_status.get() if hasattr(self, 'cb_filter_status') else "SEMUA"

        if q:
            records = self.db.search_tickets(q)
        else:
            records = self.db.get_all_tickets(filter_status=status_filter)

        if not records:
            empty_lbl = ctk.CTkLabel(
                self.ticket_scroll,
                text="Belum ada data servis pasien. Klik '+ Tambah Servis Baru' untuk mencatat pasien konter.",
                font=ctk.CTkFont(size=13),
                text_color="#707080"
            )
            empty_lbl.pack(pady=40)
            return

        for r in records:
            card = ctk.CTkFrame(self.ticket_scroll, corner_radius=8, fg_color="#1A1A26")
            card.pack(fill="x", padx=8, pady=5)

            # Row 1: Ticket No, Date, Status
            r1 = ctk.CTkFrame(card, fg_color="transparent")
            r1.pack(fill="x", padx=12, pady=(10, 2))

            t_no = ctk.CTkLabel(r1, text=f"🏷️ {r['ticket_no']}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF")
            t_no.pack(side="left")

            t_date = ctk.CTkLabel(r1, text=f"({r['created_at']})", font=ctk.CTkFont(size=11), text_color="#888")
            t_date.pack(side="left", padx=8)

            # Status Badge color
            st_color = "#C62828" if r['status'] == "MASUK" else ("#E65100" if r['status'] == "DIKERJAKAN" else ("#7B1FA2" if r['status'] == "TUNGGU_PART" else "#2E7D32"))
            st_badge = ctk.CTkLabel(r1, text=f"[{r['status']}]", font=ctk.CTkFont(size=12, weight="bold"), text_color=st_color)
            st_badge.pack(side="right")

            # Row 2: Customer & Device
            r2 = ctk.CTkFrame(card, fg_color="transparent")
            r2.pack(fill="x", padx=12, pady=2)
            c_info = ctk.CTkLabel(r2, text=f"👤 {r['customer_name']} ({r['customer_phone']})  |  📱 {r['device_model']} [{r['condition_type']}]", font=ctk.CTkFont(size=13, weight="bold"), text_color="#FFF")
            c_info.pack(side="left")

            # Row 3: Complaint & Suspected
            r3 = ctk.CTkFrame(card, fg_color="transparent")
            r3.pack(fill="x", padx=12, pady=2)
            diag_str = f"Keluhan: {r['complaint']} | Indikasi: {r['suspected_ic'] or '-'} | Biaya: {r['estimated_cost'] or '-'}"
            c_diag = ctk.CTkLabel(r3, text=diag_str, font=ctk.CTkFont(size=12), text_color="#A0A0B0")
            c_diag.pack(side="left")

            # Row 4: Action Buttons
            r4 = ctk.CTkFrame(card, fg_color="transparent")
            r4.pack(fill="x", padx=12, pady=(4, 10))

            btn_dikerjakan = ctk.CTkButton(r4, text="Dikerjakan", width=90, height=26, fg_color="#E65100", command=lambda t=r['ticket_no']: self._update_ticket_status(t, "DIKERJAKAN"))
            btn_dikerjakan.pack(side="left", padx=2)

            btn_selesai = ctk.CTkButton(r4, text="Selesai", width=80, height=26, fg_color="#2E7D32", command=lambda t=r['ticket_no']: self._update_ticket_status(t, "SELESAI"))
            btn_selesai.pack(side="left", padx=2)

            btn_diambil = ctk.CTkButton(r4, text="Diambil", width=80, height=26, fg_color="#1565C0", command=lambda t=r['ticket_no']: self._update_ticket_status(t, "DIAMBIL"))
            btn_diambil.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(r4, text="Hapus", width=70, height=26, fg_color="#424242", hover_color="#C62828", command=lambda t=r['ticket_no']: self._delete_ticket(t))
            btn_del.pack(side="right", padx=2)

    def _update_ticket_status(self, ticket_no, new_status):
        self.db.update_status(ticket_no, new_status)
        self._refresh_tickets()

    def _delete_ticket(self, ticket_no):
        if messagebox.askyesno("Hapus Tiket", f"Yakin ingin menghapus catatan servis {ticket_no}?"):
            self.db.delete_ticket(ticket_no)
            self._refresh_tickets()

    def _open_new_ticket_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Tambah Pasien Servis Baru")
        modal.geometry("520x580")
        modal.grab_set()

        ctk.CTkLabel(modal, text="Form Pasien Servis Konter", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00D2FF").pack(pady=12)

        f = ctk.CTkFrame(modal, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25)

        e_name = self._create_modal_field(f, "Nama Pelanggan:")
        e_phone = self._create_modal_field(f, "No. WhatsApp / HP:")
        e_model = self._create_modal_field(f, "Tipe HP (Contoh: Redmi Note 10):")
        
        ctk.CTkLabel(f, text="Kondisi HP:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(4, 2))
        cb_cond = ctk.CTkComboBox(f, values=["Mati Total (Matot / Konslet)", "Hidup Normal", "Bootloop / Restart", "Layar Pecah / Gelap", "Masuk Air"])
        cb_cond.pack(fill="x", pady=(0, 6))

        e_complaint = self._create_modal_field(f, "Keluhan Awal:")
        e_suspect = self._create_modal_field(f, "Indikasi Kerusakan / IC Tersangka:")
        e_cost = self._create_modal_field(f, "Estimasi Biaya (Rp):")

        # Autofill model if device connected
        if self.current_device:
            e_model.insert(0, self.current_device.get("model", ""))

        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showwarning("Data Kurang", "Nama pelanggan harus diisi!", parent=modal)
                return
            t_no = self.db.add_ticket(
                customer_name=name,
                customer_phone=e_phone.get().strip(),
                device_model=e_model.get().strip(),
                condition_type=cb_cond.get(),
                complaint=e_complaint.get().strip(),
                suspected_ic=e_suspect.get().strip(),
                estimated_cost=e_cost.get().strip(),
                status="MASUK"
            )
            messagebox.showinfo("Berhasil", f"Tiket servis {t_no} berhasil disimpan!", parent=modal)
            modal.destroy()
            self._refresh_tickets()

        ctk.CTkButton(modal, text="💾 Simpan ke Buku Servis", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#007ACC", height=38, command=save).pack(pady=15)

    def _create_modal_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(4, 2))
        e = ctk.CTkEntry(parent, height=30)
        e.pack(fill="x", pady=(0, 6))
        return e

    # -------------------------------------------------------------
    # TAB: TEST POINT & FORCE POWER-ON DATABASE
    # -------------------------------------------------------------
    def _build_tab_testpoints(self):
        container = ctk.CTkFrame(self.tab_tp, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=8)

        # Header bar with mode switcher
        hdr = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        hdr.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            hdr,
            text="📍 TEST POINT EDL / BROM & JUMPER FORCE POWER-ON (SEMUA BRAND)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            hdr,
            text="Solusi teknisi: (1) Menyalakan HP mati tanpa tombol power agar masuk ADB, dan (2) Test point unbrick Qualcomm 9008 / MediaTek BROM.",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0B0"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        # Mode Segmented Control
        self.seg_tp_mode = ctk.CTkSegmentedButton(
            hdr,
            values=[
                "⚡ FORCE POWER-ON TANPA TOMBOL (AKSES ADB)",
                "📍 TEST POINT EDL 9008 / BROM (UNBRICK)"
            ],
            font=ctk.CTkFont(size=12, weight="bold"),
            selected_color="#007ACC",
            selected_hover_color="#005999",
            command=self._on_tp_mode_changed
        )
        self.seg_tp_mode.set("⚡ FORCE POWER-ON TANPA TOMBOL (AKSES ADB)")
        self.seg_tp_mode.pack(fill="x", padx=15, pady=(0, 10))

        # Content frames container
        self.tp_content_area = ctk.CTkFrame(container, fg_color="transparent")
        self.tp_content_area.pack(fill="both", expand=True)

        # ---------------------------------------------------------
        # FRAME 1: FORCE POWER-ON TANPA TOMBOL (AKSES ADB)
        # ---------------------------------------------------------
        self.frame_tp_poweron = ctk.CTkFrame(self.tp_content_area, fg_color="transparent")

        # Fastboot Live Action Bar
        act_bar = ctk.CTkFrame(self.frame_tp_poweron, corner_radius=8, fg_color="#221C16", border_width=1, border_color="#FF9800")
        act_bar.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            act_bar,
            text="⚡ TOOL EKSEKUSI CEPAT FASTBOOT: (Colok HP ke PC sambil tahan Volume Bawah)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFA726"
        ).pack(side="left", padx=(12, 10), pady=8)

        ctk.CTkButton(
            act_bar,
            text="🚀 Fastboot Reboot ke Normal",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#007ACC",
            hover_color="#005999",
            command=self._action_fastboot_reboot
        ).pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            act_bar,
            text="⚡ Setel Auto-Boot Saat Cas",
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self._action_fastboot_autocharge
        ).pack(side="left", padx=4, pady=8)

        self.lbl_pwr_action_status = ctk.CTkLabel(act_bar, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color="#00FFAA")
        self.lbl_pwr_action_status.pack(side="left", padx=10, pady=8)

        # 2-Column body for Force Power-On
        pwr_body = ctk.CTkFrame(self.frame_tp_poweron, fg_color="transparent")
        pwr_body.pack(fill="both", expand=True)
        pwr_body.columnconfigure(0, weight=1)
        pwr_body.columnconfigure(1, weight=2)
        pwr_body.rowconfigure(0, weight=1)

        self.pwr_brand_list_scroll = ctk.CTkScrollableFrame(pwr_body, corner_radius=8, fg_color="#14141E")
        self.pwr_brand_list_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=2)

        self.pwr_detail_scroll = ctk.CTkScrollableFrame(pwr_body, corner_radius=8, fg_color="#14141E")
        self.pwr_detail_scroll.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=2)

        # ---------------------------------------------------------
        # FRAME 2: TEST POINT UNBRICK (EDL 9008 & BROM)
        # ---------------------------------------------------------
        self.frame_tp_unbrick = ctk.CTkFrame(self.tp_content_area, fg_color="transparent")

        filter_bar = ctk.CTkFrame(self.frame_tp_unbrick, fg_color="#181824", corner_radius=8)
        filter_bar.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(filter_bar, text="Merk:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(12, 6), pady=8)
        self.cb_tp_brand = ctk.CTkComboBox(
            filter_bar,
            values=TestPointDatabase.get_all_brands(),
            width=140,
            command=lambda v: self._refresh_testpoint_list()
        )
        self.cb_tp_brand.set("SEMUA MERK")
        self.cb_tp_brand.pack(side="left", padx=4, pady=8)

        ctk.CTkLabel(filter_bar, text="Cari Model:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 6), pady=8)
        self.entry_tp_search = ctk.CTkEntry(filter_bar, placeholder_text="Contoh: Note 8, Y12, A3s, A10s, POCO...", width=240)
        self.entry_tp_search.pack(side="left", padx=4, pady=8)
        self.entry_tp_search.bind("<Return>", lambda e: self._refresh_testpoint_list())

        ctk.CTkButton(
            filter_bar,
            text="🔍 Cari",
            width=70,
            fg_color="#007ACC",
            command=self._refresh_testpoint_list
        ).pack(side="left", padx=8, pady=8)

        unbrick_body = ctk.CTkFrame(self.frame_tp_unbrick, fg_color="transparent")
        unbrick_body.pack(fill="both", expand=True)
        unbrick_body.columnconfigure(0, weight=1)
        unbrick_body.columnconfigure(1, weight=2)
        unbrick_body.rowconfigure(0, weight=1)

        self.tp_list_scroll = ctk.CTkScrollableFrame(unbrick_body, corner_radius=8, fg_color="#14141E")
        self.tp_list_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=2)

        self.tp_inspector = ctk.CTkScrollableFrame(unbrick_body, corner_radius=8, fg_color="#14141E")
        self.tp_inspector.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=2)

        # Initial populate
        self._refresh_poweron_brands()
        self._refresh_testpoint_list()

        # Show default active frame
        self.frame_tp_poweron.pack(fill="both", expand=True)

    def _on_tp_mode_changed(self, mode):
        if "FORCE POWER-ON" in mode:
            self.frame_tp_unbrick.pack_forget()
            self.frame_tp_poweron.pack(fill="both", expand=True)
            brand = getattr(self, '_selected_pwr_brand', "Xiaomi / Redmi / POCO")
            self._show_poweron_detail(brand)
        else:
            self.frame_tp_poweron.pack_forget()
            self.frame_tp_unbrick.pack(fill="both", expand=True)
            self._refresh_testpoint_list()

    def _refresh_poweron_brands(self):
        for w in self.pwr_brand_list_scroll.winfo_children():
            w.destroy()

        brands = PowerOnDatabase.get_all_brands()
        for idx, b_name in enumerate(brands):
            btn = ctk.CTkButton(
                self.pwr_brand_list_scroll,
                text=f"📱 {b_name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                fg_color="#1E1E2C",
                hover_color="#2D3250",
                height=42,
                command=lambda b=b_name: self._show_poweron_detail(b)
            )
            btn.pack(fill="x", padx=4, pady=3)

        if brands:
            self._show_poweron_detail(brands[0])

    def _show_poweron_detail(self, brand_name):
        self._selected_pwr_brand = brand_name
        guide = PowerOnDatabase.get_guide(brand_name)
        for w in self.pwr_detail_scroll.winfo_children():
            w.destroy()

        # Header Title
        ctk.CTkLabel(
            self.pwr_detail_scroll,
            text=f"📱 PANDUAN FORCE POWER-ON: {guide['brand']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=12, pady=(10, 2))

        # Badge Info
        badge = ctk.CTkLabel(
            self.pwr_detail_scroll,
            text=f"CHIPSET: {guide['chipset']}  |  TEGANGAN STANDBY PWR: {guide['pwr_voltage']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00FFAA",
            fg_color="#1E1E2C",
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(
            self.pwr_detail_scroll,
            text=f"Tipe/Model: {guide['models_covered']}",
            font=ctk.CTkFont(size=11),
            text_color="#A0A0B0",
            wraplength=480,
            justify="left"
        ).pack(anchor="w", padx=12, pady=2)

        # Summary box
        box_sum = ctk.CTkFrame(self.pwr_detail_scroll, corner_radius=6, fg_color="#201C2B", border_width=1, border_color="#7B1FA2")
        box_sum.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(
            box_sum,
            text=f"💡 Strategi Utama: {guide['summary']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#E040FB",
            wraplength=460,
            justify="left"
        ).pack(anchor="w", padx=10, pady=8)

        # Section 1: Jumper Pinset
        ctk.CTkLabel(self.pwr_detail_scroll, text="🔌 1. METODE JUMPER PINSET TITIK PWR_KEY KE KALENG GROUND (GND):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFAA00").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(self.pwr_detail_scroll, text=guide['method_jumper'], font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        # Section 2: Fastboot Reboot
        ctk.CTkLabel(self.pwr_detail_scroll, text="⚡ 2. METODE MASUK FASTBOOT / RECOVERY -> BOOTING NORMAL (TANPA TOMBOL POWER):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(self.pwr_detail_scroll, text=guide['method_fastboot'], font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        # Section 3: Auto-Charge
        ctk.CTkLabel(self.pwr_detail_scroll, text="🔥 3. TRIK MENYALAKAN HP OTOMATIS SAAT COLOK CHARGER (AUTO-BOOT):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF9800").pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(self.pwr_detail_scroll, text=guide['method_autocharge'], font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        # Section 4: Battery Trick
        ctk.CTkLabel(self.pwr_detail_scroll, text="🔋 4. TRIK SIKLUS BATERAI & RESET DAYA HARDWARE:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FFAA").pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(self.pwr_detail_scroll, text=guide['method_battery_trick'], font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        # Section 5: ASCII Schematic
        ctk.CTkLabel(self.pwr_detail_scroll, text="📐 SKEMATIK JALUR PWR_KEY PADA MOTHERBOARD:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FFAA").pack(anchor="w", padx=12, pady=(14, 2))
        diag_box = ctk.CTkTextbox(
            self.pwr_detail_scroll,
            height=160,
            fg_color="#08080E",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#00FF88"
        )
        diag_box.pack(fill="x", padx=12, pady=(2, 15))
        diag_box.insert("1.0", guide['ascii_diagram'])
        diag_box.configure(state="disabled")

    def _action_fastboot_reboot(self):
        def worker():
            from config import get_fastboot_path, run_cmd
            fb = get_fastboot_path()
            serial = self.current_device.get("serial") if self.current_device else None
            cmd = [fb]
            if serial:
                cmd += ["-s", serial]
            cmd += ["reboot"]
            res = run_cmd(cmd, timeout=8)
            def update():
                msg = res or "Perintah 'fastboot reboot' terkirim!"
                self.lbl_pwr_action_status.configure(text=f"✅ {msg}")
                messagebox.showinfo("Fastboot Reboot Sukses", f"Perintah reboot terkirim!\n\nHasil: {msg}\n\nHP sedang reboot ke menu utama Android. Setelah menyala, ADB otomatis terhubung!")
            self.after(0, update)
        self.lbl_pwr_action_status.configure(text="⏳ Mengirim 'fastboot reboot'...")
        threading.Thread(target=worker, daemon=True).start()

    def _action_fastboot_autocharge(self):
        def worker():
            from config import get_fastboot_path, run_cmd
            fb = get_fastboot_path()
            serial = self.current_device.get("serial") if self.current_device else None
            cmd = [fb]
            if serial:
                cmd += ["-s", serial]
            cmd += ["oem", "off-mode-charge", "0"]
            res = run_cmd(cmd, timeout=8)
            def update():
                msg = res or "Perintah off-mode-charge 0 sukses!"
                self.lbl_pwr_action_status.configure(text=f"⚡ {msg}")
                messagebox.showinfo("Auto-Boot on Charge", f"Konfigurasi terpasang!\n\nHasil: {msg}\n\nSetiap kali kabel charger/USB dicolok, HP akan otomatis menyala ke sistem Android tanpa perlu menekan tombol power!")
            self.after(0, update)
        self.lbl_pwr_action_status.configure(text="⏳ Mengirim 'fastboot oem off-mode-charge 0'...")
        threading.Thread(target=worker, daemon=True).start()

    def _refresh_testpoint_list(self):
        for widget in self.tp_list_scroll.winfo_children():
            widget.destroy()

        brand = self.cb_tp_brand.get() if hasattr(self, 'cb_tp_brand') else "SEMUA MERK"
        q = self.entry_tp_search.get().strip() if hasattr(self, 'entry_tp_search') else ""

        results = TestPointDatabase.search(brand_filter=brand, query=q)

        if not results:
            ctk.CTkLabel(self.tp_list_scroll, text="Model tidak ditemukan.", text_color="#707080").pack(pady=20)
            return

        for idx, item in enumerate(results):
            btn = ctk.CTkButton(
                self.tp_list_scroll,
                text=f"{item['model']}\n[{item['mode']}] - {item['chipset']}",
                font=ctk.CTkFont(size=12),
                anchor="w",
                fg_color="#1E1E2C",
                hover_color="#2D3250",
                height=48,
                command=lambda it=item: self._show_testpoint_detail(it)
            )
            btn.pack(fill="x", padx=4, pady=3)

        if results:
            self._show_testpoint_detail(results[0])

    def _show_testpoint_detail(self, item):
        for widget in self.tp_inspector.winfo_children():
            widget.destroy()

        m_lbl = ctk.CTkLabel(
            self.tp_inspector,
            text=f"📱 {item['brand']} {item['model']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00D2FF"
        )
        m_lbl.pack(anchor="w", padx=12, pady=(10, 2))

        mode_color = "#E040FB" if "9008" in item['mode'] else "#00FFAA"
        badge = ctk.CTkLabel(
            self.tp_inspector,
            text=f"TARGET MODE: {item['mode']}  |  CHIPSET: {item['chipset']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=mode_color,
            fg_color="#1E1E2C",
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(self.tp_inspector, text="📍 Letak Fisik Titik Test Point:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFAA00").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(self.tp_inspector, text=item['location'], font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        ctk.CTkLabel(self.tp_inspector, text="🛠️ Langkah Eksekusi Colok USB:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(self.tp_inspector, text=item['steps'], font=ctk.CTkFont(size=12), text_color="#B0B0C0", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=2)

        ctk.CTkLabel(self.tp_inspector, text="📐 Diagram Skematik Pinout:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FFAA").pack(anchor="w", padx=12, pady=(12, 2))
        
        diag_box = ctk.CTkTextbox(
            self.tp_inspector,
            height=150,
            fg_color="#08080E",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#00FF88"
        )
        diag_box.pack(fill="x", padx=12, pady=(2, 15))
        diag_box.insert("1.0", item['ascii_diagram'])
        diag_box.configure(state="disabled")

    # -------------------------------------------------------------
    # TAB: FLASHING & FIRMWARE MANAGER
    # -------------------------------------------------------------
    def _build_tab_flasher(self):
        container = ctk.CTkScrollableFrame(self.tab_flash, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=10)

        hdr = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        hdr.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            hdr, 
            text="⚡ FLASHING & PENGGANTIAN FIRMWARE ANDROID (FASTBOOT & SIDELOAD)", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        self.lbl_flash_status = ctk.CTkLabel(
            hdr,
            text="Status Flashing: Siapkan HP dalam mode Fastboot (Tahan Vol Bawah + Power) atau Recovery Sideload.",
            font=ctk.CTkFont(size=12),
            text_color="#FFAA00"
        )
        self.lbl_flash_status.pack(anchor="w", padx=15, pady=(0, 10))

        btn_short_box = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_short_box.pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(btn_short_box, text="⚡ Masuk Fastboot Mode", width=160, fg_color="#E65100", command=self._cmd_reboot_fastboot).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_short_box, text="🛡️ Masuk Recovery Mode", width=160, fg_color="#7B1FA2", command=self._cmd_reboot_recovery).pack(side="left")

        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="x", pady=4)
        grid.columnconfigure((0, 1), weight=1)

        # Card 1: Fastboot Single Partition Flash
        c1 = ctk.CTkFrame(grid, corner_radius=8, fg_color="#1B1B26")
        c1.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        ctk.CTkLabel(c1, text="1. Flash Partisi Satuan (Fastboot .img)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(10, 4))
        
        row_p = ctk.CTkFrame(c1, fg_color="transparent")
        row_p.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(row_p, text="Partisi:", width=70, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.cb_part = ctk.CTkComboBox(row_p, values=["boot", "recovery", "vbmeta", "super", "system", "vendor", "dtbo", "userdata", "cust", "persist"], width=160)
        self.cb_part.set("boot")
        self.cb_part.pack(side="left", padx=4)

        self.chk_vbmeta = ctk.CTkCheckBox(c1, text="Disable Verity & Verification (Khusus vbmeta)", font=ctk.CTkFont(size=11))
        self.chk_vbmeta.pack(anchor="w", padx=12, pady=4)

        row_f = ctk.CTkFrame(c1, fg_color="transparent")
        row_f.pack(fill="x", padx=12, pady=4)
        self.entry_img_path = ctk.CTkEntry(row_f, placeholder_text="Pilih file image (.img)...")
        self.entry_img_path.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row_f, text="Browse", width=70, command=self._browse_img_file).pack(side="left")

        ctk.CTkButton(c1, text="⚡ FLASH PARTISI SEKARANG", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#007ACC", hover_color="#005999", command=self._exec_flash_partition).pack(anchor="w", padx=12, pady=(6, 12))

        # Card 2: Slot A/B Switcher & Wipe
        c2 = ctk.CTkFrame(grid, corner_radius=8, fg_color="#1B1B26")
        c2.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        ctk.CTkLabel(c2, text="2. Penyelamat Bootloop: Ganti Slot A/B & Wipe", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(10, 4))
        
        self.lbl_active_slot = ctk.CTkLabel(c2, text="Slot Aktif: [ Tekan tombol Cek Slot ]", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFAA00")
        self.lbl_active_slot.pack(anchor="w", padx=12, pady=2)

        slot_box = ctk.CTkFrame(c2, fg_color="transparent")
        slot_box.pack(anchor="w", padx=12, pady=4)
        ctk.CTkButton(slot_box, text="Cek Slot", width=80, fg_color="#333", command=self._check_current_slot).pack(side="left", padx=(0, 4))
        ctk.CTkButton(slot_box, text="Set Slot A", width=90, fg_color="#2E7D32", command=lambda: self._set_slot("a")).pack(side="left", padx=4)
        ctk.CTkButton(slot_box, text="Set Slot B", width=90, fg_color="#1565C0", command=lambda: self._set_slot("b")).pack(side="left", padx=4)

        ctk.CTkLabel(c2, text="Format Bersih (Factory Reset via Fastboot):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=12, pady=(6, 2))
        wipe_box = ctk.CTkFrame(c2, fg_color="transparent")
        wipe_box.pack(anchor="w", padx=12, pady=(2, 12))
        ctk.CTkButton(wipe_box, text="🧹 Erase Userdata", width=130, fg_color="#C62828", hover_color="#8E0000", command=lambda: self._erase_part("userdata")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(wipe_box, text="🧹 Erase Cache", width=110, fg_color="#616161", command=lambda: self._erase_part("cache")).pack(side="left")

        # Card 3: ADB Sideload (.ZIP Recovery / OTA)
        c3 = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c3.pack(fill="x", pady=4)

        ctk.CTkLabel(c3, text="3. Sideload Firmware (.ZIP) - Pasang ROM / Update dari Recovery", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(c3, text="HP harus dalam mode Recovery -> Pilih menu 'Apply Update from ADB' / 'ADB Sideload'.", font=ctk.CTkFont(size=11), text_color="#A0A0B0").pack(anchor="w", padx=12, pady=(0, 6))

        row_zip = ctk.CTkFrame(c3, fg_color="transparent")
        row_zip.pack(fill="x", padx=12, pady=4)
        self.entry_zip_path = ctk.CTkEntry(row_zip, placeholder_text="Pilih file firmware .zip (OTA / Custom ROM)...")
        self.entry_zip_path.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row_zip, text="Browse", width=70, command=self._browse_zip_file).pack(side="left")

        ctk.CTkButton(c3, text="📦 MULAI SIDELOAD FIRMWARE", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#7B1FA2", hover_color="#4A148C", command=self._exec_sideload).pack(anchor="w", padx=12, pady=(4, 12))

        # Card 4: Run Batch ROM Script (flash_all.bat)
        c4 = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c4.pack(fill="x", pady=4)

        ctk.CTkLabel(c4, text="4. Flash ROM Resmi Utuh (Xiaomi / Pixel Batch Script)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(c4, text="Pilih file script flash dari folder ROM Fastboot (Contoh: flash_all.bat untuk Xiaomi atau flash-all.bat untuk Pixel).", font=ctk.CTkFont(size=11), text_color="#A0A0B0").pack(anchor="w", padx=12, pady=(0, 6))

        row_bat = ctk.CTkFrame(c4, fg_color="transparent")
        row_bat.pack(fill="x", padx=12, pady=4)
        self.entry_bat_path = ctk.CTkEntry(row_bat, placeholder_text="Pilih file flash_all.bat...")
        self.entry_bat_path.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row_bat, text="Browse", width=70, command=self._browse_bat_file).pack(side="left")

        ctk.CTkButton(c4, text="🚀 JALANKAN FLASH ROM RESMI", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#D84315", hover_color="#BF360C", command=self._exec_flash_script).pack(anchor="w", padx=12, pady=(4, 12))

        # Card 5: Live Console Output Log
        log_box = ctk.CTkFrame(container, corner_radius=8, fg_color="#181824")
        log_box.pack(fill="x", pady=8)

        log_hdr = ctk.CTkFrame(log_box, fg_color="transparent")
        log_hdr.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(log_hdr, text="🖥️ LIVE LOG TERMINAL FLASHING", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00FFAA").pack(side="left")
        ctk.CTkButton(log_hdr, text="Bersihkan Log", width=100, height=24, fg_color="#333", command=self._clear_flash_log).pack(side="right")

        self.txt_flash_log = ctk.CTkTextbox(
            log_box,
            height=160,
            fg_color="#0B0B10",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#00FFAA"
        )
        self.txt_flash_log.pack(fill="x", padx=12, pady=(2, 12))
        self.txt_flash_log.insert("end", "[READY] Konsol Flashing siap. Pilih firmware dan klik tombol flash.\n")

    def _log_flash(self, text):
        def write():
            self.txt_flash_log.insert("end", text)
            self.txt_flash_log.see("end")
        self.after(0, write)

    def _clear_flash_log(self):
        self.txt_flash_log.delete("1.0", "end")
        self.txt_flash_log.insert("end", "[LOG DIBERSIHKAN]\n")

    def _browse_img_file(self):
        fn = filedialog.askopenfilename(filetypes=[("Image Files", "*.img;*.bin;*.elf"), ("All Files", "*.*")])
        if fn:
            self.entry_img_path.delete(0, "end")
            self.entry_img_path.insert(0, fn)

    def _browse_zip_file(self):
        fn = filedialog.askopenfilename(filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")])
        if fn:
            self.entry_zip_path.delete(0, "end")
            self.entry_zip_path.insert(0, fn)

    def _browse_bat_file(self):
        fn = filedialog.askopenfilename(filetypes=[("Batch Scripts", "*.bat;*.cmd;*.sh"), ("All Files", "*.*")])
        if fn:
            self.entry_bat_path.delete(0, "end")
            self.entry_bat_path.insert(0, fn)

    def _get_flasher(self):
        with self._device_lock:
            return self.flasher or FirmwareFlasher()

    def _check_current_slot(self):
        def worker():
            flasher = self._get_flasher()
            slot = flasher.get_current_slot()
            self.after(0, lambda: self.lbl_active_slot.configure(text=f"Slot Aktif: [ {slot.upper()} ]"))
            self._log_flash(f"[INFO] Current Slot: {slot}\n")
        threading.Thread(target=worker, daemon=True).start()

    def _set_slot(self, slot):
        flasher = self._get_flasher()
        threading.Thread(target=flasher.set_active_slot, args=(slot, self._log_flash), daemon=True).start()

    def _erase_part(self, part):
        if not messagebox.askyesno("Konfirmasi Erase", f"Yakin ingin menghapus partisi '{part}'?"):
            return
        flasher = self._get_flasher()
        threading.Thread(target=flasher.erase_partition, args=(part, self._log_flash), daemon=True).start()

    def _exec_flash_partition(self):
        part = self.cb_part.get().strip()
        path = self.entry_img_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showwarning("File Belum Dipilih", "Pilih file image (.img) terlebih dahulu!")
            return
        disable_verity = bool(self.chk_vbmeta.get())
        if not messagebox.askyesno("Konfirmasi Flash", f"Flash file '{os.path.basename(path)}' ke partisi '{part}'?"):
            return
        flasher = self._get_flasher()
        self._log_flash(f"\n[FLASH START] Memulai flashing partisi '{part}'...\n")
        def worker():
            ok, out = flasher.flash_partition(part, path, disable_verity=disable_verity, on_log=self._log_flash)
            if ok:
                self._log_flash(f"[SELESAI] Partisi '{part}' berhasil di-flash!\n")
            else:
                self._log_flash(f"[GAGAL] Flashing partisi '{part}' gagal.\n")
        threading.Thread(target=worker, daemon=True).start()

    def _exec_sideload(self):
        path = self.entry_zip_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showwarning("File Belum Dipilih", "Pilih file firmware (.zip) terlebih dahulu!")
            return
        if not messagebox.askyesno("Konfirmasi Sideload", f"Mulai sideload file '{os.path.basename(path)}' ke perangkat?"):
            return
        flasher = self._get_flasher()
        self._log_flash(f"\n[SIDELOAD START] Mengirim firmware '{os.path.basename(path)}'...\n")
        def worker():
            ok, out = flasher.sideload_ota_zip(path, on_log=self._log_flash)
            if ok:
                self._log_flash("[SELESAI] Sideload firmware berhasil!\n")
            else:
                self._log_flash("[GAGAL] Sideload firmware gagal.\n")
        threading.Thread(target=worker, daemon=True).start()

    def _exec_flash_script(self):
        path = self.entry_bat_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showwarning("File Belum Dipilih", "Pilih file script flash_all.bat terlebih dahulu!")
            return
        if not messagebox.askyesno("Konfirmasi Flash ROM", f"Jalankan script '{os.path.basename(path)}'? Ini akan menulis ulang seluruh partisi sistem!"):
            return
        flasher = self._get_flasher()
        self._log_flash(f"\n[BATCH FLASH START] Menjalankan script '{os.path.basename(path)}'...\n")
        def worker():
            ok, out = flasher.run_rom_flash_script(path, on_log=self._log_flash)
            if ok:
                self._log_flash("[SELESAI] Flashing ROM selesai!\n")
            else:
                self._log_flash("[GAGAL] Flashing script berhenti dengan error.\n")
        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------------------------------------
    # TAB: DRIVER USB & FILTER MANAGER
    # -------------------------------------------------------------
    def _build_tab_drivers(self):
        container = ctk.CTkScrollableFrame(self.tab_driver, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=10)

        # Header Card
        hdr = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        hdr.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            hdr,
            text="🔌 USB DRIVER & FILTER MANAGER (ASISTEN TEKNISI)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            hdr,
            text="Cek kesiapan driver flashing, port Qualcomm EDL 9008, MediaTek PreLoader/BROM, Samsung & filter LibUSB.",
            font=ctk.CTkFont(size=12),
            text_color="#A0A0B0"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        action_box = ctk.CTkFrame(hdr, fg_color="transparent")
        action_box.pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(
            action_box,
            text="🖥️ Buka Device Manager (devmgmt.msc)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#007ACC",
            hover_color="#005999",
            height=32,
            command=DriverHelper.open_device_manager
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_box,
            text="🔄 Periksa Ulang Driver",
            font=ctk.CTkFont(size=12),
            fg_color="#2D3250",
            hover_color="#424769",
            height=32,
            command=self._refresh_driver_statuses
        ).pack(side="left", padx=(0, 8))

        # Driver list section
        ctk.CTkLabel(
            container,
            text="DAFTAR DRIVER HARDWARE UTAMA",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(4, 6))

        self._driver_status_labels = {}
        for d in DriverHelper.DRIVERS:
            row = ctk.CTkFrame(container, corner_radius=8, fg_color="#181824")
            row.pack(fill="x", pady=4)

            # Left side: Info
            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            title_txt = f"{d['name']} ({d['vendor']})"
            ctk.CTkLabel(
                left,
                text=title_txt,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ECEFF1"
            ).pack(anchor="w")

            ctk.CTkLabel(
                left,
                text=f"HWID: {d['hardware_id']}  •  {d['description']}",
                font=ctk.CTkFont(size=11),
                text_color="#90A4AE"
            ).pack(anchor="w", pady=(2, 0))

            # Right side: Actions & Status
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=12, pady=10)

            lbl_st = ctk.CTkLabel(
                right,
                text="Memeriksa...",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=160,
                corner_radius=6,
                fg_color="#222230"
            )
            lbl_st.pack(side="left", padx=(0, 10), ipady=4)
            self._driver_status_labels[d["id"]] = lbl_st

            url = d["download_url"]
            ctk.CTkButton(
                right,
                text="🌐 Unduh Driver",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=110,
                height=28,
                fg_color="#2E7D32",
                hover_color="#1B5E20",
                command=lambda u=url: DriverHelper.open_driver_download(u)
            ).pack(side="left")

        # Troubleshooter Guide Box
        guide_box = ctk.CTkFrame(container, corner_radius=8, fg_color="#1E1E2F")
        guide_box.pack(fill="x", pady=(14, 10))

        ctk.CTkLabel(
            guide_box,
            text="💡 PANDUAN MENGATASI PORT TEST POINT / BROM PUTUS-NYAMBUNG (DISCONNECT LOOP)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFD54F"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        guide_text = (
            "1. Gejala: Saat HP matot dicolok / di-jumper Test Point, port Qualcomm 9008 atau MediaTek VCOM muncul di Device Manager selama 1-2 detik lalu hilang (bunyi notifikasi putus).\n"
            "2. Pasang LibUSB-win32 atau UsbDk: Tanpa driver filter, MediaTek BROM modern dan Qualcomm EDL akan langsung reset bila handshake terlambat.\n"
            "3. Nonaktifkan Driver Signature Enforcement (Windows 10 / 11 64-bit):\n"
            "   • Tahan tombol SHIFT sambil klik Start -> Power -> Restart.\n"
            "   • Pilih Troubleshoot -> Advanced Options -> Startup Settings -> Restart -> Tekan F7 (Disable driver signature enforcement).\n"
            "4. Cek Kabel & Port USB:\n"
            "   • Selalu gunakan port USB di belakang casing CPU (Motherboard langsung), BUKAN port depan casing atau USB Hub tanpa adaptor.\n"
            "   • Gunakan kabel data tebal berkualitas (hindari kabel charger tipis yang hanya memiliki jalur daya tanpa jalur D+/D-)."
        )
        ctk.CTkLabel(
            guide_box,
            text=guide_text,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#B0BEC5",
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # Initial check
        self.after(500, self._refresh_driver_statuses)

    def _refresh_driver_statuses(self):
        for d in DriverHelper.DRIVERS:
            lbl = self._driver_status_labels.get(d["id"])
            if not lbl:
                continue
            is_ok = DriverHelper.check_driver_status(d["id"])
            if is_ok:
                lbl.configure(text="✅ Terpasang / Aktif", text_color="#00E676", fg_color="#1B3B2B")
            else:
                lbl.configure(text="⚠️ Belum Terdeteksi", text_color="#FFB300", fg_color="#3B301B")

    # -------------------------------------------------------------
    # TAB 4: ALAT UJI FISIK
    # -------------------------------------------------------------
    def _build_tab_tests(self):
        container = ctk.CTkScrollableFrame(self.tab_tests, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        container.columnconfigure((0, 1), weight=1)

        # Card 1: Vibrator
        c_vib = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c_vib.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(c_vib, text="📳 Uji Motor Getar (Vibrator)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(c_vib, text="Memicu vibrator HP selama 1.5 detik (Android 8 - 15).", font=ctk.CTkFont(size=12), text_color="#A0A0B0").pack(anchor="w", padx=15, pady=(0, 10))
        ctk.CTkButton(c_vib, text="⚡ Getarkan HP Sekarang", fg_color="#007ACC", hover_color="#005999", command=self._trigger_vibrator).pack(anchor="w", padx=15, pady=(0, 6))
        self.lbl_vib_status = ctk.CTkLabel(c_vib, text="", font=ctk.CTkFont(size=11), text_color="#00FFAA", wraplength=380, justify="left")
        self.lbl_vib_status.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 2: Torch
        c_torch = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c_torch.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(c_torch, text="🔦 Uji Lampu Senter / Flash IC", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(c_torch, text="Uji nyala LED flash kamera belakang (Sysfs + Quick Settings).", font=ctk.CTkFont(size=12), text_color="#A0A0B0").pack(anchor="w", padx=15, pady=(0, 10))
        b_box = ctk.CTkFrame(c_torch, fg_color="transparent")
        b_box.pack(anchor="w", padx=15, pady=(0, 6))
        ctk.CTkButton(b_box, text="💡 Senter ON", width=110, fg_color="#2E7D32", command=lambda: self._trigger_torch(True)).pack(side="left", padx=(0, 8))
        ctk.CTkButton(b_box, text="🛑 Senter OFF", width=110, fg_color="#C62828", command=lambda: self._trigger_torch(False)).pack(side="left")
        self.lbl_torch_status = ctk.CTkLabel(c_torch, text="", font=ctk.CTkFont(size=11), text_color="#00FFAA", wraplength=380, justify="left")
        self.lbl_torch_status.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 3: Speaker, Earpiece & Mic
        c_audio = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c_audio.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(c_audio, text="🔊 Uji Audio, Speaker & Mikrofon", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(c_audio, text="Uji speaker utama bawah, earpiece telinga, dan mic loopback 3 detik.", font=ctk.CTkFont(size=11), text_color="#A0A0B0").pack(anchor="w", padx=15, pady=(0, 8))
        
        aud_btn_box = ctk.CTkFrame(c_audio, fg_color="transparent")
        aud_btn_box.pack(anchor="w", padx=15, pady=(0, 6))
        ctk.CTkButton(aud_btn_box, text="🔊 Buzzer Bawah", width=115, fg_color="#007ACC", hover_color="#005999", command=self._trigger_audio).pack(side="left", padx=(0, 6))
        ctk.CTkButton(aud_btn_box, text="📞 Earpiece Atas", width=115, fg_color="#3949AB", hover_color="#283593", command=self._trigger_earpiece).pack(side="left", padx=(0, 6))
        ctk.CTkButton(aud_btn_box, text="🎙️ Mic Loopback", width=115, fg_color="#00897B", hover_color="#00695C", command=self._trigger_mic).pack(side="left")

        self.lbl_audio_status = ctk.CTkLabel(c_audio, text="", font=ctk.CTkFont(size=11), text_color="#00FFAA", wraplength=420, justify="left")
        self.lbl_audio_status.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 4: LCD Color
        c_lcd = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c_lcd.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(c_lcd, text="🎨 Uji Warna Layar (Dead Pixel)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(c_lcd, text="Tampilkan gambar solid full-screen di Galeri Foto HP.", font=ctk.CTkFont(size=12), text_color="#A0A0B0").pack(anchor="w", padx=15, pady=(0, 10))
        c_box = ctk.CTkFrame(c_lcd, fg_color="transparent")
        c_box.pack(anchor="w", padx=15, pady=(0, 6))
        ctk.CTkButton(c_box, text="Merah", width=60, fg_color="#D32F2F", command=lambda: self._trigger_color("#FF0000")).pack(side="left", padx=2)
        ctk.CTkButton(c_box, text="Hijau", width=60, fg_color="#388E3C", command=lambda: self._trigger_color("#00FF00")).pack(side="left", padx=2)
        ctk.CTkButton(c_box, text="Biru", width=60, fg_color="#1976D2", command=lambda: self._trigger_color("#0000FF")).pack(side="left", padx=2)
        ctk.CTkButton(c_box, text="Putih", width=60, fg_color="#FFF", text_color="#000", command=lambda: self._trigger_color("#FFFFFF")).pack(side="left", padx=2)
        ctk.CTkButton(c_box, text="Hitam", width=60, fg_color="#212121", command=lambda: self._trigger_color("#000000")).pack(side="left", padx=2)
        self.lbl_lcd_status = ctk.CTkLabel(c_lcd, text="", font=ctk.CTkFont(size=11), text_color="#00FFAA", wraplength=380, justify="left")
        self.lbl_lcd_status.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 5: Physical Keys Listener
        c_keys = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        c_keys.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(c_keys, text="🔘 Uji Tombol Fisik Real-Time (Volume Up, Volume Down, Power)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00D2FF").pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(c_keys, text="Tekan tombol fisik di HP konsumen. Indikator virtual akan menyala hijau seketika!", font=ctk.CTkFont(size=12), text_color="#A0A0B0").pack(anchor="w", padx=15, pady=(0, 8))

        k_badges = ctk.CTkFrame(c_keys, fg_color="transparent")
        k_badges.pack(anchor="w", padx=15, pady=6)

        self.badge_vol_up = ctk.CTkLabel(k_badges, text="🔊 VOLUME UP", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2B2B36", text_color="#888", corner_radius=6, padx=16, pady=10)
        self.badge_vol_up.pack(side="left", padx=(0, 10))

        self.badge_vol_down = ctk.CTkLabel(k_badges, text="🔉 VOLUME DOWN", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2B2B36", text_color="#888", corner_radius=6, padx=16, pady=10)
        self.badge_vol_down.pack(side="left", padx=(0, 10))

        self.badge_power = ctk.CTkLabel(k_badges, text="⚡ POWER BUTTON", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2B2B36", text_color="#888", corner_radius=6, padx=16, pady=10)
        self.badge_power.pack(side="left", padx=(0, 15))

        self.btn_listen_keys = ctk.CTkButton(k_badges, text="▶️ Aktifkan Deteksi Tombol", fg_color="#007ACC", hover_color="#005999", command=self._toggle_key_listener)
        self.btn_listen_keys.pack(side="left", padx=10)

        # Card 6: Touchscreen Digitizer & Dead-Zone Test Suite
        c_touch = ctk.CTkFrame(container, corner_radius=8, fg_color="#181824", border_width=1, border_color="#00BCD4")
        c_touch.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=(6, 12))

        ctk.CTkLabel(
            c_touch,
            text="👆 Uji Layar Sentuh (Touchscreen Digitizer & Dead-Zone Test)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00E5FF"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            c_touch,
            text="Uji responsivitas sentuhan, deteksi area layar sentuh mati (dead zone), jejak putus-putus, serta sentuhan liar (ghost touch):",
            font=ctk.CTkFont(size=11),
            text_color="#A0A0B0",
            wraplength=700,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        touch_btn_box = ctk.CTkFrame(c_touch, fg_color="transparent")
        touch_btn_box.pack(fill="x", padx=15, pady=(0, 8))

        self.btn_toggle_pointer = ctk.CTkButton(
            touch_btn_box,
            text="📍 Aktifkan Jejak Sentuh (Pointer Location)",
            fg_color="#00838F",
            hover_color="#006064",
            font=ctk.CTkFont(weight="bold"),
            command=self._toggle_pointer_location
        )
        self.btn_toggle_pointer.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            touch_btn_box,
            text="🟩 Buka Papan Kisi Uji (Matrix Grid)",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            font=ctk.CTkFont(weight="bold"),
            command=self._launch_touch_grid
        ).pack(side="left", padx=(0, 8))

        self.btn_touch_monitor = ctk.CTkButton(
            touch_btn_box,
            text="📡 Pantau Sentuhan di PC",
            fg_color="#3949AB",
            hover_color="#283593",
            command=self._toggle_touch_monitor
        )
        self.btn_touch_monitor.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            touch_btn_box,
            text="⚙️ Menu Tes Pabrik (CIT / Factory)",
            fg_color="#455A64",
            hover_color="#37474F",
            command=self._launch_factory_touch_menu
        ).pack(side="left")

        # Telemetry info box for touch monitoring
        self.touch_telemetry_box = ctk.CTkFrame(c_touch, fg_color="#12121A", corner_radius=6)
        self.touch_telemetry_box.pack(fill="x", padx=15, pady=(0, 10))

        self.lbl_touch_status = ctk.CTkLabel(
            self.touch_telemetry_box,
            text="💡 Tip: Klik 'Aktifkan Jejak Sentuh' untuk memunculkan garis jejak merah/biru bawaan Android di layar HP.",
            font=ctk.CTkFont(size=11),
            text_color="#00FFAA",
            wraplength=680,
            justify="left"
        )
        self.lbl_touch_status.pack(anchor="w", padx=12, pady=8)

    # -------------------------------------------------------------
    # TAB 4: MENU REBOOT
    # -------------------------------------------------------------
    def _build_tab_reboot(self):
        container = ctk.CTkFrame(self.tab_reboot, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(container, text="Menu Khusus Teknisi: Reboot Perangkat Tanpa Sentuh Tombol", font=ctk.CTkFont(size=15, weight="bold"), text_color="#00D2FF").pack(anchor="w", pady=(0, 15))

        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="x", pady=10)
        grid.columnconfigure((0, 1, 2), weight=1)

        self._create_reboot_button(grid, "🔄 Reboot Normal", "Restart HP ke sistem Android biasa.", self._cmd_reboot_normal, 0, 0, "#007ACC")
        self._create_reboot_button(grid, "🛡️ Reboot Recovery", "Masuk ke Stock / TWRP Recovery mode.", self._cmd_reboot_recovery, 0, 1, "#7B1FA2")
        self._create_reboot_button(grid, "⚡ Reboot Fastboot", "Masuk ke Bootloader / Fastboot mode.", self._cmd_reboot_fastboot, 0, 2, "#E65100")
        
        self._create_reboot_button(grid, "🟣 Reboot EDL 9008", "Khusus Qualcomm (adb reboot edl).", self._cmd_reboot_edl, 1, 0, "#4A148C")
        self._create_reboot_button(grid, "💡 Bangunkan Layar", "Kirim sinyal Wakeup Screen / Power.", self._cmd_wakeup_screen, 1, 1, "#2E7D32")
        self._create_reboot_button(grid, "🔌 Matikan HP (Shutdown)", "Perintahkan HP shutdown total.", self._cmd_power_off, 1, 2, "#C62828")

    def _create_reboot_button(self, parent, title, desc, command, row, col, color):
        box = ctk.CTkFrame(parent, corner_radius=8, fg_color="#1B1B26")
        box.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFF").pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(box, text=desc, font=ctk.CTkFont(size=11), text_color="#9E9E9E", wraplength=220).pack(anchor="w", padx=12, pady=(0, 10))
        ctk.CTkButton(box, text="Eksekusi", fg_color=color, hover_color="#333", height=32, command=command).pack(anchor="w", padx=12, pady=(0, 12))

    # -------------------------------------------------------------
    # TAB 5: DATA RESCUE & SCREEN MIRROR
    # -------------------------------------------------------------
    def _build_tab_mirror(self):
        container = ctk.CTkScrollableFrame(self.tab_mirror, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            container,
            text="📦 Penyelamatan Data Pasien & Deteksi Akun (Layar Rusak / Lupa Email)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            container,
            text="Solusi untuk HP konsumen yang LCD pecah, touch mati, tombol rusak saat ganti HP baru:\n"
                 "Temukan akun Google/Gmail yang tertanam, ekspor kontak (.VCF), amankan WhatsApp, foto & dokumen via USB.",
            font=ctk.CTkFont(size=11),
            text_color="#A0A0B0",
            justify="left"
        ).pack(anchor="w", pady=(0, 15))

        # CARD 1: Deteksi Akun Google & Vendor
        card_acc = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        card_acc.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_acc,
            text="📧 Deteksi Akun Google (Gmail) & Akun Terpasang",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00FFAA"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card_acc,
            text="Membaca akun email Google, WhatsApp, Xiaomi, dan Samsung yang tersimpan di sistem tanpa membuka layar.",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        self.txt_accounts_display = ctk.CTkTextbox(
            card_acc,
            height=110,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#13131A"
        )
        self.txt_accounts_display.pack(fill="x", padx=15, pady=(0, 10))
        self.txt_accounts_display.insert("1.0", "Tekan tombol '🔍 Pindai Akun Sekarang' untuk mendeteksi akun Gmail & vendor...")
        self.txt_accounts_display.configure(state="disabled")

        acc_btn_box = ctk.CTkFrame(card_acc, fg_color="transparent")
        acc_btn_box.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(
            acc_btn_box,
            text="🔍 Pindai Akun Sekarang",
            fg_color="#007ACC",
            hover_color="#005999",
            command=self._detect_accounts
        ).pack(side="left", padx=(0, 8))

        self.btn_copy_gmail = ctk.CTkButton(
            acc_btn_box,
            text="📋 Salin Gmail Utama",
            fg_color="#37474F",
            hover_color="#263238",
            command=self._copy_primary_gmail
        )
        self.btn_copy_gmail.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            acc_btn_box,
            text="📄 Cetak / Simpan Laporan Akun (.txt)",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self._save_account_report
        ).pack(side="left")

        # GRID FOR CARD 2 (Kontak) & CARD 3 (WhatsApp)
        grid_2col = ctk.CTkFrame(container, fg_color="transparent")
        grid_2col.pack(fill="x", pady=6)
        grid_2col.columnconfigure((0, 1), weight=1)

        # CARD 2: Kontak Telepon .VCF
        c_contact = ctk.CTkFrame(grid_2col, corner_radius=8, fg_color="#1B1B26")
        c_contact.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=4)

        ctk.CTkLabel(
            c_contact,
            text="📇 Ekspor Kontak Telepon (.VCF / vCard)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            c_contact,
            text="Ekstrak seluruh nomor kontak ke file .vcf standard. Kirim ke HP baru, sekali tap langsung terimpor semua!",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E",
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self.lbl_contact_status = ctk.CTkLabel(c_contact, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color="#00FFAA")
        self.lbl_contact_status.pack(anchor="w", padx=14, pady=(0, 4))

        ctk.CTkButton(
            c_contact,
            text="📥 Ekspor Kontak Telepon (.VCF)",
            fg_color="#007ACC",
            hover_color="#005999",
            command=self._backup_contacts
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # CARD 3: WhatsApp Hub (Backup & Safe Restore)
        c_wa = ctk.CTkFrame(grid_2col, corner_radius=8, fg_color="#1B1B26")
        c_wa.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=4)

        ctk.CTkLabel(
            c_wa,
            text="💬 WhatsApp Data Hub (Backup & Restore Aman)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#25D366"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            c_wa,
            text="Amankan & pulihkan database chat (msgstore.db.crypt) antar-HP (Android 10 s/d 15) dengan proteksi overwrite, auto-permission & normalisasi database.",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E",
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self.lbl_wa_status = ctk.CTkLabel(c_wa, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color="#00FFAA")
        self.lbl_wa_status.pack(anchor="w", padx=14, pady=(0, 4))

        wa_btn_box = ctk.CTkFrame(c_wa, fg_color="transparent")
        wa_btn_box.pack(fill="x", padx=14, pady=(0, 12))

        self.btn_backup_wa = ctk.CTkButton(
            wa_btn_box,
            text="💾 Backup WA",
            fg_color="#1B5E20",
            hover_color="#0D3812",
            width=110,
            command=self._backup_whatsapp_data
        )
        self.btn_backup_wa.pack(side="left", padx=(0, 6))

        self.btn_restore_wa = ctk.CTkButton(
            wa_btn_box,
            text="🔄 Restore ke HP Baru",
            fg_color="#00695C",
            hover_color="#004D40",
            command=self._open_whatsapp_restore_modal
        )
        self.btn_restore_wa.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            wa_btn_box,
            text="📂 Buka",
            fg_color="#37474F",
            hover_color="#263238",
            width=70,
            command=self._open_whatsapp_folder
        ).pack(side="left")

        # CARD 3B: Backup Seluruh Foto .JPG (Multi-Folder Deep Scan)
        c_jpg = ctk.CTkFrame(grid_2col, corner_radius=8, fg_color="#1B1B26")
        c_jpg.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(6, 2))

        ctk.CTkLabel(
            c_jpg,
            text="🖼️ Backup Seluruh Foto (.JPG / .JPEG) dari Semua Folder",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF9800"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            c_jpg,
            text="Pindai seluruh penyimpanan HP (bukan cuma DCIM kamera, tapi mencakup WhatsApp, Telegram, Pictures, Download, Bluetooth, dll).\n"
                 "Hasil backup disimpan rapi terpisah dalam subfolder sesuai nama folder aslinya (tidak ditumpuk di satu folder).",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E",
            wraplength=680,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self.lbl_jpg_status = ctk.CTkLabel(c_jpg, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color="#00FFAA")
        self.lbl_jpg_status.pack(anchor="w", padx=14, pady=(0, 4))

        jpg_btn_box = ctk.CTkFrame(c_jpg, fg_color="transparent")
        jpg_btn_box.pack(fill="x", padx=14, pady=(0, 12))

        self.btn_backup_jpg = ctk.CTkButton(
            jpg_btn_box,
            text="📥 Backup Seluruh File .JPG Sekarang",
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self._backup_all_jpg_photos
        )
        self.btn_backup_jpg.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            jpg_btn_box,
            text="📂 Buka Folder Foto",
            fg_color="#37474F",
            hover_color="#263238",
            command=self._open_photo_folder
        ).pack(side="left")

        # CARD 4: ONE-CLICK FULL DATA RESCUE
        card_full = ctk.CTkFrame(container, corner_radius=8, fg_color="#251E14", border_width=1, border_color="#FF9800")
        card_full.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_full,
            text="⚡ 1-KLIK PENYELAMATAN DATA LENGKAP (FULL RESCUE)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFA726"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card_full,
            text="Penyelamatan data kilat sekali klik: Otomatis mencari akun Gmail, mengekspor buku kontak .vcf, menyalin seluruh foto .jpg dari SEMUA folder ke subfolder terpisah (DCIM, WhatsApp, Pictures, dll), dan dokumen penting ke satu folder pasien yang rapi.",
            font=ctk.CTkFont(size=11),
            text_color="#C0B090",
            wraplength=700,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        self.lbl_rescue_status = ctk.CTkLabel(card_full, text="Siap menjalankan full rescue.", font=ctk.CTkFont(size=11, slant="italic"), text_color="#FFA726")
        self.lbl_rescue_status.pack(anchor="w", padx=15, pady=(0, 8))

        full_btn_box = ctk.CTkFrame(card_full, fg_color="transparent")
        full_btn_box.pack(fill="x", padx=15, pady=(0, 12))

        self.btn_full_rescue = ctk.CTkButton(
            full_btn_box,
            text="🚀 JALANKAN 1-KLIK RESCUE DATA",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#E65100",
            hover_color="#BF360C",
            command=self._start_full_data_rescue
        )
        self.btn_full_rescue.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            full_btn_box,
            text="📂 Buka Folder Hasil Backup",
            fg_color="#37474F",
            hover_color="#263238",
            command=self._open_backup_folder
        ).pack(side="left")

        # CARD 5: SCREEN MIRRORING & SCREENSHOT
        card_scrcpy = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        card_scrcpy.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_scrcpy,
            text="🖥️ Kontrol Layar PC & Screenshot (Scrcpy)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00D2FF"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card_scrcpy,
            text="Jika LCD pecah tapi touch masih merespon atau butuh mouse PC untuk mengoperasikan HP:",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        mirror_btn_box = ctk.CTkFrame(card_scrcpy, fg_color="transparent")
        mirror_btn_box.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(
            mirror_btn_box,
            text="🚀 Buka Layar HP (Scrcpy)",
            fg_color="#007ACC",
            hover_color="#005999",
            command=self._launch_scrcpy_mirror
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            mirror_btn_box,
            text="📸 Tangkap Gambar Layar (Screenshot)",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self._take_quick_screenshot
        ).pack(side="left")

        # CARD 6: PINTASAN BYPASS FRP & RESET KUNCI LAYAR
        card_frp = ctk.CTkFrame(container, corner_radius=8, fg_color="#181824", border_width=1, border_color="#3F51B5")
        card_frp.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card_frp,
            text="🔓 Pintasan Bypass FRP (Google Lock) & Reset Kunci Layar",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#7986CB"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card_frp,
            text="Alat bantu teknisi saat HP nyangkut di Setup Wizard (FRP) atau lupa PIN/Pola tanpa menghapus data foto & kontak:",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E9E",
            wraplength=680,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 8))

        frp_box1 = ctk.CTkFrame(card_frp, fg_color="transparent")
        frp_box1.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkButton(
            frp_box1,
            text="🌐 Buka YouTube / Chrome (MTP/ADB)",
            fg_color="#3949AB",
            hover_color="#283593",
            command=lambda: self._trigger_frp_browser("youtube")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frp_box1,
            text="⚙️ Buka Menu Pengaturan HP",
            fg_color="#303F9F",
            hover_color="#1A237E",
            command=lambda: self._trigger_frp_browser("settings")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frp_box1,
            text="⚡ Lewati Setup Wizard (ADB Direct)",
            fg_color="#00897B",
            hover_color="#00695C",
            command=self._trigger_bypass_wizard
        ).pack(side="left")

        frp_box2 = ctk.CTkFrame(card_frp, fg_color="transparent")
        frp_box2.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkButton(
            frp_box2,
            text="🚀 Fastboot Erase FRP (Mode Fastboot)",
            fg_color="#D81B60",
            hover_color="#AD1457",
            command=self._trigger_fastboot_frp
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frp_box2,
            text="🔓 Hapus Kunci Pola/PIN (TWRP / Root - Data Utuh)",
            fg_color="#E53935",
            hover_color="#C62828",
            command=self._trigger_reset_screen_lock
        ).pack(side="left")

        frp_box3 = ctk.CTkFrame(card_frp, fg_color="transparent")
        frp_box3.pack(fill="x", padx=15, pady=(0, 8))

        self.btn_samsung_adb = ctk.CTkButton(
            frp_box3,
            text="⚡ 1-Klik Aktifkan ADB Samsung (Modem AT MTP Port)",
            fg_color="#F57C00",
            hover_color="#E65100",
            font=ctk.CTkFont(weight="bold"),
            command=self._trigger_samsung_enable_adb
        )
        self.btn_samsung_adb.pack(side="left")

        self.lbl_frp_status = ctk.CTkLabel(card_frp, text="", font=ctk.CTkFont(size=11), text_color="#00FFAA", wraplength=680, justify="left")
        self.lbl_frp_status.pack(anchor="w", padx=15, pady=(0, 10))

    # -------------------------------------------------------------
    # TAB 6: CETAK NOTA SERVIS
    # -------------------------------------------------------------
    def _build_tab_receipt(self):
        container = ctk.CTkScrollableFrame(self.tab_receipt, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(container, text="Cetak Nota Servis Berlogo Konter Resmi", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00D2FF").pack(anchor="w", pady=(0, 4))

        form = ctk.CTkFrame(container, corner_radius=8, fg_color="#1B1B26")
        form.pack(fill="x", pady=6)

        self.entry_shop = self._create_input_row(form, "Nama Konter Servis:", "BINTANG REPAIR CELL")
        self.entry_shop_contact = self._create_input_row(form, "Alamat / WhatsApp Konter:", "Jl. Raya Servis No. 12 | WA: 0812-3456-7890")
        self.entry_cust_name = self._create_input_row(form, "Nama Pelanggan:", "Pak Budi")
        self.entry_cust_phone = self._create_input_row(form, "No. HP Pelanggan:", "0857-xxxx-xxxx")
        self.entry_complaint = self._create_input_row(form, "Keluhan Awal:", "HP sering mati sendiri & baterai cepat habis")
        self.entry_price = self._create_input_row(form, "Estimasi Biaya / Pengerjaan:", "Rp 150.000 (Ganti Baterai Original) - 1 Hari")

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", pady=15)

        ctk.CTkButton(
            btn_box,
            text="🖨️ CETAK NOTA SERVIS & DIAGNOSA (HTML / PDF)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#007ACC",
            hover_color="#005999",
            height=40,
            command=self._generate_service_receipt
        ).pack(side="left", padx=(0, 10))

    def _create_input_row(self, parent, label_text, default_val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=8)
        lbl = ctk.CTkLabel(row, text=label_text, width=200, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="#E0E0E0")
        lbl.pack(side="left")
        entry = ctk.CTkEntry(row, height=32, font=ctk.CTkFont(size=12))
        entry.insert(0, default_val)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    # -------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------
    def _build_footer(self):
        footer = ctk.CTkFrame(self, height=26, fg_color="#101018")
        footer.pack(fill="x", side="bottom")

        self.lbl_status = ctk.CTkLabel(footer, text="Siap digunakan.", font=ctk.CTkFont(size=11, slant="italic"), text_color="#808090")
        self.lbl_status.pack(side="left", padx=15, pady=2)

        adb_lbl = ctk.CTkLabel(footer, text=f"ADB: {get_adb_path()}", font=ctk.CTkFont(size=11), text_color="#505060")
        adb_lbl.pack(side="right", padx=15, pady=2)

    def _create_card(self, parent, title, row, col):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color="#1B1B26")
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=4)
        t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color="#00D2FF")
        t_lbl.pack(anchor="w", padx=12, pady=(10, 6))
        content = ctk.CTkLabel(
            card,
            text="Menunggu scan...",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#B0B0C0",
            justify="left",
            anchor="w",
            wraplength=460
        )
        content.pack(anchor="w", fill="x", padx=12, pady=(0, 12))

        def _on_card_resize(e, lbl=content):
            new_wrap = max(360, e.width - 24)
            try:
                if abs(lbl.cget("wraplength") - new_wrap) > 15:
                    lbl.configure(wraplength=new_wrap)
            except Exception:
                pass

        card.bind("<Configure>", _on_card_resize)
        return content

    # -------------------------------------------------------------
    # DAEMONS
    # -------------------------------------------------------------
    def _on_close(self):
        self.monitoring_usb = False
        with self._device_lock:
            if self.hardware_tester:
                try:
                    self.hardware_tester.stop_key_listener()
                    self.hardware_tester.stop_touch_listener()
                except Exception:
                    pass
        self.destroy()

    def _monitor_usb_devices(self):
        last_state = None
        while self.monitoring_usb:
            if not self.is_scanning:
                status = DeviceDetector.get_connected_status()
                state_key = (status["status"], status["type"], str(status["device"]))
                if state_key != last_state:
                    last_state = state_key
                    self.after(0, self._update_connection_ui, status)
            time.sleep(1.8)

    def _monitor_live_power(self):
        while self.monitoring_usb:
            with self._device_lock:
                pm = self.power_monitor
            if pm and not self.is_scanning:
                try:
                    p = pm.read_live_power()
                    if p.get("voltage_mv", 0) > 0:
                        sign = "+" if p.get("is_charging") else "-"
                        txt = f"⚡ Arus: {sign}{p.get('current_ma')} mA | Voltase: {p.get('voltage_v')}V | Suhu: {p.get('temperature_c')}°C ({p.get('charge_speed')})"
                        self.after(0, lambda t=txt: self.lbl_live_power.configure(text=t))
                except Exception:
                    pass
            time.sleep(2.5)

    def _update_connection_ui(self, status):
        try:
            st = status["status"]
            t = status["type"]
            dev = status["device"]

            with self._device_lock:
                if st == "DISCONNECTED":
                    self.current_device = None
                    self.hardware_tester = None
                    self.power_monitor = None
                    self.screen_mirror = None
                    self.reboot_tools = None
                    self.flasher = None
                    self.data_rescue = None
                    self.conn_pill.configure(text="🔴 Menunggu Sambungan Kabel USB...", text_color="#FF6B6B", fg_color="#2A2030")
                    self.lbl_status.configure(text="Belum ada perangkat terhubung.")
                    self.lbl_live_power.configure(text="⚡ Arus Pengisian: -- mA | Voltase: -- V")
                    if hasattr(self, 'lbl_flash_status'):
                        self.lbl_flash_status.configure(text="Status Flashing: Belum ada perangkat terhubung. Siapkan Fastboot atau Sideload.", text_color="#FFAA00")
                elif t == "ADB":
                    self.current_device = dev
                    serial = dev.get("serial")
                    self.hardware_tester = HardwareTester(serial=serial)
                    self.power_monitor = PowerMonitor(serial=serial)
                    self.screen_mirror = ScreenMirrorManager(serial=serial)
                    self.reboot_tools = RebootTools(serial=serial)
                    self.flasher = FirmwareFlasher(serial=serial)
                    self.data_rescue = DataRescueManager(serial=serial)

                    state = dev.get("state", "device")
                    model = dev.get("model", "Android")
                    if state == "device":
                        self.conn_pill.configure(text=f"🟢 Terhubung: {model} (ADB)", text_color="#00FFAA", fg_color="#18382B")
                        self.lbl_status.configure(text="Perangkat siap dioperasikan.")
                        if hasattr(self, 'lbl_flash_status'):
                            self.lbl_flash_status.configure(text="Mode ADB Terhubung. Klik '⚡ Masuk Fastboot Mode' untuk mulai flashing partisi/ROM.", text_color="#00D2FF")
                    elif state == "sideload":
                        self.conn_pill.configure(text=f"📦 Terhubung: Mode Recovery Sideload ({serial})", text_color="#7B1FA2", fg_color="#2A1838")
                        if hasattr(self, 'lbl_flash_status'):
                            self.lbl_flash_status.configure(text="✅ Mode Recovery Sideload Aktif! Siap pasang file firmware .zip OTA/Recovery.", text_color="#00FFAA")
                    elif state == "unauthorized":
                        self.conn_pill.configure(text=f"🟡 Terhubung: {model} (Izinkan USB Debugging!)", text_color="#FFD600", fg_color="#36321A")
                elif t == "FASTBOOT":
                    self.current_device = dev
                    serial = dev.get("serial")
                    self.flasher = FirmwareFlasher(serial=serial)
                    self.conn_pill.configure(text=f"⚡ Terhubung: Fastboot Mode ({serial})", text_color="#FF9800", fg_color="#362818")
                    if hasattr(self, 'lbl_flash_status'):
                        self.lbl_flash_status.configure(text="✅ Mode Fastboot Aktif! Siap flash partisi (boot, recovery, vbmeta) atau script ROM.", text_color="#00FFAA")
                elif t == "COM":
                    self.current_device = dev
                    self.flasher = None
                    self.conn_pill.configure(text=f"🟣 Emergency Port: {dev.get('title')} ({dev.get('port')})", text_color="#E040FB", fg_color="#321838")
                    self.lbl_status.configure(text=f"Mode darurat chipset terdeteksi: {dev.get('title')}")
                    if hasattr(self, 'lbl_flash_status'):
                        self.lbl_flash_status.configure(text=f"Port Darurat Chipset ({dev.get('title')}). Mode EDL/BROM terdeteksi.", text_color="#E040FB")

            if hasattr(self, 'selected_ampere'):
                self._on_dead_diagnose_calculate()
        except Exception:
            pass

    # -------------------------------------------------------------
    # ACTION HANDLERS
    # -------------------------------------------------------------
    def start_scan(self):
        if self.is_scanning:
            return
        status = DeviceDetector.get_connected_status()
        if status["status"] == "DISCONNECTED":
            messagebox.showwarning("Kabel Belum Terpasang", "Sambungkan HP Android via kabel USB terlebih dahulu!")
            return

        self.is_scanning = True
        self.btn_scan.configure(state="disabled", text="⏳ SEDANG MEMINDAI...")
        self.lbl_status.configure(text="Mengambil data diagnosa komprehensif...")

        threading.Thread(target=self._run_scan_worker, args=(status,), daemon=True).start()

    def _run_scan_worker(self, conn_status):
        t = conn_status["type"]
        dev = conn_status["device"]
        result = {}
        try:
            if t == "ADB":
                scanner = AdbHardwareScanner(serial=dev.get("serial"))
                result = scanner.scan_all()
            elif t == "FASTBOOT":
                scanner = FastbootScanner(serial=dev.get("serial"))
                result = scanner.scan()
            elif t == "COM":
                result = {"mode": "EMERGENCY_COM", "title": dev.get("title"), "port": dev.get("port"), "diagnosis": dev.get("diagnosis")}
        except Exception as e:
            result = {"error": str(e)}

        self.after(0, self._render_scan_results, result)

    def _render_scan_results(self, data):
        self.is_scanning = False
        self.btn_scan.configure(state="normal", text="🔍 MULAI SCAN HARDWARE LENGKAP")
        self.last_scan_data = data
        self.btn_save_txt.configure(state="normal")
        self.lbl_status.configure(text="Pemindaian selesai!")

        if "device_info" in data:
            d = data["device_info"]
            g_accs = d.get('google_accounts_list', [])
            if not g_accs and d.get('google_accounts'):
                val = d.get('google_accounts')
                if "Tidak Terdeteksi" not in val:
                    g_accs = [x.strip() for x in val.split(',') if x.strip()]
            if len(g_accs) > 1:
                g_str = f"{g_accs[0]} (+{len(g_accs)-1} akun lainnya)"
            elif len(g_accs) == 1:
                g_str = g_accs[0]
            else:
                g_str = d.get('google_accounts', '-')

            imei_str = f"IMEI 1: {d.get('imei1', '-')}"
            if d.get('imei2') and d.get('imei2') != "-":
                imei_str += f" | IMEI 2: {d.get('imei2')}"

            self.card_dev.configure(
                text=f"• Merk / Model   : {d.get('brand')} {d.get('model')}\n"
                     f"• Chipset / Board: {d.get('chipset')} ({d.get('manufacturer')})\n"
                     f"• Android / Patch: v{d.get('android_version')} (Patch: {d.get('security_patch')})\n"
                     f"• RAM            : Total {d.get('ram_total')} | Sisa {d.get('ram_available')}\n"
                     f"• Baseband/Modem : {d.get('baseband_status')}\n"
                     f"• No. IMEI       : {imei_str}\n"
                     f"• Diagnosa RF    : {d.get('signal_diagnosis', '-')}\n"
                     f"• Akun Google    : {g_str}"
            )

            b = data.get("battery", {})
            self.card_bat.configure(
                text=f"• Level / Voltase: {b.get('level', '-')} | {b.get('voltage', '-')}\n"
                     f"• Kesehatan (SoH): {b.get('health_pct', 'Unknown')} [{b.get('health', 'Bagus')}]\n"
                     f"• Siklus Cas     : {b.get('cycle_count', '-')}\n"
                     f"• Kapasitas mAh  : {b.get('current_capacity', '-')} / Asli {b.get('design_capacity', '-')}\n"
                     f"• Penurunan Daya : {b.get('capacity_loss', '-')}\n"
                     f"• Suhu Termal    : {b.get('temperature', '-')}\n"
                     f"• Evaluasi       : [{b.get('status_flag', 'OK')}] {b.get('note', '-')}"
            )

            s = data.get("storage", {})
            self.card_stor.configure(
                text=f"• Keausan Memori : {s.get('wear_percentage')}\n"
                     f"• Blok Cadangan  : {s.get('pre_eol_status')}\n"
                     f"• Uji I/O Speed  : {s.get('io_health')}\n"
                     f"• Ruang Storage  : {s.get('free_space')}\n"
                     f"• Analisa Teknis : {' '.join(s.get('notes', []))}"
            )

            disp = data.get("display", {})
            touch = data.get("touchscreen", {})
            cams = data.get("cameras", {})
            sens = data.get("sensors", {})
            conn = data.get("connectivity", {})
            s_text = sens.get('sensors', '-')
            if len(s_text) > 42:
                s_text = f"{sens.get('detected_count', '')} Sensor Aktif ({s_text[:38]}...)"

            self.card_periph.configure(
                text=f"• Display        : {disp.get('resolution')} ({disp.get('density')})\n"
                     f"• IC Touchscreen : {touch.get('controller')}\n"
                     f"• Modul Kamera   : {cams.get('count')} Modul ({cams.get('note')})\n"
                     f"• Sensor Fisik   : {s_text}\n"
                     f"• Wi-Fi MAC      : {conn.get('wifi_status')}"
            )

            faults = data.get("hardware_faults", [])
            self.txt_faults.configure(state="normal")
            self.txt_faults.delete("1.0", "end")
            if faults:
                self.txt_faults.insert("end", "⚠️ PERINGATAN KERNEL: TERDETEKSI KESALAHAN BUS HARDWARE:\n\n")
                for f in faults:
                    self.txt_faults.insert("end", f"🚨 [{f.get('category')}]\n   Detail Log: {f.get('log')}\n\n")
            else:
                self.txt_faults.insert("end", "✅ KERNEL LOG BERSIH:\nTidak terdeteksi error bus I2C/SPI fatal, sensor kamera, atau crash audio codec.")
            self.txt_faults.configure(state="disabled")

        elif "mode" in data and "FASTBOOT" in data["mode"]:
            prod = data.get("product", "Unknown")
            bl_ver = data.get("bootloader_version", "Unknown")
            bb_ver = data.get("baseband_version", "Unknown")
            unl = data.get("unlocked", "Unknown")
            sec = data.get("secure", "Unknown")
            v_bat = data.get("battery_voltage", "Unknown")

            self.card_dev.configure(text=f"• Status Mode    : FASTBOOT (BOOTLOADER)\n• Tipe Product   : {prod}\n• Bootloader Ver : {bl_ver}\n• Baseband Ver   : {bb_ver}\n• Status Lock    : Unlocked = {unl}")
            self.card_bat.configure(text=f"• Tegangan Baterai: {v_bat}\n• Status Baterai : [{data.get('status_flag', 'OK')}]\n• Rekomendasi   : Siap untuk proses flashing partisi")
            self.card_stor.configure(text=f"• Target Storage : Partisi Internal ROM\n• Secure Boot    : {sec}\n• Kesiapan Flash : Bootloader Aktif & Merespon")
            self.card_periph.configure(text="• Mode Fastboot Aktif (ADB Shell dinonaktifkan)\n• Pengujian layar/sensor hanya bisa dilakukan di mode ADB biasa.\n• Buka tab 'Flashing' untuk flash boot, recovery, atau ROM.")

            self.txt_faults.configure(state="normal")
            self.txt_faults.delete("1.0", "end")
            self.txt_faults.insert("end", "⚡ DIAGNOSA MODE FASTBOOT:\n\n")
            for note in data.get("notes", []):
                self.txt_faults.insert("end", f"• {note}\n")
            raw_vars = data.get("raw_vars", {})
            if raw_vars:
                self.txt_faults.insert("end", f"\nParameter Fastboot Terbaca ({len(raw_vars)} variabel):\n")
                for k, v in list(raw_vars.items())[:10]:
                    self.txt_faults.insert("end", f"  [{k}] = {v}\n")
            self.txt_faults.configure(state="disabled")

        elif "mode" in data and data["mode"] == "EMERGENCY_COM":
            title = data.get("title", "Port Darurat")
            port = data.get("port", "COM")
            diag = data.get("diagnosis", "-")

            self.card_dev.configure(text=f"• Status Mode    : LOW-LEVEL CHIPSET PORT\n• Port Serial    : {port}\n• Chipset Mode   : {title}\n• Kondisi        : Emergency BootROM Aktif")
            self.card_bat.configure(text="• Level Baterai  : Tidak Terbaca (Mode Chipset)\n• Saran          : Pastikan baterai minimal terisi 3.7V")
            self.card_stor.configure(text="• Storage Status : eMMC / UFS Handshake Mode\n• Indikasi       : HP Siap Flash via Tool Resmi / Test Point")
            self.card_periph.configure(text="• Layar HP Gelap Total (Tidak ada tampilan)\n• Komunikasi via COM Port langsung ke CPU/PMIC.")

            self.txt_faults.configure(state="normal")
            self.txt_faults.delete("1.0", "end")
            self.txt_faults.insert("end", f"🟣 DETEKSI MODE DARURAT CHIPSET ({title}):\n\n{diag}\n\n• Gunakan tab 'Test Point (TP)' untuk melihat letak titik jumper.\n• Gunakan tab 'Driver USB' untuk memastikan driver filter LibUSB terpasang.")
            self.txt_faults.configure(state="disabled")

    def save_txt_report(self):
        if not self.last_scan_data:
            return
        txt = ReportGenerator.generate_text_report(self.last_scan_data)
        saved = ReportGenerator.save_report_to_file(txt)
        if saved:
            messagebox.showinfo("Laporan Disimpan", f"Laporan tersimpan di:\n{os.path.abspath(saved)}")
        else:
            messagebox.showerror("Gagal Menyimpan", "Gagal menyimpan file laporan diagnosa ke disk!")

    # -------------------------------------------------------------
    # TESTS & REBOOT HANDLERS
    # -------------------------------------------------------------
    def _trigger_vibrator(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        def worker():
            ok, msg = self.hardware_tester.test_vibrator(1500)
            self.after(0, lambda: self.lbl_vib_status.configure(text=f"✅ {msg}"))
            self.after(4000, lambda: self.lbl_vib_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_torch(self, state):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        def worker():
            ok, msg = self.hardware_tester.toggle_torch(state)
            self.after(0, lambda: self.lbl_torch_status.configure(text=f"💡 {msg}"))
            self.after(5000, lambda: self.lbl_torch_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_audio(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        def worker():
            ok, msg = self.hardware_tester.test_speaker()
            self.after(0, lambda: self.lbl_audio_status.configure(text=f"🔊 {msg}"))
            self.after(4000, lambda: self.lbl_audio_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_earpiece(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        def worker():
            ok, msg = self.hardware_tester.test_earpiece()
            self.after(0, lambda: self.lbl_audio_status.configure(text=f"📞 {msg}"))
            self.after(5000, lambda: self.lbl_audio_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_mic(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        self.lbl_audio_status.configure(text="🎙️ Sedang merekam 3 detik... Ucapkan suara di dekat mic HP!")
        def worker():
            ok, msg = self.hardware_tester.test_mic_loopback()
            self.after(0, lambda: self.lbl_audio_status.configure(text=f"🎙️ {msg}"))
            self.after(6000, lambda: self.lbl_audio_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_color(self, hex_color):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        def worker():
            ok, msg = self.hardware_tester.test_lcd_color(hex_color)
            self.after(0, lambda: self.lbl_lcd_status.configure(text=f"🎨 {msg}"))
            self.after(5000, lambda: self.lbl_lcd_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _toggle_key_listener(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        if self.hardware_tester._listening:
            self.hardware_tester.stop_key_listener()
            self.btn_listen_keys.configure(text="▶️ Aktifkan Deteksi Tombol", fg_color="#007ACC")
        else:
            self.btn_listen_keys.configure(text="⏹️ Hentikan Deteksi Tombol", fg_color="#C62828")
            self.hardware_tester.start_key_listener(self._on_physical_key_event)

    def _on_physical_key_event(self, key_name, action):
        def update():
            if key_name == "VOLUME_UP":
                self.badge_vol_up.configure(fg_color="#2E7D32", text_color="#FFF")
                self.after(600, lambda: self.badge_vol_up.configure(fg_color="#2B2B36", text_color="#888"))
            elif key_name == "VOLUME_DOWN":
                self.badge_vol_down.configure(fg_color="#2E7D32", text_color="#FFF")
                self.after(600, lambda: self.badge_vol_down.configure(fg_color="#2B2B36", text_color="#888"))
            elif key_name == "POWER":
                self.badge_power.configure(fg_color="#2E7D32", text_color="#FFF")
                self.after(600, lambda: self.badge_power.configure(fg_color="#2B2B36", text_color="#888"))
        self.after(0, update)

    def _toggle_pointer_location(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return

        is_active = self.hardware_tester.get_pointer_location_state()
        new_state = not is_active

        def worker():
            ok, msg = self.hardware_tester.set_pointer_location(new_state)
            def update_ui():
                if new_state:
                    self.btn_toggle_pointer.configure(text="🛑 Matikan Jejak Sentuh", fg_color="#C62828")
                    self.lbl_touch_status.configure(text=f"📍 {msg}")
                else:
                    self.btn_toggle_pointer.configure(text="📍 Aktifkan Jejak Sentuh (Pointer Location)", fg_color="#00838F")
                    self.lbl_touch_status.configure(text=f"🛑 {msg}")
            self.after(0, update_ui)
        threading.Thread(target=worker, daemon=True).start()

    def _launch_touch_grid(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        self.lbl_touch_status.configure(text="⏳ Mempersiapkan papan kisi uji sentuh di layar HP...")
        def worker():
            ok, msg = self.hardware_tester.launch_touch_grid_test()
            self.after(0, lambda: self.lbl_touch_status.configure(text=f"🟩 {msg}"))
        threading.Thread(target=worker, daemon=True).start()

    def _toggle_touch_monitor(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return

        if self.hardware_tester._touch_listening:
            self.hardware_tester.stop_touch_listener()
            self.btn_touch_monitor.configure(text="📡 Pantau Sentuhan di PC", fg_color="#3949AB")
            self.lbl_touch_status.configure(text="⏹️ Pemantauan sentuhan real-time dihentikan.")
        else:
            self.btn_touch_monitor.configure(text="⏹️ Berhenti Pantau", fg_color="#C62828")
            self.lbl_touch_status.configure(text="📡 Mendengarkan input sentuhan digitizer... Silakan sentuh layar HP.")
            self.hardware_tester.start_touch_listener(self._on_touch_telemetry_event)

    def _on_touch_telemetry_event(self, x, y, is_down, count):
        def update():
            state_str = "JARI MENYENTUH (DOWN)" if is_down else "LEPAS (UP)"
            color_str = "#00FFAA" if is_down else "#A0A0B0"
            self.lbl_touch_status.configure(
                text=f"📡 Event #{count} | Koordinat: X={x}, Y={y} | Status: {state_str}",
                text_color=color_str
            )
        self.after(0, update)

    def _launch_factory_touch_menu(self):
        self._open_factory_test_modal()

    def _open_factory_test_modal(self):
        if not self.hardware_tester:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return

        detected = self.hardware_tester.detect_device_brand()
        brand_map = {
            "xiaomi": "Xiaomi / Redmi / POCO",
            "samsung": "Samsung Galaxy",
            "oppo": "Oppo / Realme / OnePlus",
            "vivo": "Vivo / iQOO",
            "transsion": "Infinix / Tecno / Itel",
            "universal": "Universal Android"
        }
        detected_name = brand_map.get(detected, detected.upper())

        modal = ctk.CTkToplevel(self)
        modal.title("⚙️ Buka Menu Tes Hardware Pabrik (CIT / Factory Mode)")
        modal.geometry("540x530")
        modal.minsize(500, 480)
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text="⚙️ MENU TES HARDWARE PABRIK (DIALER & BROADCAST)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00FFAA"
        ).pack(padx=20, pady=(15, 2), anchor="w")

        ctk.CTkLabel(
            modal,
            text="Membuka menu diagnostik layar & sensor bawaan OEM via Telephony Secret Code & Activity Intent:",
            font=ctk.CTkFont(size=11),
            text_color="#A0A0B0",
            wraplength=480,
            justify="left"
        ).pack(padx=20, pady=(0, 10), anchor="w")

        det_frame = ctk.CTkFrame(modal, fg_color="#1E1E2A", corner_radius=6)
        det_frame.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            det_frame,
            text=f"📱 Terdeteksi: {detected_name.upper()} (Otomatis)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFD54F"
        ).pack(padx=14, pady=8, anchor="w")

        def trigger_brand(brand_key):
            self.lbl_touch_status.configure(text=f"⏳ Mengirim sinyal tes pabrik ({brand_key})...")
            modal.destroy()
            def worker():
                ok, msg = self.hardware_tester.launch_factory_touch_test(target_brand=brand_key)
                self.after(0, lambda: self.lbl_touch_status.configure(text=f"⚙️ {msg}"))
            threading.Thread(target=worker, daemon=True).start()

        ctk.CTkButton(
            modal,
            text=f"🚀 Luncurkan Menu Sesuai Brand Terdeteksi ({detected_name})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#00897B",
            hover_color="#00695C",
            height=36,
            command=lambda: trigger_brand(detected)
        ).pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(modal, text="Atau pilih menu merk manual di bawah ini:", font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", padx=20, pady=(0, 6))

        grid = ctk.CTkFrame(modal, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        brands_list = [
            ("🟠 Xiaomi / Redmi / POCO (CIT *#*#6484#*#*)", "xiaomi", "#E65100"),
            ("🔵 Samsung Galaxy (*#0*# & *#7353#)", "samsung", "#0D47A1"),
            ("🟢 Oppo / Realme (Engineer *#899#)", "oppo", "#1B5E20"),
            ("🔷 Vivo / iQOO (Factory *#558#)", "vivo", "#006064"),
            ("🟣 Infinix / Tecno (*#*#83781#*#*)", "transsion", "#4A148C"),
            ("⚪ Universal Android (*#*#4636#*#*)", "universal", "#37474F")
        ]

        for text_btn, b_key, col in brands_list:
            ctk.CTkButton(
                grid,
                text=text_btn,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=col,
                anchor="w",
                height=32,
                command=lambda k=b_key: trigger_brand(k)
            ).pack(fill="x", pady=3)

    def _cmd_reboot_normal(self):
        if self.reboot_tools and messagebox.askyesno("Konfirmasi", "Reboot HP sekarang?"):
            self.reboot_tools.reboot_normal()

    def _cmd_reboot_recovery(self):
        if self.reboot_tools and messagebox.askyesno("Konfirmasi", "Reboot ke Recovery?"):
            self.reboot_tools.reboot_recovery()

    def _cmd_reboot_fastboot(self):
        if self.reboot_tools and messagebox.askyesno("Konfirmasi", "Reboot ke Fastboot?"):
            self.reboot_tools.reboot_bootloader()

    def _cmd_reboot_edl(self):
        if self.reboot_tools and messagebox.askyesno("Konfirmasi", "Reboot ke EDL 9008?"):
            self.reboot_tools.reboot_edl()

    def _cmd_wakeup_screen(self):
        if self.reboot_tools:
            self.reboot_tools.wakeup_screen()

    def _cmd_power_off(self):
        if self.reboot_tools and messagebox.askyesno("Konfirmasi", "Matikan HP (Shutdown)?"):
            self.reboot_tools.power_off()

    def _launch_scrcpy_mirror(self):
        if not self.screen_mirror:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        ok, msg = self.screen_mirror.launch_scrcpy()
        if not ok:
            messagebox.showinfo("Scrcpy Belum Terpasang", "Letakkan 'scrcpy.exe' di folder 'bin' aplikasi ini untuk mengaktifkan screen mirror.")

    def _take_quick_screenshot(self):
        if not self.screen_mirror:
            messagebox.showwarning("Koneksi", "Sambungkan HP via ADB terlebih dahulu!")
            return
        saved_file = self.screen_mirror.take_screenshot()
        if saved_file and os.path.exists(saved_file):
            messagebox.showinfo("Screenshot", f"Tersimpan di:\n{os.path.abspath(saved_file)}")
            try:
                os.startfile(os.path.abspath(saved_file))
            except Exception:
                pass
        else:
            messagebox.showerror("Gagal Screenshot", "Gagal mengambil gambar layar. Pastikan layar HP menyala dan tidak terkunci.")

    # -------------------------------------------------------------
    # DATA RESCUE ACTION HANDLERS
    # -------------------------------------------------------------
    def _get_data_rescue(self):
        with self._device_lock:
            if not self.data_rescue:
                serial = self.current_device.get("serial") if self.current_device else None
                self.data_rescue = DataRescueManager(serial=serial)
            return self.data_rescue

    def _detect_accounts(self):
        if not self.current_device:
            messagebox.showwarning("Koneksi", "Sambungkan HP Android via kabel USB terlebih dahulu!")
            return

        def worker():
            rescue = self._get_data_rescue()
            accounts = rescue.get_accounts()
            self._last_detected_accounts = accounts

            def update_ui():
                self.txt_accounts_display.configure(state="normal")
                self.txt_accounts_display.delete("1.0", "end")
                owner = accounts.get("device_owner")
                google_accs = accounts.get("google", [])
                wa_accs = accounts.get("whatsapp", [])
                xiaomi_accs = accounts.get("xiaomi", [])
                samsung_accs = accounts.get("samsung", [])
                vivo_accs = accounts.get("vivo", [])
                others = accounts.get("others", [])

                if owner:
                    self.txt_accounts_display.insert("end", f"👤 PROFIL PEMILIK: {owner}\n\n")

                if google_accs:
                    self.txt_accounts_display.insert("end", f"📧 AKUN GOOGLE (GMAIL) TERDETEKSI ({len(google_accs)} akun):\n")
                    for g in google_accs:
                        self.txt_accounts_display.insert("end", f"  ▶ {g}\n")
                else:
                    self.txt_accounts_display.insert("end", "📧 Akun Google: Tidak terdeteksi atau belum login.\n")

                if wa_accs:
                    self.txt_accounts_display.insert("end", f"\n💬 WHATSAPP: {', '.join(wa_accs)}\n")
                if xiaomi_accs:
                    self.txt_accounts_display.insert("end", f"📱 MI ACCOUNT (XIAOMI): {', '.join(xiaomi_accs)}\n")
                if samsung_accs:
                    self.txt_accounts_display.insert("end", f"📱 SAMSUNG ACCOUNT: {', '.join(samsung_accs)}\n")
                if vivo_accs:
                    self.txt_accounts_display.insert("end", f"📱 VIVO ACCOUNT ID: {', '.join(vivo_accs)}\n")
                if others:
                    self.txt_accounts_display.insert("end", f"\n🌐 APLIKASI LAIN ({len(others)} akun terdaftar):\n")
                    for o in others[:6]:
                        self.txt_accounts_display.insert("end", f"  • {o}\n")

                self.txt_accounts_display.configure(state="disabled")

            self.after(0, update_ui)

        self.txt_accounts_display.configure(state="normal")
        self.txt_accounts_display.delete("1.0", "end")
        self.txt_accounts_display.insert("1.0", "⏳ Sedang memindai AccountManager Android via dumpsys...")
        self.txt_accounts_display.configure(state="disabled")
        threading.Thread(target=worker, daemon=True).start()

    def _copy_primary_gmail(self):
        accounts = getattr(self, '_last_detected_accounts', None)
        if not accounts or not accounts.get("google"):
            messagebox.showinfo("Akun Google", "Lakukan 'Pindai Akun Sekarang' terlebih dahulu!")
            return
        primary_gmail = accounts["google"][0]
        self.clipboard_clear()
        self.clipboard_append(primary_gmail)
        messagebox.showinfo("Tersalin", f"Akun Gmail berhasil disalin ke clipboard:\n{primary_gmail}")

    def _save_account_report(self):
        if not self.current_device:
            messagebox.showwarning("Koneksi", "Sambungkan HP via USB terlebih dahulu!")
            return
        rescue = self._get_data_rescue()
        model = self.current_device.get("model", "Android")
        saved_file = rescue.generate_account_summary_file(device_model=model)
        if saved_file and os.path.exists(saved_file):
            messagebox.showinfo("Laporan Disimpan", f"Daftar akun berhasil disimpan:\n{os.path.abspath(saved_file)}")
            try:
                os.startfile(os.path.abspath(saved_file))
            except Exception:
                pass
        else:
            messagebox.showerror("Gagal", "Gagal menyimpan laporan akun!")

    def _backup_contacts(self):
        if not self.current_device:
            messagebox.showwarning("Koneksi", "Sambungkan HP via USB terlebih dahulu!")
            return

        self.lbl_contact_status.configure(text="⏳ Mengekspor kontak telepon via Content Provider...")
        def worker():
            rescue = self._get_data_rescue()
            ok, res_path, count = rescue.export_contacts_vcf()
            def finish():
                if ok:
                    self.lbl_contact_status.configure(text=f"✅ Berhasil ekspor {count} kontak (.vcf)!")
                    messagebox.showinfo(
                        "Ekspor Kontak Sukses",
                        f"Berhasil mengekstrak {count} kontak telepon!\n\n"
                        f"File .VCF siap kirim ke HP baru:\n{os.path.abspath(res_path)}"
                    )
                    try:
                        os.startfile(os.path.dirname(os.path.abspath(res_path)))
                    except Exception:
                        pass
                else:
                    self.lbl_contact_status.configure(text=f"❌ {res_path}")
                    messagebox.showwarning("Kontak Telepon", res_path)
            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _backup_whatsapp_data(self):
        if not self.current_device:
            messagebox.showwarning("Koneksi", "Sambungkan HP via USB terlebih dahulu!")
            return

        choice = messagebox.askyesnocancel(
            "Pilih Mode Backup WhatsApp",
            "Pilih metode pengamanan data WhatsApp:\n\n"
            "• Klik [YES] untuk BACKUP LENGKAP (Database Chat + Seluruh Media Foto/Video)\n"
            "  *Memakan waktu lebih lama tergantung kapasitas media customer*\n\n"
            "• Klik [NO] untuk HANYA DATABASE CHAT (msgstore.db.crypt)\n"
            "  *Rekomendasi konter: Super cepat (~10 detik), ringan, riwayat chat 100% aman*\n\n"
            "• Klik [CANCEL] untuk Membatalkan."
        )

        if choice is None:
            return

        b_type = "all" if choice is True else "db_only"
        type_str = "Lengkap (Chat + Media)" if b_type == "all" else "Hanya Database Chat"

        self.btn_backup_wa.configure(state="disabled")
        self.lbl_wa_status.configure(text=f"⏳ Memulai backup WhatsApp ({type_str})...")

        def worker():
            rescue = self._get_data_rescue()
            def on_prog(msg):
                self.after(0, lambda m=msg: self.lbl_wa_status.configure(text=m))

            ok, msg = rescue.backup_whatsapp(backup_type=b_type, on_progress=on_prog)
            def finish():
                self.btn_backup_wa.configure(state="normal")
                if ok:
                    self.lbl_wa_status.configure(text="✅ Backup WhatsApp selesai!")
                    messagebox.showinfo("Backup WhatsApp Selesai", msg)
                else:
                    self.lbl_wa_status.configure(text="❌ Gagal backup WhatsApp.")
                    messagebox.showwarning("Backup WhatsApp", msg)
            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _open_whatsapp_folder(self):
        cust_dir = os.path.join(APP_DIR, "customer_backup")
        target_dir = cust_dir
        if os.path.exists(cust_dir):
            for root, dirs, _ in os.walk(cust_dir):
                for d in dirs:
                    if "whatsapp" in d.lower():
                        target_dir = os.path.join(root, d)
                        break
                if target_dir != cust_dir:
                    break
        try:
            os.startfile(os.path.abspath(target_dir))
        except Exception:
            pass

    def _open_whatsapp_restore_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("🔄 Restore Aman Database WhatsApp ke HP Baru")
        modal.geometry("640x680")
        modal.minsize(580, 600)
        modal.grab_set()

        t_lbl = ctk.CTkLabel(
            modal,
            text="🔄 RESTORE DATABASE WHATSAPP KE HP BARU / RESET",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00FFAA"
        )
        t_lbl.pack(padx=20, pady=(15, 2), anchor="w")

        sub_lbl = ctk.CTkLabel(
            modal,
            text="Menyuntikkan database pesan (msgstore.db.crypt) ke direktori WhatsApp HP target secara aman dengan proteksi overwrite dan auto-permission.",
            font=ctk.CTkFont(size=11),
            text_color="#A0A0B0",
            wraplength=600,
            justify="left"
        )
        sub_lbl.pack(padx=20, pady=(0, 10), anchor="w")

        scroll = ctk.CTkScrollableFrame(modal, fg_color="#13131A", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Target Phone Banner
        dev_frame = ctk.CTkFrame(scroll, fg_color="#1E1E2A", corner_radius=6)
        dev_frame.pack(fill="x", padx=10, pady=(10, 8))

        if self.current_device:
            dev_text = f"📱 HP Target Terhubung: {self.current_device.get('model', 'Android')} (Serial: {self.current_device.get('serial', '-')})"
            dev_color = "#00FFAA"
        else:
            dev_text = "⚠️ HP Target Belum Terdeteksi! Colokkan HP baru via USB (Aktifkan USB Debugging)."
            dev_color = "#FF9800"

        ctk.CTkLabel(dev_frame, text=dev_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=dev_color).pack(padx=12, pady=8, anchor="w")

        # 1. Source Folder Picker
        ctk.CTkLabel(scroll, text="📁 1. Folder Cadangan WhatsApp di Komputer:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
        
        f_pick = ctk.CTkFrame(scroll, fg_color="transparent")
        f_pick.pack(fill="x", padx=10, pady=(0, 4))

        # Auto-detect newest backup folder
        default_folder = ""
        cust_dir = os.path.join(APP_DIR, "customer_backup")
        if os.path.exists(cust_dir):
            newest_mtime = 0
            for root, dirs, files in os.walk(cust_dir):
                for f in files:
                    if re.match(r"^msgstore.*\.db\.crypt\d+$", f, re.I):
                        try:
                            mt = os.path.getmtime(os.path.join(root, f))
                        except OSError:
                            mt = 0
                        if mt > newest_mtime:
                            newest_mtime = mt
                            p = root
                            while p and p != cust_dir:
                                if "whatsapp_backup" in os.path.basename(p).lower() or "pasien_" in os.path.basename(p).lower():
                                    default_folder = p
                                    break
                                p = os.path.dirname(p)
                            if not default_folder:
                                default_folder = root

        entry_folder = ctk.CTkEntry(f_pick, placeholder_text="Pilih folder cadangan WhatsApp...")
        if default_folder:
            entry_folder.insert(0, default_folder)
        entry_folder.pack(side="left", fill="x", expand=True, padx=(0, 6))

        lbl_inspect = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=11), text_color="#A0A0B0", justify="left")

        def update_inspect(path):
            if not path or not os.path.exists(path):
                lbl_inspect.configure(text="❌ Folder tidak ditemukan.", text_color="#FF5252")
                return None
            rescue = self._get_data_rescue()
            insp = rescue.inspect_whatsapp_backup(path)
            if insp.get("valid"):
                media_info = f"{insp.get('media_count', 0)} file (~{insp.get('media_size_mb', 0)} MB)" if insp.get("has_media") else "Tidak ada"
                lbl_inspect.configure(
                    text=f"✅ Database Ditemukan: {insp.get('active_db')} ({insp.get('total_db_size_mb')} MB)\n"
                         f"   • Riwayat Harian: {insp.get('total_db_files_count')} file database\n"
                         f"   • Pengaturan Akun: {'Tersedia' if insp.get('has_backups') else 'Tidak ada'}\n"
                         f"   • Media Foto/Video: {media_info}",
                    text_color="#00FFAA"
                )
            else:
                lbl_inspect.configure(text=f"⚠️ {insp.get('error', 'Database tidak valid')}", text_color="#FFAA00")
            return insp

        def pick_folder():
            d = filedialog.askdirectory(initialdir=cust_dir if os.path.exists(cust_dir) else APP_DIR, title="Pilih Folder Cadangan WhatsApp")
            if d:
                entry_folder.delete(0, "end")
                entry_folder.insert(0, d)
                update_inspect(d)

        ctk.CTkButton(f_pick, text="📂 Cari Folder...", width=110, command=pick_folder).pack(side="left")

        lbl_inspect.pack(anchor="w", padx=10, pady=(0, 10))
        if default_folder:
            update_inspect(default_folder)

        # 2. Target App Type
        ctk.CTkLabel(scroll, text="📱 2. Aplikasi Target di HP Baru:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
        wa_type_var = ctk.StringVar(value="com.whatsapp")
        f_type = ctk.CTkFrame(scroll, fg_color="transparent")
        f_type.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkRadioButton(f_type, text="WhatsApp Biasa (com.whatsapp)", variable=wa_type_var, value="com.whatsapp").pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(f_type, text="WhatsApp Business (com.whatsapp.w4b)", variable=wa_type_var, value="com.whatsapp.w4b").pack(side="left")

        # 3. Restore Options
        ctk.CTkLabel(scroll, text="⚙️ 3. Opsi Pemulihan:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
        
        var_restore_media = ctk.BooleanVar(value=False)
        var_grant_perms = ctk.BooleanVar(value=True)

        cb_db = ctk.CTkCheckBox(scroll, text="Database Chat Utama & Riwayat (msgstore.db.crypt) [Wajib]", state="disabled")
        cb_db.select()
        cb_db.pack(anchor="w", padx=14, pady=3)

        cb_media = ctk.CTkCheckBox(scroll, text="Sertakan Media WhatsApp (Foto, Video, Voice Notes) jika ada di backup", variable=var_restore_media)
        cb_media.pack(anchor="w", padx=14, pady=3)

        cb_perm = ctk.CTkCheckBox(scroll, text="Auto-Grant Izin Penyimpanan via ADB (pm grant & appops) [Rekomendasi]", variable=var_grant_perms)
        cb_perm.pack(anchor="w", padx=14, pady=3)

        # 4. Technician SOP Box
        guide_box = ctk.CTkFrame(scroll, fg_color="#251F14", border_width=1, border_color="#FF9800", corner_radius=6)
        guide_box.pack(fill="x", padx=10, pady=(12, 10))

        ctk.CTkLabel(
            guide_box,
            text="💡 PANDUAN TEKNISI SEBELUM KLIK RESTORE:\n"
                 "1. Pastikan WhatsApp sudah diinstal di HP baru dari Play Store, TETAPI JANGAN DIBUKA DULU.\n"
                 "2. Jika sudah terlanjur dibuka: Buka Pengaturan HP > Aplikasi > WhatsApp > Hapus Data (Clear Data).\n"
                 "3. Klik tombol 'Mulai Restore Database' di bawah ini.\n"
                 "4. Setelah selesai, buka WhatsApp di HP baru -> Izinkan Akses File -> Masukkan Nomor HP & SMS OTP.\n"
                 "5. Layar 'Cadangan Ditemukan' akan OTOMATIS muncul -> Klik 'PULIHKAN'!",
            font=ctk.CTkFont(size=11),
            text_color="#FFD54F",
            justify="left"
        ).pack(padx=12, pady=10, anchor="w")

        # Bottom Action Bar
        bot_bar = ctk.CTkFrame(modal, fg_color="transparent")
        bot_bar.pack(fill="x", padx=20, pady=(0, 15))

        lbl_status = ctk.CTkLabel(bot_bar, text="", font=ctk.CTkFont(size=11, slant="italic"), text_color="#00FFAA")
        lbl_status.pack(anchor="w", pady=(0, 6))

        btn_run = ctk.CTkButton(
            bot_bar,
            text="🚀 Mulai Restore Database ke HP Target",
            fg_color="#00897B",
            hover_color="#00695C",
            height=36,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_run.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            bot_bar,
            text="Tutup",
            fg_color="#37474F",
            hover_color="#263238",
            height=36,
            command=modal.destroy
        ).pack(side="left")

        def start_restore():
            folder = entry_folder.get().strip()
            if not folder or not os.path.exists(folder):
                messagebox.showwarning("Pilih Folder", "Silakan pilih folder backup WhatsApp yang valid!", parent=modal)
                return

            if not self.current_device:
                messagebox.showwarning("HP Target", "HP target belum terdeteksi. Hubungkan HP baru via kabel USB dengan USB Debugging aktif!", parent=modal)
                return

            insp = update_inspect(folder)
            if not insp or not insp.get("valid"):
                messagebox.showerror("Database Tidak Valid", f"Folder tidak berisi database yang valid:\n{insp.get('error') if insp else ''}", parent=modal)
                return

            target_pkg = wa_type_var.get()
            want_media = var_restore_media.get()
            grant_p = var_grant_perms.get()

            btn_run.configure(state="disabled", text="⏳ Memulihkan Database...")
            lbl_status.configure(text="⏳ Mempersiapkan transfer database ke HP target...")

            def worker():
                rescue = self._get_data_rescue()
                def on_prog(msg):
                    self.after(0, lambda m=msg: lbl_status.configure(text=m))

                ok, report = rescue.restore_whatsapp(
                    backup_folder=folder,
                    target_package=target_pkg,
                    restore_media=want_media,
                    auto_grant_perms=grant_p,
                    on_progress=on_prog
                )

                def finish():
                    btn_run.configure(state="normal", text="🚀 Mulai Restore Database ke HP Target")
                    if ok:
                        lbl_status.configure(text="✅ Pemulihan database sukses!")
                        self.lbl_wa_status.configure(text="✅ Restore WhatsApp ke HP target sukses!")
                        messagebox.showinfo("Restore Selesai", report, parent=modal)
                    else:
                        lbl_status.configure(text="❌ Proses pemulihan terhenti.")
                        messagebox.showerror("Gagal Restore", report, parent=modal)

                self.after(0, finish)

            threading.Thread(target=worker, daemon=True).start()

        btn_run.configure(command=start_restore)

    def _start_full_data_rescue(self):
        if not self.current_device:
            messagebox.showwarning("Koneksi", "Sambungkan HP via USB terlebih dahulu!")
            return

        model = self.current_device.get("model", "Android")
        if not messagebox.askyesno(
            "1-Klik Full Rescue",
            f"Mulai penyelamatan data lengkap untuk {model}?\n\n"
            "Aplikasi akan otomatis:\n"
            "1. Mendeteksi & membuat laporan akun Gmail/vendor\n"
            "2. Mengekspor seluruh kontak telepon ke format .VCF\n"
            "3. Menyalin seluruh foto .jpg dari SEMUA folder ke subfolder terpisah (DCIM, WhatsApp, Pictures, dll)\n"
            "4. Menyalin folder Dokumen & Unduhan\n\n"
            "Semua data akan disimpan dalam satu folder pasien khusus."
        ):
            return

        self.btn_full_rescue.configure(state="disabled")

        def on_status_update(status_text):
            self.after(0, lambda: self.lbl_rescue_status.configure(text=status_text))

        def worker():
            rescue = self._get_data_rescue()
            ok, out_folder = rescue.full_data_rescue(device_model=model, on_status=on_status_update)
            def finish():
                self.btn_full_rescue.configure(state="normal")
                if ok:
                    self.lbl_rescue_status.configure(text=f"✅ Data lengkap tersimpan di: {os.path.basename(out_folder)}")
                    if messagebox.askyesno(
                        "Penyelamatan Sukses",
                        f"Penyelamatan data pasien selesai!\n\nFolder backup:\n{os.path.abspath(out_folder)}\n\nBuka folder sekarang?"
                    ):
                        try:
                            os.startfile(os.path.abspath(out_folder))
                        except Exception:
                            pass
                else:
                    self.lbl_rescue_status.configure(text="❌ Proses rescue terhenti.")
                    messagebox.showerror("Gagal", f"Gagal menjalankan rescue: {out_folder}")

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _backup_all_jpg_photos(self):
        rescue = self._get_data_rescue()
        if not rescue:
            messagebox.showwarning("Koneksi", "Sambungkan HP Android via kabel USB terlebih dahulu!")
            return

        self.btn_backup_jpg.configure(state="disabled", text="⏳ Memindai File .JPG...")
        self.lbl_jpg_status.configure(text="🔍 Memindai seluruh folder penyimpanan HP mencari file .jpg...")

        def worker():
            def on_prog(msg):
                self.after(0, lambda m=msg: self.lbl_jpg_status.configure(text=m))

            dest_dir = os.path.join(APP_DIR, "customer_backup", f"Semua_Foto_JPG_{int(time.time())}")
            ok, msg, count = rescue.backup_all_jpg(dest_folder=dest_dir, on_progress=on_prog)

            def done():
                self.btn_backup_jpg.configure(state="normal", text="📥 Backup Seluruh File .JPG Sekarang")
                if ok:
                    self.lbl_jpg_status.configure(text=f"✅ {count} file .jpg tersimpan rapi per subfolder!")
                    if messagebox.askyesno("Backup Selesai", f"{msg}\n\nBuka folder hasil backup sekarang?"):
                        try:
                            os.startfile(os.path.abspath(dest_dir))
                        except Exception:
                            pass
                else:
                    self.lbl_jpg_status.configure(text="❌ Gagal mem-backup file .jpg.")
                    messagebox.showerror("Gagal", msg)

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def _open_photo_folder(self):
        backup_dir = os.path.join(APP_DIR, "customer_backup")
        os.makedirs(backup_dir, exist_ok=True)
        try:
            os.startfile(os.path.abspath(backup_dir))
        except Exception as e:
            messagebox.showerror("Folder Error", f"Gagal membuka folder: {e}")

    def _open_backup_folder(self):
        backup_dir = os.path.join(APP_DIR, "customer_backup")
        os.makedirs(backup_dir, exist_ok=True)
        try:
            os.startfile(os.path.abspath(backup_dir))
        except Exception as e:
            messagebox.showerror("Folder Error", f"Gagal membuka folder: {e}")

    def _backup_customer_photos(self):
        self._backup_all_jpg_photos()

    def _generate_service_receipt(self):
        if not self.last_scan_data:
            if not messagebox.askyesno("Belum Scan", "Belum ada hasil scan. Tetap cetak nota kosong?"):
                return
            self.last_scan_data = {}

        html_file = ReceiptGenerator.generate_html_receipt(
            shop_name=self.entry_shop.get().strip(),
            shop_contact=self.entry_shop_contact.get().strip(),
            customer_name=self.entry_cust_name.get().strip(),
            customer_phone=self.entry_cust_phone.get().strip(),
            complaint=self.entry_complaint.get().strip(),
            estimate_price=self.entry_price.get().strip(),
            scan_data=self.last_scan_data
        )
        if html_file and os.path.exists(html_file):
            ReceiptGenerator.open_receipt(html_file)
        else:
            messagebox.showerror("Gagal", "Gagal membuat file nota servis!")

    def _show_usb_current_guide(self):
        modal = ctk.CTkToplevel(self)
        modal.title("📊 Kamus Diagnosa Arus USB (USB Charger Doctor)")
        modal.geometry("640x540")
        modal.minsize(580, 480)
        modal.grab_set()

        t_lbl = ctk.CTkLabel(
            modal,
            text="⚡ KAMUS ANALISA KONSUMSI ARUS USB CHARGER",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFAA00"
        )
        t_lbl.pack(padx=20, pady=(15, 4), anchor="w")

        sub_lbl = ctk.CTkLabel(
            modal,
            text="Panduan pembacaan amperemeter USB teknisi konter untuk mendeteksi letak kerusakan hardware:",
            font=ctk.CTkFont(size=11),
            text_color="#B0B0C0"
        )
        sub_lbl.pack(padx=20, pady=(0, 10), anchor="w")

        scroll = ctk.CTkScrollableFrame(modal, fg_color="#13131A", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        guides = [
            ("0.00 A (Nol Total)", "#FF5252", 
             "• Jalur VBUS 5V putus / Flexible sub-board cas robek / lepas soket.\n"
             "• Port konektor Type-C / Micro USB patah / kotor / longgar.\n"
             "• Dioda proteksi OVP (Over Voltage Protection) jebol / short."),
             
            ("0.01 - 0.08 A (Short Halus)", "#FFA726",
             "• Terjadi kebocoran arus halus di jalur sekunder VDD_MAIN / VBAT.\n"
             "• Kapasitor keramik di sekitar IC Power / IC Charger bocor.\n"
             "• Gejala: HP terasa hangat saat dicolok & baterai boros saat standby."),
             
            ("0.10 - 0.25 A Gantung (CPU Stalling)", "#FFD54F",
             "• HP mati suri / bootloop / CPU tidak merespon perintah boot.\n"
             "• Partisi Bootloader / eMMC korup atau IC RAM lepas kaki timah (kering).\n"
             "• Solusi: Coba masuk Fastboot / EDL 9008 atau flashing partisi ulang."),
             
            ("0.40 - 0.50 A (Mode USB Standar)", "#81C784",
             "• Arus pengisian normal dari port USB komputer / PC (Limit USB 2.0 = 500mA).\n"
             "• Jika dicolok ke kepala cas dinding tetap 0.45A: IC Charger tidak mendeteksi jalur data D+ / D- (Fast Charging gagal negosiasi)."),
             
            ("1.20 - 2.50 A (Fast Charging Normal)", "#4CAF50",
             "• Jalur pengisian sangat prima! IC Charger, kabel, dan baterai normal menyerap daya besar.\n"
             "• Protokol QC 3.0 / PD / VOOC / Dart bekerja normal."),
             
            ("Arus Bouncing (Naik-Turun Cepat)", "#BA68C8",
             "• Tegangan sel baterai drop total di bawah 2.8V (Baterai pingsan).\n"
             "• Jalur BSI (Battery Status Indicator) atau Pin B-Temp (Thermistor) kotor/putus.\n"
             "• IC Charging mencoba cas, gagal verifikasi termal, lalu memutus arus berulang-ulang.")
        ]

        for title, col, desc in guides:
            box = ctk.CTkFrame(scroll, fg_color="#1E1E28", corner_radius=6)
            box.pack(fill="x", pady=5, padx=4)
            h = ctk.CTkLabel(box, text=f"📌 {title}", font=ctk.CTkFont(size=12, weight="bold"), text_color=col)
            h.pack(anchor="w", padx=12, pady=(8, 2))
            d = ctk.CTkLabel(box, text=desc, font=ctk.CTkFont(family="Consolas", size=11), text_color="#E0E0E0", justify="left")
            d.pack(anchor="w", padx=12, pady=(0, 8))

    def _trigger_frp_browser(self, target="youtube"):
        dev = self.current_device
        serial = dev.get("serial") if dev else None
        tools = FrpAndLockTools(serial=serial)
        def worker():
            ok, msg = tools.launch_browser(target=target)
            self.after(0, lambda: self.lbl_frp_status.configure(text=f"🌐 {msg}"))
            self.after(6000, lambda: self.lbl_frp_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_bypass_wizard(self):
        dev = self.current_device
        serial = dev.get("serial") if dev else None
        tools = FrpAndLockTools(serial=serial)
        def worker():
            ok, msg = tools.bypass_setup_wizard()
            self.after(0, lambda: self.lbl_frp_status.configure(text=f"⚡ {msg}"))
            self.after(6000, lambda: self.lbl_frp_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_fastboot_frp(self):
        dev = self.current_device
        serial = dev.get("serial") if dev else None
        tools = FrpAndLockTools(serial=serial)
        def worker():
            ok, msg = tools.fastboot_erase_frp()
            self.after(0, lambda: self.lbl_frp_status.configure(text=f"{msg}"))
            self.after(8000, lambda: self.lbl_frp_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_reset_screen_lock(self):
        confirm = messagebox.askyesno(
            "Konfirmasi Reset Kunci Layar",
            "PERINGATAN TEKNISI:\n"
            "Fitur ini menghapus database kunci (pola/PIN/sandi) secara langsung.\n"
            "Hanya bisa bekerja jika HP berada di mode TWRP/Recovery atau memiliki akses ROOT.\n"
            "Semua data foto, chat WhatsApp, dan kontak TIDAK AKAN HILANG.\n\n"
            "Lanjutkan penghapusan kunci layar sekarang?"
        )
        if not confirm:
            return
        dev = self.current_device
        serial = dev.get("serial") if dev else None
        tools = FrpAndLockTools(serial=serial)
        def worker():
            ok, msg = tools.reset_screen_lock()
            self.after(0, lambda: self.lbl_frp_status.configure(text=f"🔓 {msg}"))
            self.after(8000, lambda: self.lbl_frp_status.configure(text=""))
        threading.Thread(target=worker, daemon=True).start()

    def _trigger_samsung_enable_adb(self):
        confirm = messagebox.askyesno(
            "1-Klik Aktifkan ADB Samsung",
            "FITUR KHUSUS SAMSUNG (MODEM AT-COMMAND EXPLOIT):\n\n"
            "• Cara Kerja: Mengirim paket perintah AT khusus ke driver 'SAMSUNG Mobile USB Modem' di Windows untuk memaksa daemon ADB aktif.\n"
            "• Kompatibel: Samsung One UI patch lama & menengah (Android 9 s/d 13).\n"
            "• Catatan: Jika layar masih bisa disentuh, buka menu Panggilan Darurat dan ketik *#0*# terlebih dahulu untuk hasil maksimal.\n\n"
            "Jalankan exploit aktivasi ADB sekarang?"
        )
        if not confirm:
            return

        self.btn_samsung_adb.configure(state="disabled", text="⏳ Mengirim Perintah AT...")
        self.lbl_frp_status.configure(text="🔍 Memindai port modem Samsung...")

        def worker():
            activator = SamsungAdbActivator()
            def on_prog(msg):
                self.after(0, lambda m=msg: self.lbl_frp_status.configure(text=m))

            ok, report = activator.activate_adb_modem(on_progress=on_prog)

            def finish():
                self.btn_samsung_adb.configure(state="normal", text="⚡ 1-Klik Aktifkan ADB Samsung (Modem AT MTP Port)")
                if ok:
                    self.lbl_frp_status.configure(text="✅ Proses aktivasi ADB selesai!")
                    messagebox.showinfo("Aktivasi ADB Samsung", report)
                else:
                    self.lbl_frp_status.configure(text="⚠️ Aktivasi ADB via modem belum berhasil.")
                    messagebox.showwarning("Aktivasi ADB Samsung", report)

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app = AndroidHardwareDoctorApp()
    app.mainloop()
