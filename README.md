# ⚡ Android Hardware Doctor Pro v2.5 (All-in-One Stasiun Servis HP)

Aplikasi diagnosa hardware, panduan penanganan HP mati total, flashing firmware, alat uji fisik, dan sistem kasir/database servis HP Android.

---

### 🌟 Fitur & Tab Lengkap

#### 1. 🔍 Tab Diagnosa HP Hidup / Normal
* **Pengecekan Komponen:** Baterai, keausan memori internal eMMC/UFS (0% - 100%), modul kamera, driver IC touchscreen, sensor fisik, dan MAC Wi-Fi.
* **🔋 Evaluasi Mendalam Baterai & Siklus Cas:**
  * **Kesehatan (SoH - State of Health):** Persentase kesehatan riil baterai.
  * **Siklus Cas (Cycle Count):** Berapa kali baterai sudah mengalami siklus cas penuh dari awal pemakaian.
  * **Kapasitas Nyata vs Pabrik:** Menghitung kapasitas riil saat ini (mAh) terhadap kapasitas asli desain pabrikan.
  * **Penurunan Daya (Capacity Loss):** Menghitung selisih mAh dan persentase daya yang hilang akibat usia pakai.
  * **Vonis Otomatis:** Deteksi baterai masih prima, pemakaian wajar, atau sudah DROP dan wajib diganti.
* **📶 Deteksi No. IMEI & Status Sinyal / Baseband:**
  * Ekstraksi otomatis IMEI 1 dan IMEI 2 fisik via multi-jalur.
  * Diagnosa otomatis apakah hardware baseband normal atau rusak (IC Baseband / EFS NVRAM hilang).
* **Live Current Monitor & 📊 Kamus Arus USB:** Arus pengisian real-time (*mA*), voltase (*V*), dan tombol pembuka modal Kamus Analisa Amperemeter USB teknisi konter.
* **Kernel Fault Analyzer:** Memindai error bus I2C/SPI di log kernel.

#### 2. 💀 Tab HP Mati Total (Matot / Konslet)
* **Low-Level BootROM Handshake:** Deteksi otomatis Qualcomm 9008, MediaTek BROM / Preloader.
* **Kalkulator Analisis Arus Ampere:**
  * 0.00A (Jalur VBUS 5V putus / OVP jebol)
  * 0.01A - 0.08A Diam (Arus dingin: Osilator kristal 19.2MHz / IC Power belum bangkit)
  * 0.10A - 0.28A Gantung (Tegangan sekunder LDO drop / RAM error)
  * 0.40A - 0.90A Stuck (CPU normal / eMMC atau UFS lepas / rusak)
  * > 1.0A Langsung (KONSLET TOTAL jalur utama VPH_PWR / VDD_MAIN)
* **🔋 Dokter Baterai & Kalkulator Tegangan (BARU!):**
  * Masukkan angka hasil ukur voltmeter (misal: 3.66V, 2.4V, atau 0V).
  * Tool otomatis memberi notifikasi apakah tegangan kritis, apakah kuat booting, dan rekomendasi langsung (suntik 3 menit vs cas dinding 45 menit).
* **Panduan Pengukuran Multimeter (Borneo Schematics Style):** Titik ukur tegangan wajib teknisi.

#### 3. 📍 Tab Database Test Point & Jumper Force Power-On (Semua Brand Android)
* **Mode 1: ⚡ Force Power-On Tanpa Tombol (Akses ADB HP Rusak Tombol):**
  * Solusi khusus teknisi saat tombol power fisik rontok/rusak flexibel agar HP bisa menyala normal dan ADB terhubung:
  * **Xiaomi / Redmi / POCO:** Jumper titik kuningan `PWR_KEY` ke kaleng GND, fastboot reboot, dan trik auto-boot.
  * **Samsung Galaxy:** Jumper `PWR_SW` (1.8V), trik masuk Download Mode lalu Cancel (Vol Down 7 detik) untuk restart normal 100% tanpa tombol power.
  * **Oppo & Realme:** Jumper `KCOL0 / PWR` ke kaleng GND, trik menu ColorOS Recovery Reboot.
  * **Vivo & iQOO:** Jumper titik `POWER` ke kaleng, trik menu Fastboot Vivo Reboot.
  * **Infinix, Tecno, Itel:** Trik hard-reset siklus baterai saat charger tertancap (Auto-Boot MTK).
  * **Universal Android:** Panduan pengukuran multimeter tegangan standby pull-up 1.8V - 3.8V pada semua chipset Qualcomm, MediaTek, Unisoc, dan Exynos.
  * **Tombol Aksi Cepat 1-Klik:** Tombol langsung `🚀 Fastboot Reboot ke Normal` dan `⚡ Setel Auto-Boot Saat Cas (off-mode-charge 0)`.
