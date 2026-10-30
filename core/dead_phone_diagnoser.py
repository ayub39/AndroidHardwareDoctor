class DeadPhoneDiagnoser:
    """
    Expert technician diagnostic engine for DEAD / MATOT phones.
    Analyzes USB handshake, current consumption (Ampere), and symptoms
    to pinpoint faulty ICs and components.
    """

    AMPERE_PROFILES = {
        "0.00A": {
            "title": "Arus 0.00 A (Nol Total / Tanpa Konsumsi Daya)",
            "primary_suspect": "Jalur VBUS 5V Putus / OVP IC / Port Cas Jebol",
            "explanation": "Listrik dari kabel USB sama sekali tidak masuk ke motherboard HP.",
            "probing_points": [
                "1. Ukur pin VBUS di fleksibel konektor cas (harus keluar 5.0V).",
                "2. Cek diode / resistor fuse pelindung (OVP) sebelum IC Cas.",
                "3. Cek apakah pin baterai / konektor baterai longgar atau patah."
            ],
            "severity": "CRITICAL_POWER_INPUT"
        },
        "0.01A-0.08A": {
            "title": "Arus 0.01 A - 0.08 A Diam (Arus Dingin)",
            "primary_suspect": "Osilator Kristal (19.2 / 38.4 MHz) atau IC Power (PMIC) Utama",
            "explanation": "IC Power menerima arus tetapi gagal memicu sinyal clock (detak jantung) ke CPU.",
            "probing_points": [
                "1. Cek tegangan tombol Power (PWR_KEY) harus ada 1.8V - 4.0V.",
                "2. Ukur osilator kristal (XTAL 19.2MHz / 38.4MHz) di samping PMIC.",
                "3. Ukur jalur tegangan dasar PMIC: VREG_LDO1, VREG_S1 (Buck Converter)."
            ],
            "severity": "CPU_CLOCK_DEAD"
        },
        "0.10A-0.28A": {
            "title": "Arus 0.10 A - 0.28 A Gantung (Arus Hangat / Stuck)",
            "primary_suspect": "Tegangan Sekunder (LDO) Drop / IC RAM / Jalur Bus I2C Konslet",
            "explanation": "CPU mulai bekerja tetapi mogok saat menginisiasi subsistem atau RAM.",
            "probing_points": [
                "1. Raba apakah ada IC yang hangat (terutama PMIC sekunder / Audio / Wi-Fi).",
                "2. Cek tegangan LDO 1.8V (VREG_L5) dan 1.2V (VREG_S4) di sekitar CPU.",
                "3. Periksa jalur data I2C_SDA dan I2C_SCL (jangan sampai short ke ground)."
            ],
            "severity": "SECONDARY_RAIL_FAULT"
        },
        "0.40A-0.90A": {
            "title": "Arus 0.40 A - 0.90 A Stuck (Arus eMMC / UFS Lepas)",
            "primary_suspect": "Chip Memori Internal (eMMC / UFS) Rusak, Kosong, atau Kaki Lepas",
            "explanation": "CPU dan sistem daya bekerja normal, tetapi sistem operasi tidak ditemukan di storage.",
            "probing_points": [
                "1. Cek apakah HP terdeteksi otomatis sebagai Qualcomm 9008 atau MTK Port di PC.",
                "2. Ukur tegangan VCC (3.0V) dan VCCQ (1.8V) untuk supply eMMC/UFS.",
                "3. Lakukan proses Reballing atau ganti IC eMMC/UFS."
            ],
            "severity": "STORAGE_CHIP_DEAD"
        },
        "PULSE_LOOP": {
            "title": "Arus Naik Turun Berulang (Denyut: 0.0A -> 0.3A -> 0.0A)",
            "primary_suspect": "Watchdog Timer Reset / Konslet Jalur Tegangan Sekunder",
            "explanation": "IC Power mencoba menghidupkan HP, mendeteksi konslet ringan, lalu mati untuk memproteksi diri.",
            "probing_points": [
                "1. Cek kapasitor di sekitar IC Wi-Fi, IC Lampu Layar, dan IC PA Sinyal.",
                "2. Ukur hambatan dalam baterai (baterai drop di bawah 3.0V).",
                "3. Lepas kamera depan & belakang untuk memastikan modul kamera tidak konslet."
            ],
            "severity": "PROTECTION_SHUTDOWN"
        },
        "SHORT_OVER_1A": {
            "title": "Arus > 1.0 A Langsung Saat Dicolok (KONSLET TOTAL / SHORT)",
            "primary_suspect": "Kapasitor / Dioda di Jalur Utama (VPH_PWR / VDD_MAIN) Jebol ke Ground",
            "explanation": "Ada komponen di jalur tegangan utama baterai yang terbakar dan menghubungkan kutub positif langsung ke ground.",
            "probing_points": [
                "1. JANGAN PAKSA COLOK USB TERUS-MENERUS (bisa merusak komponen lain!).",
                "2. Gunakan MBR (Short Killer) atau Rosin Smoke Method untuk melihat komponen mana yang berasap/meleleh.",
                "3. Komponen yang paling sering short: Kapasitor keramik di samping IC Power / IC Charger (SMB/PMI)."
            ],
            "severity": "DANGEROUS_SHORT_CIRCUIT"
        }
    }

    @classmethod
    def evaluate_battery_voltage(cls, volts: float) -> dict:
        """
        Evaluates battery voltage and gives clear actionable repair advice
        (Trickle charge vs Jump start/Suntik vs Normal).
        Handles reverse probe polarity gracefully.
        """
        is_reverse_polarity = False
        if volts < 0.0:
            is_reverse_polarity = True
            volts = abs(volts)

        rev_note = " [!] (PROBE MULTIMETER TERBALIK: Polaritas Jarum Merah & Hitam Tertukar!)" if is_reverse_polarity else ""

        if volts <= 0.05:
            return {
                "level": "ZERO_NO_VOLTAGE",
                "badge": f"0.00V (KOSONG TOTAL / SEKRING PUTUS){rev_note}",
                "color": "#C62828",
                "can_boot": False,
                "title": "Baterai Mati Total / Putus Jalur",
                "diagnosis": f"Tidak ada tegangan sama sekali yang keluar dari pin konektor baterai.{rev_note}",
                "solution": "1. Cek sekring/fuse 'PL' di PCB baterai (kemungkinan besar putus).\n2. Cek apakah ada jalur fleksibel baterai yang robek.\n3. Jika sekring utuh tapi tetap 0V, sel baterai sudah mati total dan wajib ganti baterai baru."
            }
        elif volts < 3.00:
            return {
                "level": "CRITICAL_DROP",
                "badge": f"{volts:.2f}V (DROP PARAH - WAJIB SUNTIK){rev_note}",
                "color": "#D32F2F",
                "can_boot": False,
                "title": "Baterai Drop Parah (IC Cas Memblokir Pengisian)",
                "diagnosis": f"Tegangan baterai di bawah 3.0V. IC Charger di HP otomatis memutus arus karena sistem menganggap sel baterai tidak aman untuk dicas biasa.{rev_note}",
                "solution": "1. WAJIB SUNTIK BATERAI menggunakan kabel charger 5V atau charger kodok selama 10-15 menit.\n2. Jangan cas lewat colokan HP biasa karena arus tidak akan masuk sebelum baterai terisi minimal 3.2V."
            }
        elif volts < 3.70:
            return {
                "level": "LOW_CUTOFF",
                "badge": f"{volts:.2f}V (TEGANGAN KRITIS - TIDAK KUAT BOOTING){rev_note}",
                "color": "#E65100",
                "can_boot": False,
                "title": "Tegangan Baterai Kritis / Lemah",
                "diagnosis": f"Tegangan ({volts:.2f}V) berada di bawah ambang batas booting OS. Saat HP dinyalakan atau dicolok ke PC, tarikan arus CPU membuat tegangan anjlok seketika (voltage sag) sehingga HP restart berulang / port USB putus-nyambung!{rev_note}",
                "solution": "1. OPSI CEPAT: Suntik baterai pakai kabel charger 5V / charger kodok selama 3-5 menit sampai naik ke > 3.85V.\n2. OPSI SANTAI: Pasang baterai ke HP, colok ke charger dinding (bukan USB PC), dan biarkan trickle charge selama 45 menit - 1 jam tanpa ditekan tombol Power."
            }
        elif volts <= 4.25:
            return {
                "level": "NORMAL_GOOD",
                "badge": f"{volts:.2f}V (NORMAL & SIAP BOOTING){rev_note}",
                "color": "#2E7D32",
                "can_boot": True,
                "title": "Baterai Sehat & Daya Mencukupi",
                "diagnosis": f"Tegangan baterai dalam kondisi sehat dan sangat cukup untuk menghidupkan mesin HP Android secara normal.{rev_note}",
                "solution": "Baterai aman. Jika HP tetap tidak mau nyala pada tegangan ini, periksa tombol Power, fleksibel LCD, atau jalur IC Power di motherboard."
            }
        else:
            return {
                "level": "FULL",
                "badge": f"{volts:.2f}V (BATERAI PENUH / FULL){rev_note}",
                "color": "#1B5E20",
                "can_boot": True,
                "title": "Baterai Terisi Penuh (100%)",
                "diagnosis": f"Baterai terisi penuh (kapasitas maksimum).{rev_note}",
                "solution": "Baterai sangat prima. Siap untuk proses flashing, pengujian beban, atau pemakaian normal."
            }

    @classmethod
    def diagnose_dead_phone(cls, ampere_key: str, usb_mode: str, extra_symptoms: list = None) -> dict:
        """
        Synthesizes Ampere profile + USB Mode into an actionable technician report.
        """
        extra_symptoms = extra_symptoms or []
        profile = cls.AMPERE_PROFILES.get(ampere_key, cls.AMPERE_PROFILES["0.00A"])
        
        chipset_diagnosis = ""
        if usb_mode == "EDL_QUALCOMM":
            chipset_diagnosis = "HP terdeteksi otomatis di Port 9008! Artinya CPU Snapdragon & PMIC 100% HIDUP. Masalah ada pada IC Storage (eMMC/UFS) yang tidak terbaca, partisi bootloader rusak, atau kaki timah eMMC retak."
        elif usb_mode == "MTK_BROM":
            chipset_diagnosis = "HP terdeteksi di Port MediaTek BROM / Preloader! Artinya CPU MediaTek & IC Power HIDUP. Tinggal dilakukan tes memori RAM atau flashing firmware resmi."
        elif usb_mode == "DISCONNECTED":
            chipset_diagnosis = "Tidak ada respon USB sama sekali di komputer. Cek jalur data D+/D- atau gunakan panduan analisis arus di bawah."

        return {
            "title": profile["title"],
            "primary_suspect": profile["primary_suspect"],
            "explanation": profile["explanation"],
            "chipset_diagnosis": chipset_diagnosis,
            "probing_points": profile["probing_points"],
            "severity": profile["severity"]
        }
