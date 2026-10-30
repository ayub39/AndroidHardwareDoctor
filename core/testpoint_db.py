class TestPointDatabase:
    """
    UnlockTool & Borneo Schematics-style Test Point (TP) Database for hardware unbricking.
    Provides pinout locations, connection steps, and visual ASCII diagrams
    for major brands: Xiaomi, Samsung, Oppo, Realme, Vivo, Infinix, Tecno, and Universal.
    """

    DATABASE = [
        # =========================================================
        # 1. XIAOMI / REDMI / POCO
        # =========================================================
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 8 (Ginkgo)",
            "chipset": "Qualcomm Snapdragon 665",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan bulat kecil di atas soket baterai, di samping konektor fingerprint.",
            "steps": "1. Cabut kabel USB dan lepas soket baterai.\n2. Hubungkan kedua titik kuningan (TP) pakai pinset logam runcing.\n3. Sambil pinset tetap menghubungkan kedua titik TP, colok kabel USB ke PC.\n4. Tunggu PC bunyi 'tut-tut' (muncul port Qualcomm 9008), lalu lepas pinset.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │      MOTHERBOARD        │\n"
                "  │  [KAMERA]               │\n"
                "  │                         │\n"
                "  │     (•) (•) ◄─── TEST POINT (Jumper 2 titik ini)\n"
                "  │                         │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 7 (Lavender)",
            "chipset": "Qualcomm Snapdragon 660",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di bawah soket baterai, tepat di atas kaleng pelindung IC.",
            "steps": "1. Lepas soket baterai.\n2. Satukan kedua titik kuningan dengan ujung pinset.\n3. Colokkan kabel USB ke PC.\n4. Lepas pinset begitu terdeteksi Qualcomm HS-USB QDLoader 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [ SOKET LCD ]          │\n"
                "  │                         │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  │     (•) (•) ◄─── TEST POINT\n"
                "  │  ┌───────────────────┐  │\n"
                "  │  │   KALENG CPU      │  │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 9 Pro / 9S (Curtana/Joyeuse)",
            "chipset": "Qualcomm Snapdragon 720G",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di samping kiri soket fleksibel penghubung board bawah (Sub-board).",
            "steps": "1. Lepas soket baterai.\n2. Short 2 titik TP pakai pinset logam runcing.\n3. Colok kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [MODUL 4 KAMERA]       │\n"
                "  │                         │\n"
                "  │  (•) (•) ◄─── TP 9008   │\n"
                "  │  [SOKET SUB-BOARD]      │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 10 (Sunny/Mojito)",
            "chipset": "Qualcomm Snapdragon 678",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di sebelah kiri fleksibel penghubung baterai, dekat modul kamera.",
            "steps": "1. Lepas baterai.\n2. Short 2 titik Test Point pakai pinset logam ke Ground (kaleng motherboard).\n3. Colokkan kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [MODUL 4 KAMERA]       │\n"
                "  │  (•) (•) ◄─── TEST POINT│\n"
                "  │                         │\n"
                "  │  [ SOKET FLEKSIBEL ]    │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 11 (Spes)",
            "chipset": "Qualcomm Snapdragon 680",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan kecil vertikal di bawah soket kamera utama.",
            "steps": "1. Lepas soket baterai.\n2. Satukan kedua titik kuningan dengan pinset runcing.\n3. Colokkan kabel USB ke PC sampai terdeteksi Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA 50MP]          │\n"
                "  │    (•)                  │\n"
                "  │    (•) ◄─── TP 9008     │\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │   KALENG CPU     │   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi Note 12 4G (Topaz)",
            "chipset": "Qualcomm Snapdragon 685",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan sejajar horizontal di atas soket fleksibel LCD.",
            "steps": "1. Cabut soket baterai.\n2. Satukan kedua titik kuningan TP menggunakan pinset.\n3. Colok kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA BELAKANG]      │\n"
                "  │  (•) (•) ◄─── TP 9008   │\n"
                "  │  [ SOKET LCD ]          │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "POCO X3 NFC / X3 Pro (Surya/Vayu)",
            "chipset": "Qualcomm Snapdragon 732G / 860",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan kecil vertikal di bawah soket fleksibel LCD.",
            "steps": "1. Lepas baterai.\n2. Satukan 2 titik TP menggunakan pinset.\n3. Colokkan kabel USB ke PC sampai PC mendeteksi Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET SUB-BOARD]      │\n"
                "  │     (•)                 │\n"
                "  │     (•) ◄─── TEST POINT │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "POCO M3 (Citrus)",
            "chipset": "Qualcomm Snapdragon 662",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di sudut kiri atas kaleng CPU (dekat soket kamera depan).",
            "steps": "1. Lepas soket baterai.\n2. Hubungkan 2 titik kuningan TP dengan pinset.\n3. Colok kabel USB ke PC sampai keluar port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  (•) (•) ◄─── TP 9008   │\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │   KALENG CPU     │   │\n"
                "  │  └──────────────────┘   │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi 8 / 8A (Olive/Olivelite)",
            "chipset": "Qualcomm Snapdragon 439",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di sebelah kanan soket baterai.",
            "steps": "1. Lepas baterai.\n2. Jumper 2 titik TP pakai pinset.\n3. Colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA]               │\n"
                "  │  [SOKET BAT]  (•) (•) ◄─┼── TP 9008\n"
                "  │  [SOKET LCD]            │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi 9 / 9A / 9C",
            "chipset": "MediaTek Helio G25 / G35 / G80",
            "mode": "MediaTek BROM",
            "location": "Metode Tombol Vol Atas+Bawah atau TP 1 titik ke Ground (kaleng).",
            "steps": "METODE 1 (Tanpa Bongkar):\n1. Matikan HP.\n2. Tahan tombol Volume Atas (+) & Volume Bawah (-).\n3. Colokkan kabel USB ke PC.\n\nMETODE 2 (Test Point jika bootloop parah):\n1. Buka casing, lepas baterai.\n2. Hubungkan 1 titik kuningan TP bertuliskan 'CLK' ke Ground (kaleng mesin).\n3. Colokkan kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KALENG MESIN / GND]   │\n"
                "  │     ■═══[PINSET]═══■    │\n"
                "  │    (GND)          (•)TP │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Xiaomi",
            "model": "Redmi 6 / 6A (Cactus/Cereus)",
            "chipset": "MediaTek Helio A22 / P22",
            "mode": "MediaTek BROM",
            "location": "Satu titik kuningan bulat kecil di bawah soket LCD dihubungkan ke Kaleng (Ground).",
            "steps": "1. Lepas soket baterai.\n2. Tempelkan satu kaki pinset ke titik TP dan satu kaki ke kaleng Ground.\n3. Colokkan kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD]            │\n"
                "  │    (•) TP ──[PINSET]──┐ │\n"
                "  │  [KALENG GND ═════════▼]│\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 2. VIVO / IQOO
        # =========================================================
        {
            "brand": "Vivo",
            "model": "Vivo Y12 / Y15 / Y17 (B-G7)",
            "chipset": "MediaTek MT6765 (Helio P35)",
            "mode": "MediaTek BROM",
            "location": "Metode Kombinasi Tombol atau Titik TP di samping soket LCD.",
            "steps": "METODE TOMBOL (Paling Mudah):\n1. Lepas soket baterai 3 detik, pasang kembali.\n2. Tahan tombol Volume Atas (+) dan Volume Bawah (-) bersamaan.\n3. Sambil ditahan, colok kabel USB ke PC.\n\nMETODE TEST POINT (Jika tombol rusak):\n1. Lepas baterai.\n2. Hubungkan titik kuningan TP di samping soket LCD ke kaleng Ground menggunakan pinset.\n3. Colokkan kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [3 KAMERA BELAKANG]    │\n"
                "  │                         │\n"
                "  │  [SOKET LCD] (•) ◄── TP │\n"
                "  │  [SOKET BATERAI B-G7]   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y15s / Y16 (V2134/V2204)",
            "chipset": "MediaTek Helio P35",
            "mode": "MediaTek BROM",
            "location": "Satu titik kuningan TP di sebelah kiri konektor baterai dihubungkan ke kaleng Ground.",
            "steps": "1. Lepas konektor baterai.\n2. Jumper titik kuningan TP ke kaleng pelindung IC terdekat.\n3. Colok kabel USB ke PC sampai terdeteksi MediaTek USB Port.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [MODUL KAMERA GANDA]   │\n"
                "  │                         │\n"
                "  │  (•) TP ──┐             │\n"
                "  │           ▼ [PINSET]    │\n"
                "  │  [KALENG GROUND SENG]   │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y20 / Y20s (V2029)",
            "chipset": "Qualcomm Snapdragon 460",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di bawah kaleng CPU dekat konektor LCD.",
            "steps": "1. Lepas soket baterai.\n2. Satukan kedua titik kuningan TP dengan pinset logam.\n3. Colokkan kabel USB ke PC.\n4. Lepas pinset setelah terdeteksi Qualcomm HS-USB QDLoader 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │    KALENG CPU    │   │\n"
                "  │  └──────────────────┘   │\n"
                "  │    (•) (•) ◄─── TP 9008 │\n"
                "  │  [ SOKET BATERAI ]      │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y21 / Y21s / Y22 (V2111/V2207)",
            "chipset": "MediaTek Helio P35 / Helio G80 / Helio G85",
            "mode": "MediaTek BROM",
            "location": "Tahan Vol Atas+Bawah atau titik TP kuningan bulat di atas soket LCD ke Ground.",
            "steps": "1. Buka penutup mesin, lepas baterai 5 detik lalu pasang lagi.\n2. Tahan tombol Volume Atas (+) & Bawah (-).\n3. Colok kabel USB ke PC.\n(Jika tombol rusak: hubungkan titik TP kuningan di atas soket LCD ke kaleng Ground dengan pinset).",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA 50MP]          │\n"
                "  │  (•) TP ◄── Jumper GND  │\n"
                "  │  [SOKET LCD]            │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y91 / Y93 / Y95",
            "chipset": "Qualcomm Snapdragon 439",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan sejajar horizontal di sebelah kanan soket baterai.",
            "steps": "1. Lepas konektor baterai.\n2. Hubungkan 2 titik kuningan TP menggunakan pinset.\n3. Colok kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD]            │\n"
                "  │                         │\n"
                "  │  [SOKET BAT]  (•) (•) ◄─┼── TP 9008\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y51 / Y51A (2020)",
            "chipset": "Qualcomm Snapdragon 662",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di bawah modul kamera utama.",
            "steps": "1. Lepas baterai.\n2. Jumper 2 titik TP menggunakan pinset runcing.\n3. Colokkan kabel data USB ke komputer.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [3 KAMERA BELAKANG]    │\n"
                "  │  (•) (•) ◄─── TP 9008   │\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │   KALENG CPU     │   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Vivo",
            "model": "Vivo Y53 / Y65 / Y71",
            "chipset": "Qualcomm Snapdragon 425 / 430 / 450",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di samping soket LCD atau di atas konektor baterai.",
            "steps": "1. Lepaskan soket baterai.\n2. Satukan kedua titik kuningan TP dengan pinset.\n3. Colok kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD]            │\n"
                "  │     (•) (•) ◄─── TP     │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 3. OPPO
        # =========================================================
        {
            "brand": "Oppo",
            "model": "Oppo A3s (CPH1803/CPH1853)",
            "chipset": "Qualcomm Snapdragon 450",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di samping kanan soket baterai.",
            "steps": "1. Buka penutup mesin, lepas soket baterai.\n2. Jumper / short kedua titik TP menggunakan pinset runcing.\n3. Sambil ditahan, colok kabel USB ke PC sampai keluar port Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA BELAKANG]      │\n"
                "  │                         │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  │       (•) (•) ◄─── TP   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Oppo",
            "model": "Oppo A5s / A15 / A16",
            "chipset": "MediaTek Helio P35 / G35",
            "mode": "MediaTek BROM",
            "location": "Metode Tombol Vol Atas+Bawah atau Test Point 1 titik ke Ground.",
            "steps": "1. Lepas baterai 3 detik, lalu pasang kembali.\n2. Tahan tombol Volume (+) dan Volume (-).\n3. Colokkan kabel USB ke PC sampai terdeteksi MediaTek USB Port.\n(Jika tombol rusak, gunakan 1 titik TP di bawah soket LCD lalu hubungkan ke kaleng Ground).",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET FLEKSIBEL LCD]  │\n"
                "  │    (•) ◄── TP (ke GND)  │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Oppo",
            "model": "Oppo A5 2020 / A9 2020 (CPH1931/CPH1937)",
            "chipset": "Qualcomm Snapdragon 665",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di atas soket baterai, di bawah kaleng IC Power.",
            "steps": "1. Buka casing, lepas baterai.\n2. Satukan kedua titik kuningan dengan pinset logam.\n3. Colok kabel USB ke PC sampai terdeteksi Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [4 KAMERA BELAKANG]    │\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │  KALENG IC POWER │   │\n"
                "  │  └──────────────────┘   │\n"
                "  │    (•) (•) ◄─── TP 9008 │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Oppo",
            "model": "Oppo A53 (2020 / CPH2127)",
            "chipset": "Qualcomm Snapdragon 460",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di bawah soket kamera depan.",
            "steps": "1. Lepas baterai.\n2. Hubungkan kedua titik kuningan dengan pinset.\n3. Colokkan kabel USB ke PC sampai terdeteksi port 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA DEPAN]         │\n"
                "  │    (•) (•) ◄─── TP 9008 │\n"
                "  │  ┌──────────────────┐   │\n"
                "  │  │    KALENG CPU    │   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Oppo",
            "model": "Oppo A54 / A57 2022 (CPH2239/CPH2387)",
            "chipset": "MediaTek Helio P35 / Helio G35",
            "mode": "MediaTek BROM",
            "location": "Kombinasi tombol Volume Atas & Bawah atau TP titik CLK ke Ground.",
            "steps": "1. Lepaskan soket baterai selama 5 detik, lalu pasang kembali.\n2. Tahan tombol Volume Atas (+) & Volume Bawah (-) bersamaan.\n3. Colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [TOMBOL VOL + & VOL -] │\n"
                "  │  TAHAN BERSAMAAN        │\n"
                "  │  LALU COLOK USB KE PC   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Oppo",
            "model": "Oppo A71 / A83 (Jadul)",
            "chipset": "MediaTek MT6763 / Qualcomm SD450",
            "mode": "MediaTek BROM / EDL 9008",
            "location": "Titik kuningan bulat di samping soket LCD.",
            "steps": "1. Lepas baterai.\n2. Jumper titik kuningan ke kaleng Ground.\n3. Colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD]            │\n"
                "  │    (•) ◄── Jumper GND   │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 4. REALME
        # =========================================================
        {
            "brand": "Realme",
            "model": "Realme C2 / C11 / C12 / C15",
            "chipset": "MediaTek Helio P22 / G35",
            "mode": "MediaTek BROM",
            "location": "Kombinasi tombol Volume (+) & (-) atau TP 1 titik ke Ground.",
            "steps": "1. Pastikan HP mati.\n2. Tahan Volume Atas (+) & Volume Bawah (-).\n3. Colok kabel USB ke PC sampai terdeteksi MediaTek USB Port.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [TOMBOL VOL + & VOL -] │\n"
                "  │  TAHAN BERSAMAAN        │\n"
                "  │  LALU COLOK USB KE PC   │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Realme",
            "model": "Realme C21 / C25 / C25s",
            "chipset": "MediaTek Helio G35 / G70 / G85",
            "mode": "MediaTek BROM",
            "location": "Tahan tombol Volume Atas & Bawah, atau 1 titik TP di bawah kamera ke Ground.",
            "steps": "1. Cabut soket baterai 3 detik, pasang lagi.\n2. Tahan Vol Up + Vol Down, colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA BELAKANG]      │\n"
                "  │    (•) TP ke GND        │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Realme",
            "model": "Realme C30 / C33 / C35 / C53",
            "chipset": "Unisoc Tiger T612 / T616",
            "mode": "Unisoc SPD Diag / Flash",
            "location": "Tahan Volume Bawah (-) lalu colok USB (Tanpa Bongkar).",
            "steps": "1. Matikan HP.\n2. Tahan tombol Volume Bawah (-).\n3. Colokkan kabel USB ke PC sampai terdeteksi port SPRD U2S Diag / Unisoc Port.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  CHIPSET UNISOC TIGER   │\n"
                "  │  TAHAN TOMBOL VOL (-)   │\n"
                "  │  COLOK KABEL USB KE PC  │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Realme",
            "model": "Realme 5 / 5i / 5 Pro",
            "chipset": "Qualcomm Snapdragon 665 / 712",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan bulat di atas soket baterai.",
            "steps": "1. Lepas soket baterai.\n2. Satukan kedua titik kuningan dengan pinset.\n3. Colok kabel USB ke PC sampai terdeteksi Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KALENG IC POWER]      │\n"
                "  │    (•) (•) ◄─── TP 9008 │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 5. SAMSUNG GALAXY
        # =========================================================
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A01 / A11 (SM-A015F/SM-A115F)",
            "chipset": "Qualcomm Snapdragon 439 / 450",
            "mode": "EDL 9008",
            "location": "Dua titik kuningan di samping konektor baterai.",
            "steps": "1. Lepas baterai.\n2. Satukan 2 titik kuningan TP dengan pinset logam.\n3. Colokkan kabel USB ke PC sampai terdeteksi Qualcomm 9008.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD]            │\n"
                "  │                         │\n"
                "  │  [SOKET BAT] (•) (•) ◄──┼── TP 9008\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A02s / A03s (SM-A025F/SM-A037F)",
            "chipset": "Qualcomm Snapdragon 450 / MediaTek Helio P35",
            "mode": "EDL 9008 / MTK BROM",
            "location": "Dua titik kuningan di samping soket baterai (Qualcomm) atau 1 titik ke Ground (MTK).",
            "steps": "1. Buka penutup mesin, lepas baterai.\n2. Jumper titik kuningan dengan pinset.\n3. Colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET KAMERA]         │\n"
                "  │  [SOKET BAT] (•) (•) ◄──┼── TEST POINT\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A03 Core (SM-A032F)",
            "chipset": "Unisoc SC9863A",
            "mode": "Unisoc SPD Flash",
            "location": "Tahan tombol Volume Bawah (-) lalu colok USB.",
            "steps": "1. Pastikan HP mati.\n2. Tahan tombol Volume Bawah (-).\n3. Colok kabel USB ke PC sampai terdeteksi port Unisoc / SPD.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [CHIPSET UNISOC SPD]   │\n"
                "  │  TAHAN VOL BAWAH (-)    │\n"
                "  │  COLOK KABEL USB KE PC  │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A04 / A04s / A05 / A05s",
            "chipset": "MediaTek Helio P35 / Exynos 850 / Snapdragon 680",
            "mode": "BROM / Odin Download Mode / EDL 9008",
            "location": "Titik kuningan dekat soket LCD atau kombinasi Vol Atas+Bawah.",
            "steps": "1. Tahan tombol Volume Atas (+) & Volume Bawah (-).\n2. Colok kabel USB ke PC untuk masuk mode Download / Odin.\n3. Jika butuh EDL/BROM: buka casing dan jumper titik kuningan di samping soket baterai ke kaleng Ground.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET FLEKSIBEL LCD]  │\n"
                "  │  (•) (•) ◄─── TEST POINT│\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A10s (SM-A107F)",
            "chipset": "MediaTek MT6762 (Helio P22)",
            "mode": "MediaTek BROM",
            "location": "Satu titik kuningan bulat di samping soket LCD dihubungkan ke Kaleng (Ground).",
            "steps": "1. Lepas baterai.\n2. Hubungkan 1 titik kuningan TP menggunakan pinset ke kaleng Ground terdekat.\n3. Sambil ditahan, colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  ┌──────────────┐       │\n"
                "  │  │ KALENG (GND) │       │\n"
                "  │  └──────┬───────┘       │\n"
                "  │         ▲ [PINSET]      │\n"
                "  │         ▼               │\n"
                "  │        (•) ◄── TEST POINT\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A12 (SM-A125F)",
            "chipset": "MediaTek MT6765 (Helio P35)",
            "mode": "MediaTek BROM",
            "location": "Satu titik kuningan di bawah soket kamera belakang ke Ground.",
            "steps": "1. Buka penutup mesin, lepas baterai.\n2. Tempelkan satu ujung pinset ke titik TP dan satu ujung ke kaleng seng (GND).\n3. Colokkan kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA BELAKANG]      │\n"
                "  │    (•) TP ──[PINSET]──┐ │\n"
                "  │                       ▼ │\n"
                "  │  [KALENG GROUND SENG ═══]│\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Samsung",
            "model": "Samsung Galaxy A21s / A51 / A50 (Exynos)",
            "chipset": "Samsung Exynos 850 / 9611",
            "mode": "Odin Download Mode / EUB Mode",
            "location": "Kombinasi tombol Volume Atas & Bawah atau titik TP UART di samping soket LCD.",
            "steps": "1. Matikan HP.\n2. Tahan tombol Volume Atas (+) & Bawah (-) bersamaan.\n3. Colok kabel USB ke PC sampai layar hijau tosca Download Mode muncul.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SAMSUNG EXYNOS MODE]  │\n"
                "  │  TAHAN VOL (+) & (-)    │\n"
                "  │  LALU COLOK USB KE PC   │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 6. INFINIX
        # =========================================================
        {
            "brand": "Infinix",
            "model": "Infinix Hot 9 / 10 / 10 Play (X680/X682)",
            "chipset": "MediaTek Helio A25 / G25 / G70",
            "mode": "MediaTek BROM",
            "location": "Tahan tombol Volume (+) & (-) atau jumper titik kuningan CLK ke kaleng Ground.",
            "steps": "1. Lepas soket baterai 3 detik, pasang kembali.\n2. Tahan tombol Volume Atas (+) & Bawah (-) bersamaan.\n3. Colok kabel USB ke PC sampai terdeteksi MediaTek USB Port.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [KAMERA BELAKANG]      │\n"
                "  │  (•) CLK ──[PINSET]──┐  │\n"
                "  │  [KALENG GND ════════▼] │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Infinix",
            "model": "Infinix Hot 11 / 11 Play / 12 Play",
            "chipset": "MediaTek Helio G35 / G37 / G88",
            "mode": "MediaTek BROM",
            "location": "Satu titik kuningan bulat di atas soket LCD ke kaleng Ground.",
            "steps": "1. Lepas soket baterai.\n2. Tempelkan pinset antara titik kuningan TP ke kaleng Ground.\n3. Colok kabel data USB ke komputer.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SOKET LCD] (•) ◄── TP │\n"
                "  │  [KALENG CPU / GND]     │\n"
                "  │  [SOKET BATERAI]        │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Infinix",
            "model": "Infinix Smart 5 / 6 / 7 / 8",
            "chipset": "MediaTek Helio A20 / Unisoc SC9863A / Unisoc T606",
            "mode": "MediaTek BROM / Unisoc SPD",
            "location": "Tahan Volume Bawah (-) atau Volume Atas+Bawah lalu colok USB.",
            "steps": "1. Pastikan HP mati.\n2. Tahan tombol Volume Bawah (-).\n3. Colok kabel USB ke PC sampai terdeteksi port flashing.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [SERI INFINIX SMART]   │\n"
                "  │  TAHAN VOL BAWAH (-)    │\n"
                "  │  COLOK KABEL USB KE PC  │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 7. TECNO
        # =========================================================
        {
            "brand": "Tecno",
            "model": "Tecno Spark 6 Go / 7 / 8 / 8C",
            "chipset": "MediaTek Helio A20 / A25 / Unisoc T606",
            "mode": "MediaTek BROM / Unisoc SPD",
            "location": "Kombinasi tombol Volume (+) & (-) atau jumper titik kuningan dekat soket tombol.",
            "steps": "1. Lepas soket baterai 3 detik, pasang lagi.\n2. Tahan tombol Volume (+) & (-) bersamaan.\n3. Colok kabel USB ke PC.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [TECNO SPARK SERIES]   │\n"
                "  │  TAHAN VOL (+) & (-)    │\n"
                "  │  COLOK KABEL USB KE PC  │\n"
                "  └─────────────────────────┘"
            )
        },
        {
            "brand": "Tecno",
            "model": "Tecno Pova 2 / Pova 3 / Pova 4 / Pova 5",
            "chipset": "MediaTek Helio G85 / G88 / G99",
            "mode": "MediaTek BROM",
            "location": "Tahan tombol Volume Atas & Bawah, atau 1 titik TP kuningan di samping soket LCD ke Ground.",
            "steps": "1. Pastikan HP mati.\n2. Tahan Volume Atas (+) & Bawah (-).\n3. Colok kabel USB ke PC sampai terdeteksi port MediaTek.",
            "ascii_diagram": (
                "  ┌─────────────────────────┐\n"
                "  │  [TECNO POVA SERIES]    │\n"
                "  │  (•) TP ──[PINSET]──┐   │\n"
                "  │  [KALENG GND ═══════▼]  │\n"
                "  │  [SOKET BATERAI JUMBO]  │\n"
                "  └─────────────────────────┘"
            )
        },

        # =========================================================
        # 8. UNIVERSAL / TRIK DETEKSI MANUAL MEJA SERVIS
        # =========================================================
        {
            "brand": "Universal",
            "model": "Trik Menemukan Titik Test Point Sendiri (Semua HP Baru / Tipe Langka)",
            "chipset": "Semua Chipset (Qualcomm, MTK, Unisoc, Exynos)",
            "mode": "EDL 9008 / BROM / SPD Flash",
            "location": "Metode pencarian fisik titik resistor pull-up 1.8V di dekat kaleng CPU / eMMC menggunakan Multimeter.",
            "steps": (
                "PANDUAN TEKNISI MENEMUKAN TITIK TEST POINT SENDIRI (JIKA HP BELUM ADA DI FOTO GOOGLE):\n\n"
                "1. CARA CEK METODE TOMBOL DULU (90% BERHASIL TANPA BONGKAR):\n"
                "   - HP MediaTek / Unisoc: Coba tahan Volume (+) & (-) atau Volume (-) saja, lalu colok kabel USB ke PC. Cek Device Manager apakah muncul port MTK atau SPD.\n"
                "   - HP Samsung: Coba tahan Volume (+) & (-) lalu colok USB ke PC untuk masuk Download Mode.\n\n"
                "2. CARA CARI TITIK TEST POINT EDL 9008 PADA HP QUALCOMM:\n"
                "   - Buka penutup kaleng motherboard.\n"
                "   - Cari 2 titik kuningan bulat kecil yang posisinya sangat berdekatan (jarak ~1-2 mm).\n"
                "   - Ciri khas titik TP 9008: Satu titik memiliki hambatan pull-up 1.8V ke IC Power, dan titik pasangannya adalah Ground (GND) atau jalur data.\n"
                "   - Ambil multimeter di mode Buzzer / Continuity:\n"
                "     * Probe hitam ke kaleng Ground.\n"
                "     * Sentuh kedua titik: satu titik harus berbunyi 'bip' (GND) dan satu lagi tidak berbunyi (Jalur Data).\n"
                "   - Hubungkan kedua titik tersebut pakai pinset, lalu colok kabel USB ke PC!\n\n"
                "3. CARA CARI TITIK CLK/DAT0 TEST POINT PADA HP MEDIATEK (MTK):\n"
                "   - Pada board MTK, titik TP biasanya hanya 1 titik bulat bertuliskan 'CLK', 'CMD', atau 'DAT0' di dekat chip eMMC/UFS.\n"
                "   - Cukup tempelkan satu ujung pinset ke titik tersebut, dan ujung pinset lainnya ke kaleng Ground seng.\n"
                "   - Colokkan kabel USB ke PC!"
            ),
            "ascii_diagram": (
                "  ┌──────────────────────────────────────────┐\n"
                "  │     CARA CARI TEST POINT DENGAN PINSET   │\n"
                "  │                                          │\n"
                "  │  Ciri-ciri fisik di Motherboard:         │\n"
                "  │  1. Ada 2 titik bulat emas kecil (•)(•)  │\n"
                "  │  2. Berjarak 1-2 mm dekat kaleng CPU     │\n"
                "  │  3. Satukan 2 titik ini pakai pinset:    │\n"
                "  │                                          │\n"
                "  │      (•)═══[PINSET LOGAM]═══(•)          │\n"
                "  │       ▲                      ▲           │\n"
                "  │     PIN 1                  PIN 2         │\n"
                "  │                                          │\n"
                "  │  4. Sambil ditahan pinset, colokkan USB! │\n"
                "  └──────────────────────────────────────────┘"
            )
        }
    ]

    @classmethod
    def get_all_brands(cls) -> list:
        brands = sorted(list(set(item["brand"] for item in cls.DATABASE)))
        return ["SEMUA MERK"] + brands

    @classmethod
    def search(cls, brand_filter: str = "SEMUA MERK", query: str = "") -> list:
        results = []
        q = query.lower().strip()
        for item in cls.DATABASE:
            if brand_filter != "SEMUA MERK" and item["brand"].lower() != brand_filter.lower():
                continue
            if q:
                match = (
                    q in item["model"].lower() or
                    q in item["brand"].lower() or
                    q in item["chipset"].lower() or
                    q in item["mode"].lower()
                )
                if not match:
                    continue
            results.append(item)
        return results