* **Mode 2: 📍 Database Test Point EDL 9008 & BROM (Unbrick HP Mati Total):**
  * Kumpulan letak titik test point unbrick untuk Qualcomm 9008 dan MediaTek BROM lengkap dengan skematik ASCII motherboard.

#### 4. ⚡ Tab Flashing & Ganti Firmware
* **Flash Partisi Satuan (Fastboot):** Flash partisi `boot`, `recovery`, `vbmeta`, `super`, `system`, `vendor`, dll. Mendukung opsi `--disable-verity --disable-verification`.
* **Penyelamat Bootloop A/B:** Cek slot aktif dan switch instan (`Slot A` / `Slot B`).
* **Format / Wipe Bersih:** Fastboot `erase userdata` & `erase cache`.
* **ADB Sideload:** Pasang file firmware `.zip` (OTA / Recovery ROM) langsung saat HP di recovery mode.
* **Flash ROM Resmi Utuh:** Jalankan script batch ROM Fastboot (`flash_all.bat` Xiaomi, `flash-all.bat` Pixel).
* **Live Terminal Flashing:** Konsol log real-time melihat proses penulisan partisi.

#### 5. 🔌 Tab Driver USB & Filter Manager (UnlockTool Style)
* **Inspeksi Driver Windows Otomatis:** Deteksi registry untuk Qualcomm HS-USB QDLoader 9008, MediaTek USB VCOM / PreLoader, Samsung Mobile USB, Google ADB & LibUSB.
* **Akses Cepat Device Manager:** Tombol 1-klik membuka `devmgmt.msc`.
* **Tautan Download Resmi Driver:** Link langsung mengunduh driver OEM tanpa ribet.
* **Panduan Mengatasi Port Putus-Nyambung:** Solusi teknisi saat port 9008 atau BROM disconnect dalam 1 detik (pemasangan LibUSB filter, disable driver signature enforcement, dan pemilihan jalur USB).

#### 6. 🛠️ Tab Alat Uji Fisik Interaktif
* **Uji Getar (Vibrator):** Memicu motor getar (Android 8 - 15 + Sysfs).
* **Uji Lampu Senter (Flash LED):** Uji nyala LED flash kamera belakang.
* **Uji Audio Lengkap:**
  * **🔊 Buzzer Bawah:** Memutar nada uji ke speaker musik utama.
  * **📞 Earpiece Atas:** Mengalihkan suara ke speaker telinga depan (Voice Call Stream).
  * **🎙️ Mic Loopback:** Merekam suara 3 detik lalu memutar balik ke speaker untuk tes IC Audio Codec & mic.
