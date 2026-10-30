"""
Database & Panduan Lengkap Teknisi:
Menyalakan HP Android Mati Tanpa Tombol Power Agar Masuk ADB
(Force Power-On / Jumper PWR_KEY / Fastboot Boot / Charging Loop)
Untuk Semua Merk & Chipset Android.
"""

class PowerOnDatabase:
    GUIDES = [
        # 1. XIAOMI / REDMI / POCO
        {
            "brand": "Xiaomi / Redmi / POCO",
            "models_covered": "Redmi Series (Note 7-13, 9, 10, 12, A series), POCO (X3, F3, M3, C series), Mi Series",
            "chipset": "Qualcomm Snapdragon & MediaTek Helio/Dimensity",
            "pwr_voltage": "1.8V - 3.3V (Pull-Up PMIC)",
            "summary": "Jumper titik PWR_KEY ke kaleng Ground, atau masuk Fastboot via Vol Down lalu eksekusi Fastboot Reboot.",
            "method_jumper": (
                "1. Buka penutup belakang (backdoor) dan lepaskan penutup kaleng motherboard.\n"
                "2. Cari konektor soket fleksibel tombol samping (Power & Volume).\n"
                "3. Di dekat soket tersebut terdapat 2 atau 3 titik kuningan bulat kecil. Titik bertuliskan 'PWR', 'ON', atau pin paling atas adalah jalur PWR_KEY.\n"
                "4. Siapkan pinset logam runcing:\n"
                "   - Tempelkan satu ujung pinset ke titik PWR_KEY.\n"
                "   - Tempelkan ujung pinset lainnya ke Kaleng Pelindung IC (Ground / GND).\n"
                "5. Tahan hubungan pinset selama 2 - 3 detik sampai HP bergetar.\n"
                "6. Lepas pinset, HP akan langsung menyala normal masuk ke sistem Android (ADB otomatis aktif)."
            ),
            "method_fastboot": (
                "JIKA TOMBOL VOLUME BAWAH (-) MASIH BERFUNGSI:\n"
                "1. Tahan tombol Volume Bawah (-).\n"
                "2. Sambil ditahan, colok kabel USB yang terhubung ke PC.\n"
                "3. Layar HP akan menyala menampilkan logo FASTBOOT (Kelinci Mi / tulisan Fastboot).\n"
                "4. Di aplikasi ini, klik tombol '🚀 Eksekusi Fastboot Reboot'.\n"
                "5. HP akan otomatis restart langsung masuk ke menu Android tanpa perlu menekan tombol Power!"
            ),
            "method_autocharge": (
                "TRIK AKTIFKAN NYALA OTOMATIS SAAT CAS (PERMANEN):\n"
                "1. Saat HP dalam posisi Fastboot, jalankan perintah:\n"
                "   fastboot oem off-mode-charge 0\n"
                "2. Dengan setelan ini, jika HP mati dan dicolok kabel charger/USB, HP TIDAK AKAN menampilkan animasi baterai mengecas, melainkan LANGSUNG NYALA MASUK KE ANDROID OTOMATIS!"
            ),
            "method_battery_trick": (
                "TRIK SIKLUS SOKET BATERAI:\n"
                "1. Lepaskan soket baterai dari motherboard.\n"
                "2. Colok kabel USB ke PC (lampu LED notifikasi di atas layar akan berkedip).\n"
                "3. Tepat saat logo Mi muncul sekejap (jeda 1 detik), tancapkan kembali soket baterai.\n"
                "4. Pada Redmi 9/9A/Note 8 trik ini seringkali langsung memicu Auto-Boot."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │     MOTHERBOARD XIAOMI / REDMI / POCO    │\n"
                "  │                                          │\n"
                "  │  ┌────────────────────┐   [SOKET TOMBOL] │\n"
                "  │  │   KALENG CPU/IC    │   ┌────────────┐ │\n"
                "  │  │   (GROUND / GND)   │   │  (•) PWR   │ │\n"
                "  │  └────────┬───────────┘   │  (•) VOL-  │ │\n"
                "  │           ▲ [PINSET]      │  (•) VOL+  │ │\n"
                "  │           └───────────────┴──(•) GND   │ │\n"
                "  │                           └────────────┘ │\n"
                "  │  [ SOKET BATERAI ]                       │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Hubungkan titik (•) PWR ke Kaleng (GND) selama 2-3 detik"
            )
        },

        # 2. SAMSUNG GALAXY
        {
            "brand": "Samsung Galaxy",
            "models_covered": "Galaxy Seri A (A01-A54), Seri M (M10-M53), Seri S & Note, Seri J (J2-J7 Prime)",
            "chipset": "Exynos, Qualcomm Snapdragon, MediaTek",
            "pwr_voltage": "1.8V (Pull-Up PMIC S2MPU/Shannon)",
            "summary": "Jumper pin PWR_SW ke GND, atau masuk Download Mode (Vol Up+Down) lalu Cancel Reboot ke System.",
            "method_jumper": (
                "1. Buka penutup belakang dan frame bezel tengah.\n"
                "2. Di sisi kanan motherboard, perhatikan kontak pin tombol power (sering berupa 2 plat kuningan atau konektor FPC).\n"
                "3. Satu plat adalah Ground (GND), satu plat lagi adalah jalur PWR_KEY (tegangan 1.8V).\n"
                "4. Ambil pinset logam, satukan kedua plat kuningan tersebut (atau jumper jalur PWR ke kaleng IC).\n"
                "5. Tahan selama 3 detik sampai muncul getaran dan logo 'Samsung Galaxy'.\n"
                "6. Lepas pinset, HP langsung booting masuk ke One UI Android."
            ),
            "method_fastboot": (
                "TRIK DOWNLOAD MODE -> REBOOT SYSTEM (100% TANPA TOMBOL POWER):\n"
                "1. Pastikan HP mati total dan baterai terpasang.\n"
                "2. Tahan tombol Volume Atas (+) DAN Volume Bawah (-) bersamaan.\n"
                "3. Sambil kedua tombol volume ditahan, colok kabel USB yang terhubung ke PC.\n"
                "4. Layar HP akan menyala hijau tosca (Layar 'Warning / Download Mode').\n"
                "5. Perhatikan tulisan di layar: 'Volume Down: Cancel (restart phone)'.\n"
                "6. Tekan tombol Volume Bawah (-) SATU KALI:\n"
                "   -> HP akan langsung membatalkan Download Mode dan REBOOT NORMAL KE ANDROID!\n"
                "7. Tunggu HP masuk layar menu utama, kabel USB tetap tercolok, dan ADB langsung aktif!"
            ),
            "method_autocharge": (
                "TRIK AUTO-BOOT VIA BOOTING CHARGE RECOVERY:\n"
                "1. Saat HP mati, colok kabel USB ke charger.\n"
                "2. Begitu lingkaran baterai persentase muncul, tahan Volume Atas (+) untuk masuk Recovery Samsung.\n"
                "3. Di menu Recovery, pilih 'Reboot system now' menggunakan tombol volume (atau colok ke PC dan jalankan adb reboot)."
            ),
            "method_battery_trick": (
                "TRIK RESISTOR JIG 300K OHM (Untuk Port Micro-USB/Type-C Samsung):\n"
                "Teknisi konter sering menggunakan USB Jig (Resistor 300K Ohm antara Pin ID dan GND). Begitu ditancapkan ke port charger, HP Samsung yang mati langsung menyala otomatis tanpa menekan tombol apapun."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │       MOTHERBOARD SAMSUNG GALAXY         │\n"
                "  │                                          │\n"
                "  │  ┌────────────────────┐   PIN POWER:     │\n"
                "  │  │   KALENG SHANNON   │    [•] PWR (1.8V)│\n"
                "  │  │   (GROUND / GND)   │     │  ▲ [PINSET]│\n"
                "  │  └────────┬───────────┘     │  ▼         │\n"
                "  │           └─────────────────┴─[•] GND    │\n"
                "  │                                          │\n"
                "  │  [ SOKET FLEKSIBEL BATERAI ]             │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Hubungkan [•] PWR ke [•] GND selama 3 detik"
            )
        },

        # 3. OPPO / REALME
        {
            "brand": "Oppo / Realme",
            "models_covered": "Oppo Seri A (A3s, A5s, A15, A16, A53, A54), Reno Series, Realme C Series (C2-C55), Realme Number/Narzo Series",
            "chipset": "MediaTek Helio/Dimensity & Qualcomm Snapdragon",
            "pwr_voltage": "1.8V - 2.8V (Pull-Up PMIC MT63xx/PMxxx)",
            "summary": "Jumper titik kuningan KCOL0 / PWR ke kaleng GND, atau manfaatkan menu ColorOS Recovery Reboot.",
            "method_jumper": (
                "1. Buka casing dan bezel pengaman motherboard.\n"
                "2. Pada Oppo/Realme, tombol Power berada di sisi kanan, sedangkan tombol Volume di sisi kiri.\n"
                "3. Di dekat soket fleksibel power sisi kanan, cari titik kuningan berlabel 'PWR', 'KCOL0', atau titik emas paling dekat dengan soket tombol.\n"
                "4. Gunakan pinset, hubungkan titik kuningan tersebut ke Kaleng Pelindung (GND).\n"
                "5. Tahan 3 detik sampai terasa getar dan logo 'OPPO' / 'realme' muncul di layar.\n"
                "6. Lepaskan pinset, tunggu loading ColorOS / Realme UI selesai."
            ),
            "method_fastboot": (
                "TRIK MASUK RECOVERY -> REBOOT (TANPA TOMBOL POWER):\n"
                "1. Tahan tombol Volume Bawah (-).\n"
                "2. Colokkan kabel USB dari PC ke HP.\n"
                "3. HP akan menyala masuk ke menu 'ColorOS Recovery' (Pilihan Bahasa: English / Mandarin).\n"
                "4. Layar sentuh (touchscreen) di Recovery Oppo/Realme biasanya AKTIF:\n"
                "   - Sentuh bahasa 'English'.\n"
                "   - Sentuh menu 'Reboot' -> 'OK'.\n"
                "5. HP langsung restart normal masuk ke menu Android dan ADB langsung terdeteksi di PC!"
            ),
            "method_autocharge": (
                "TRIK FASTBOOT FORCED BOOT (Untuk Seri Qualcomm Oppo A3s, A53, Realme 5):\n"
                "Jika HP bisa masuk Fastboot via tombol Volume Bawah, klik tombol '🚀 Eksekusi Fastboot Reboot' di aplikasi ini untuk mem-bypass tombol power."
            ),
            "method_battery_trick": (
                "TRIK POWER RESET CHIPSET MEDIATEK (Oppo A5s/A15/A16, Realme C2/C11):\n"
                "1. Cabut soket baterai selama 5 detik.\n"
                "2. Hubungkan pinset pada pin PWR ke Ground.\n"
                "3. Sambil ditahan pinsetnya, pasang soket baterai, lalu colok kabel USB.\n"
                "4. Arus tegangan baterai seketika memaksa IC PMIC memicu boot sequence."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │       MOTHERBOARD OPPO / REALME          │\n"
                "  │                                          │\n"
                "  │  [KAMERA]        ┌──────────────────┐    │\n"
                "  │                  │    KALENG CPU    │    │\n"
                "  │                  │   (GROUND / GND) │    │\n"
                "  │                  └────────┬─────────┘    │\n"
                "  │                           ▲ [PINSET]     │\n"
                "  │  (•) PWR_KEY (KCOL0) ─────┘              │\n"
                "  │  [ SOKET POWER KANAN ]                   │\n"
                "  │                                          │\n"
                "  │  [ SOKET BATERAI ]                       │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Hubungkan titik PWR_KEY ke Kaleng GND selama 3 detik"
            )
        },

        # 4. VIVO / IQOO
        {
            "brand": "Vivo / iQOO",
            "models_covered": "Vivo Seri Y (Y12, Y15, Y20, Y91, Y93, Y35), Seri V (V15, V20, V27), iQOO Series",
            "chipset": "MediaTek MT67xx & Qualcomm Snapdragon",
            "pwr_voltage": "1.8V - 3.0V (Pull-Up PMIC)",
            "summary": "Jumper titik PWR di samping baterai ke kaleng, atau masuk Fastboot Vivo via Vol Up lalu pilih Reboot.",
            "method_jumper": (
                "1. Buka backdoor dan lepaskan baut penutup PCB bagian atas.\n"
                "2. Di motherboard Vivo, titik tombol power biasanya berupa 2 pin kontak kuningan sejajar atau titik test point bulat bertuliskan 'PWR' / 'POWER'.\n"
                "3. Hubungkan titik kuningan PWR dengan Kaleng IC menggunakan pinset logam.\n"
                "4. Tahan selama 3 detik hingga HP bergetar dan logo 'vivo' atau 'iQOO' menyala.\n"
                "5. Lepaskan pinset, biarkan sistem FuntouchOS / OriginOS memuat hingga menu utama."
            ),
            "method_fastboot": (
                "TRIK FASTBOOT REBOOT VIVO (TANPA TOMBOL POWER):\n"
                "1. Pastikan HP mati.\n"
                "2. Tahan tombol Volume Atas (+).\n"
                "3. Sambil ditahan, colok kabel USB yang terhubung ke PC.\n"
                "4. HP Vivo akan langsung masuk ke menu 'FASTBOOT' dengan logo Funtouch.\n"
                "5. Di layar Fastboot Vivo, opsi default adalah 'Reboot':\n"
                "   - Cukup klik tombol '🚀 Eksekusi Fastboot Reboot' di aplikasi ini, ATAU\n"
                "   - Tekan Volume Bawah (-) untuk memilih jika tombol volume masih ada.\n"
                "6. HP Vivo langsung menyala normal masuk ke sistem Android!"
            ),
            "method_autocharge": (
                "TRIK CHARGING AUTO-POWER ON:\n"
                "Pada beberapa seri Vivo Y91/Y93/Y12, saat baterai kosong total (0%), colok charger 15 menit. Begitu baterai mencapai 3%, sistem otomatis melakukan cold-start booting tanpa perlu menekan tombol power."
            ),
            "method_battery_trick": (
                "TRIK RESET DAYA VIVO:\n"
                "Lepas soket baterai 3 detik, pasang kembali. Hubungkan titik TP PWR ke Ground sambil menancapkan kabel USB."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │         MOTHERBOARD VIVO / IQOO          │\n"
                "  │                                          │\n"
                "  │  ┌────────────────────┐                  │\n"
                "  │  │     KALENG IC      │   [SOKET POWER]  │\n"
                "  │  │   (GROUND / GND)   │     (•) PWR_KEY  │\n"
                "  │  └────────┬───────────┘      │   ▲ [PINSET]│\n"
                "  │           └──────────────────┴───┘       │\n"
                "  │                                          │\n"
                "  │  [ SOKET LCD ]   [ SOKET BATERAI ]       │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Hubungkan titik (•) PWR_KEY ke Kaleng GND selama 3 detik"
            )
        },

        # 5. INFINIX / TECNO / ITEL (TRANSSION)
        {
            "brand": "Infinix / Tecno / Itel",
            "models_covered": "Infinix Hot Series (Hot 8-40), Smart Series, Note Series, Tecno Spark/Pova/Camon, Itel Vision/P series",
            "chipset": "MediaTek Helio (G25, G35, G85, G88, G99) & Unisoc Tiger (T606, T616)",
            "pwr_voltage": "1.8V - 3.4V (Pull-Up PMIC MT6357/Unisoc SC27xx)",
            "summary": "Trik cabut-pasang baterai saat colok USB (Auto-Boot MTK), atau jumper titik bulat PWR ke Ground.",
            "method_jumper": (
                "1. Buka penutup belakang dan frame pengaman mesin.\n"
                "2. Di motherboard Infinix/Tecno, titik tombol power sangat jelas: terdapat titik kuningan bertuliskan 'PWR', 'K0', atau 'VKEY' di dekat soket fleksibel samping.\n"
                "3. Ambil pinset, tempelkan satu kaki ke titik PWR dan satu kaki ke kaleng penutup CPU (GND).\n"
                "4. Tahan 2 - 3 detik sampai bergetar dan muncul logo 'Infinix' / 'TECNO'.\n"
                "5. Lepas pinset, sistem XOS / HiOS langsung berjalan normal ke menu."
            ),
            "method_fastboot": (
                "TRIK FASTBOOT VIA VOLUME BAWAH:\n"
                "1. Tahan tombol Volume Bawah (-).\n"
                "2. Colokkan kabel USB ke PC.\n"
                "3. Begitu muncul layar 'FASTBOOT mode...', klik tombol '🚀 Eksekusi Fastboot Reboot' di aplikasi ini.\n"
                "4. Mesin langsung meluncur ke Android normal tanpa butuh tombol power."
            ),
            "method_autocharge": (
                "TRIK HARD-RESET AUTO-BOOT TRANSSION (PALING AMPUH TANPA BONGKAR):\n"
                "1. Jika HP mati total, colokkan charger original 2A.\n"
                "2. Tahan tombol Volume Atas (+) & Bawah (-) bersamaan selama 15 detik saat charger tertancap.\n"
                "3. PMIC MediaTek akan mendeteksi hardware force reset dan langsung menyalakan HP otomatis ke sistem!"
            ),
            "method_battery_trick": (
                "TRIK CABUT SOKET BATERAI SAAT CAS:\n"
                "1. Lepaskan konektor baterai dari motherboard.\n"
                "2. Colokkan kabel USB ke charger/PC.\n"
                "3. Saat lampu LED senter/notifikasi berkedip atau layar menyala putih 1 detik, langsung tekan pasang soket baterai.\n"
                "4. HP Infinix/Tecno langsung melanjutkan proses booting ke menu utama."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │     MOTHERBOARD INFINIX / TECNO / ITEL   │\n"
                "  │                                          │\n"
                "  │  ┌────────────────────┐   TITIK TESTPOINT│\n"
                "  │  │    KALENG CPU      │     (•) PWR / K0 │\n"
                "  │  │   (GROUND / GND)   │      │   ▲ [PINSET]│\n"
                "  │  └────────┬───────────┘      │   ▼       │\n"
                "  │           └──────────────────┴──(•) GND  │\n"
                "  │                                          │\n"
                "  │  [ SOKET FLEKSIBEL BATERAI ]             │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Hubungkan titik PWR / K0 ke Kaleng GND selama 3 detik"
            )
        },

        # 6. UNIVERSAL ANDROID (SEMUA MERK LAIN / ASUS / MOTOROLA / HUAWEI)
        {
            "brand": "Universal Android (Semua Merk Lain)",
            "models_covered": "Asus Zenfone/ROG, Huawei/Honor, Motorola, Advan, Evercoss, Pixel, Sony Xperia, & Semua Smartphone Android",
            "chipset": "Qualcomm Snapdragon, MediaTek, Unisoc, Kirin, Intel",
            "pwr_voltage": "1.8V - 3.8V (Standar Standby PMIC)",
            "summary": "Prinsip dasar hardware: Jumper jalur Power Key (Pull-up) ke Ground (0V) memicu sinyal ON ke PMIC.",
            "method_jumper": (
                "PRINSIP KERJA TEKNIKAL SEMUA HP ANDROID:\n"
                "Semua smartphone Android di dunia bekerja dengan prinsip yang sama:\n"
                "Jalur tombol Power (PWR_KEY) selalu memiliki tegangan pull-up standby sebesar 1.8V s/d 3.8V yang disuplai oleh IC Power (PMIC).\n"
                "Saat tombol ditekan, jalur tersebut dihubungkan ke Ground (0V). Begitu PMIC mendeteksi tegangan drop ke 0V selama minimal 1.5 detik, PMIC akan menyalakan regulator LDO, mengaktifkan osilator kristal 19.2MHz/26MHz, dan memulai urutan booting (Power-On Sequence).\n\n"
                "CARA JUMPER MANUAL DI MEJA SERVIS:\n"
                "1. Buka casing dan temukan soket fleksibel tombol samping.\n"
                "2. Gunakan Voltmeter / Multimeter digital di skala DC 20V:\n"
                "   - Probe hitam ke kaleng Ground (GND).\n"
                "   - Probe merah sentuh satu per satu pin kuningan di dekat soket tombol.\n"
                "   - Pin yang menunjukkan tegangan antara 1.8V s/d 3.8V ADALAH JALUR TOMBOL POWER (PWR_KEY)!\n"
                "3. Ambil pinset logam, hubungkan pin bertegangan tersebut ke kaleng Ground selama 3 detik.\n"
                "4. Mesin HP dijamin 100% langsung bergetar dan menyala normal!"
            ),
            "method_fastboot": (
                "PERINTAH UNIVERSAL FASTBOOT REBOOT:\n"
                "Colok kabel USB sambil tahan Volume Bawah (-) atau Volume Atas (+).\n"
                "Begitu terdeteksi di Fastboot, kirim perintah:\n"
                "fastboot reboot\n"
                "HP langsung keluar dari fastboot dan booting ke Android."
            ),
            "method_autocharge": (
                "PERINTAH UNIVERSAL AUTO-POWER ON SAAT CAS:\n"
                "Untuk semua chipset Qualcomm & MediaTek modern, jalankan di Fastboot:\n"
                "fastboot oem off-mode-charge 0\n"
                "Perintah ini menonaktifkan mode animasi charging dan memaksa HP menyala normal saat mendeteksi daya kabel USB."
            ),
            "method_battery_trick": (
                "TRIK RESET SIKLUS TEGANGAN VBUS:\n"
                "Colokkan kabel USB ke charger dinding 5V. Sambil kabel tertancap, lepaskan soket baterai 3 detik lalu pasang kembali. Hard reset jalur VBUS/VBAT ini memaksa IC PMIC menghidupkan kembali CPU."
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │     SKEMATIK UNIVERSAL MOTHERBOARD       │\n"
                "  │                                          │\n"
                "  │  ┌────────────────────┐   PIN VOLTMETER: │\n"
                "  │  │     KALENG IC      │    [•] 1.8V-3.8V ◄─── (PWR_KEY!)\n"
                "  │  │   (GROUND / 0V)    │     │  ▲ [PINSET]│\n"
                "  │  └────────┬───────────┘     │  ▼         │\n"
                "  │           └─────────────────┴─[•] GND    │\n"
                "  │                                          │\n"
                "  │  [ SOKET BATERAI ]                       │\n"
                "  └──────────────────────────────────────────┘\n"
                "  *Cari pin bertegangan 1.8V-3.8V pakai multimeter, lalu jumper ke Kaleng!"
            )
        }
    ]

    @classmethod
    def get_all_brands(cls) -> list:
        return [guide["brand"] for guide in cls.GUIDES]

    @classmethod
    def get_guide(cls, brand_name: str) -> dict:
        for guide in cls.GUIDES:
            if guide["brand"].lower() == brand_name.lower():
                return guide
        return cls.GUIDES[0]