* **Uji Layar (Dead Pixel):** Menampilkan warna solid (Merah, Hijau, Biru, Putih, Hitam).
* **Pendeteksi Tombol Fisik Real-Time:** Volume Up, Volume Down, Power button event listener.
* **👆 Uji Layar Sentuh (Touchscreen Digitizer & Dead-Zone Suite):**
  * **📍 Pointer Location (Jejak Sentuh Bawaan Android):** 1-klik mengaktifkan jejak garis sentuh merah/biru & koordinat realtime di layar HP untuk mencari jalur sentuhan yang putus/mati.
  * **🟩 Papan Kisi Uji (Matrix Grid Test):** Membuka kisi matrix interaktif 180 kotak di layar HP. Kotak otomatis berubah hijau saat diusap dan memberi respon getar (*haptic*). 100% lulus jika semua kotak terisi hijau.
  * **📡 Pantau Sentuhan Real-Time di PC:** Menangkap koordinat X, Y, status tekanan jari (*down/up*), dan deteksi *ghost touch* secara langsung di monitor PC via `getevent`.
  * **⚙️ Pintasan Menu Tes Pabrik (CIT / Factory Test):** Membuka menu hardware test bawaan Samsung (*#0*#), Xiaomi (CIT), Oppo/Realme, dan Vivo Engineer Mode.

#### 7. 🔄 Tab Menu Reboot
* Reboot Normal, Recovery, Fastboot, EDL 9008, Wakeup Screen, dan Shutdown.

#### 8. 📦 Tab Penyelamatan Data Pasien & Deteksi Akun (Layar Rusak / Lupa Email)
* **Solusi Khusus Teknisi saat Layar HP Pecah / Touch Mati / Tombol Rusak:**
  * **📧 Deteksi Akun Google (Gmail) & Akun Terpasang:** Membaca akun email Google / Gmail yang tersimpan di AccountManager sistem tanpa menyentuh layar atau memasukkan pola. Membantu konsumen yang ingin login di HP baru tapi lupa alamat email mereka.
  * **📋 Salin Akun Sekali Klik & Laporan Cetak (.txt):** Salin Gmail utama ke clipboard atau buat file rangkuman akun resmi siap cetak untuk diserahkan ke pelanggan.
  * **📇 Ekspor Kontak Telepon (.VCF / vCard 3.0):** Mengekstrak seluruh buku telepon via Contacts Content Provider tanpa perlu LCD hidup. Tinggal kirim file `.vcf` ke HP baru, sekali klik semua kontak langsung terimpor!
  * **💬 WhatsApp Hub (Backup & Ultra-Safe Restore Engine):**
    * **Backup Cepat & Fleksibel:** Pilihan backup "Hanya Database Chat (~10 detik, ringan & aman)" atau "Lengkap (Database + Semua File Media)". Menghasilkan manifest cadangan (`wa_manifest.json`) dan checksum SHA256.
    * **Restore Super Aman ke HP Baru:**
      * **Dual-Path Deployment:** Menyuntikkan database ke partisi Android 11+ (*Scoped Storage* `/sdcard/Android/media/com.whatsapp/WhatsApp/Databases`) sekaligus jalur Legacy (`/sdcard/WhatsApp/Databases`) demi kompatibilitas 100%.
      * **Normalisasi Database:** Otomatis mengubah nama cadangan harian (`msgstore-YYYY-MM-DD.1.db.cryptXX`) menjadi database aktif (`msgstore.db.cryptXX`) agar setup wizard WhatsApp HP baru langsung mendeteksinya.
      * **Proteksi Overwrite Target:** Otomatis mengamankan database lama di HP target ke `Databases_SAFETY_<timestamp>` sebelum restore.
      * **Auto-Permission via ADB:** Otomatis memberikan izin penyimpanan Android (`pm grant` & `appops set MANAGE_EXTERNAL_STORAGE allow`) sehingga WhatsApp tidak mem-bypass cadangan lokal saat pertama kali dibuka.
      * **Verifikasi Post-Restore:** Memeriksa keberadaan dan ukuran byte database di HP target setelah transfer.
  * **⚡ 1-Klik Penyelamatan Data Lengkap (Full Data Rescue):** Sekali klik langsung otomatis mendeteksi email Gmail, mengekstrak buku kontak `.vcf`, menyalin foto kamera (DCIM) dan dokumen penting ke satu folder pasien khusus (`customer_backup/Pasien_<Model>_<Timestamp>/`).
  * **🖥️ Screen Mirroring (Scrcpy) & Screenshot:** Tampilkan layar di monitor PC dan kendalikan dengan mouse komputer jika layar pecah tapi mesin masih hidup.
  * **🔓 Pintasan Bypass FRP & Hapus Kunci Layar (BARU!):**
    * Buka YouTube / Chrome via intent MTP/ADB di Setup Wizard.
    * Buka menu Settings langsung.
    * Lewati Setup Wizard (ADB Direct Home Screen Jump).
    * 1-Klik Fastboot Erase FRP (`frp`, `config`, `persistent`).
    * Hapus kunci pola/PIN/sandi tanpa menghapus data via TWRP/Root!
    * **⚡ 1-Klik Aktifkan ADB Samsung (Modem AT-Command Exploit):** Mengirim paket perintah AT via port `SAMSUNG Mobile USB Modem` (COM Port) untuk menyalakan daemon ADB secara otomatis (seperti SamFW Tool / Chimera).

#### 9. 📋 Tab Buku Pasien Konter (Database SQLite)
* Pencatatan servis, pencarian pasien, dan update status tiket: `[MASUK]`, `[DIKERJAKAN]`, `[TUNGGU PART]`, `[SELESAI]`, `[DIAMBIL]`.

#### 10. 📄 Tab Cetak Nota Servis
* Cetak nota tanda terima resmi berformat HTML / PDF lengkap dengan checklist diagnosa.

---

### 🚀 Cara Menjalankan
Buka folder:
`C:\Users\Administrator\Desktop\AndroidHardwareDoctor`
Lalu klik ganda file:
👉 **`run.bat`**
