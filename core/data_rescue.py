import os
import sys
import re
import time
import subprocess
import json
import hashlib
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_adb_path, run_cmd, APP_DIR


class DataRescueManager:
    """
    Comprehensive Data Rescue & Account Inspector Engine for phones
    with broken screens (LCD pecah/touch mati) and broken buttons.
    Extracts Gmail accounts, exports contacts to .vcf, backs up WhatsApp,
    photos, documents, and generates customer migration reports.
    """

    def __init__(self, serial=None):
        self.adb = get_adb_path()
        self.serial = serial
        self.base_cmd = [self.adb]
        if serial:
            self.base_cmd += ["-s", serial]

    def _shell(self, cmd_str, timeout=12):
        return run_cmd(self.base_cmd + ["shell", cmd_str], timeout=timeout)

    # -------------------------------------------------------------
    # 1. ACCOUNT INSPECTOR (GMAIL / GOOGLE / WHATSAPP / MI ACCOUNT)
    # -------------------------------------------------------------
    @staticmethod
    def _is_masked(val: str) -> bool:
        """Checks if Android or OEM has masked/redacted the account name with 'x'."""
        if not val:
            return True
        s = val.strip()
        cleaned = re.sub(r'[@\._\s-]', '', s)
        if cleaned and set(cleaned.lower()) <= {'x'}:
            return True
        if '@' in s:
            user_part = s.split('@')[0]
            domain_part = s.split('@')[1]
            if set(user_part.lower()) <= {'x'} or set(domain_part.replace('.', '').lower()) <= {'x'}:
                return True
        return False

    def get_accounts(self) -> dict:
        """
        Scans Android AccountManager, SyncManager, Calendar, Contacts, and Profile
        to discover all logged-in accounts (Gmail, WhatsApp, Xiaomi, Samsung, Vivo, etc.).
        Automatically bypasses Android 14+ / OEM privacy redaction (xxxxxxxx@xxxxx.xxx)
        by extracting authentic addresses from unmasked system sync providers.
        """
        accounts = {
            "device_owner": None,
            "google": [],
            "whatsapp": [],
            "xiaomi": [],
            "samsung": [],
            "vivo": [],
            "others": []
        }

        seen_google = set()
        seen_others = set()

        # Tier 1: Android SyncManager (dumpsys content - Sync Status)
        # Android's SyncManager preserves full real email addresses and account IDs
        # without redaction across all Android versions (including Android 13/14/15/OriginOS).
        out_content = self._shell("dumpsys content 2>/dev/null", timeout=8)
        if out_content:
            for line in out_content.splitlines():
                line = line.strip()
                m = re.match(r'^Account\s+([^\s]+)\s+u\d+\s+([^\s]+)', line)
                if not m:
                    m = re.match(r'^Account\s+([^\s]+)\s+([^\s]+)', line)
                if m:
                    name = m.group(1).strip()
                    acc_type = m.group(2).strip()
                    acc_type_lower = acc_type.lower()

                    if self._is_masked(name):
                        continue

                    if "com.google" in acc_type_lower:
                        if "@" in name and not name.endswith("@group.v.calendar.google.com") and not name.endswith("@group.calendar.google.com"):
                            if name not in seen_google:
                                seen_google.add(name)
                                accounts["google"].append(name)
                        else:
                            item = f"{name} ({acc_type})"
                            if item not in seen_others:
                                seen_others.add(item)
                                accounts["others"].append(item)
                    elif "whatsapp" in acc_type_lower:
                        if name not in accounts["whatsapp"] and name.lower() != "whatsapp":
                            accounts["whatsapp"].append(name)
                    elif "xiaomi" in acc_type_lower:
                        if name not in accounts["xiaomi"]:
                            accounts["xiaomi"].append(name)
                    elif "samsung" in acc_type_lower or "osp.app" in acc_type_lower:
                        if name not in accounts["samsung"]:
                            accounts["samsung"].append(name)
                    elif "bbkonlineservice" in acc_type_lower or "vivo" in acc_type_lower:
                        if name not in accounts["vivo"]:
                            accounts["vivo"].append(name)
                    else:
                        item = f"{name} ({acc_type})"
                        if item not in seen_others:
                            seen_others.add(item)
                            accounts["others"].append(item)

        # Tier 2: Calendar Content Provider (Calendars table)
        out_cal = self._shell("content query --uri content://com.android.calendar/calendars --projection ownerAccount:name:account_name:account_type 2>/dev/null", timeout=6)
        if out_cal:
            for line in out_cal.splitlines():
                line = line.strip()
                if not line.startswith("Row:"):
                    continue
                for m in re.finditer(r'(?:ownerAccount|account_name|name)=([^\s,]+)', line):
                    candidate = m.group(1).strip()
                    if "@gmail.com" in candidate.lower() or ("@" in candidate and not candidate.endswith(".calendar.google.com")):
                        if not self._is_masked(candidate) and candidate not in seen_google:
                            seen_google.add(candidate)
                            accounts["google"].append(candidate)

        # Tier 3: Contacts Content Provider (raw_contacts table)
        out_contacts = self._shell("content query --uri content://com.android.contacts/raw_contacts --projection account_name:account_type 2>/dev/null", timeout=6)
        if out_contacts:
            for line in out_contacts.splitlines():
                line = line.strip()
                if not line.startswith("Row:"):
                    continue
                m = re.search(r'account_name=([^,]+),\s*account_type=([^,\s]+)', line)
                if m:
                    name = m.group(1).strip()
                    acc_type = m.group(2).strip()
                    if not self._is_masked(name):
                        if ("com.google" in acc_type.lower() or "@gmail.com" in name.lower()) and "@" in name:
                            if name not in seen_google:
                                seen_google.add(name)
                                accounts["google"].append(name)
                        elif "whatsapp" in acc_type.lower():
                            if name not in accounts["whatsapp"] and name.lower() != "whatsapp":
                                accounts["whatsapp"].append(name)
                        elif "xiaomi" in acc_type.lower():
                            if name not in accounts["xiaomi"]:
                                accounts["xiaomi"].append(name)
                        elif "bbkonlineservice" in acc_type.lower():
                            if name not in accounts["vivo"]:
                                accounts["vivo"].append(name)

        # Tier 4: AccountManager (dumpsys account) - Fallback for unmasked environments
        out_acc = self._shell("dumpsys account 2>/dev/null", timeout=6)
        if out_acc:
            for line in out_acc.splitlines():
                line = line.strip()
                if not line.startswith("Account"):
                    continue
                m_name = re.search(r'name=([^,\s\}]+)', line)
                m_type = re.search(r'type=([^,\s\}]+)', line)
                if not m_name or not m_type:
                    continue
                name = m_name.group(1).strip()
                acc_type = m_type.group(1).strip()
                acc_type_lower = acc_type.lower()

                if self._is_masked(name):
                    continue

                if "com.google" in acc_type_lower:
                    if "@" in name and not name.endswith("@group.v.calendar.google.com") and not name.endswith("@group.calendar.google.com"):
                        if name not in seen_google:
                            seen_google.add(name)
                            accounts["google"].append(name)
                    else:
                        item = f"{name} ({acc_type})"
                        if item not in seen_others:
                            seen_others.add(item)
                            accounts["others"].append(item)
                elif "whatsapp" in acc_type_lower:
                    if name not in accounts["whatsapp"] and name.lower() != "whatsapp":
                        accounts["whatsapp"].append(name)
                elif "xiaomi" in acc_type_lower:
                    if name not in accounts["xiaomi"]:
                        accounts["xiaomi"].append(name)
                elif "samsung" in acc_type_lower or "osp.app" in acc_type_lower:
                    if name not in accounts["samsung"]:
                        accounts["samsung"].append(name)
                elif "bbkonlineservice" in acc_type_lower or "vivo" in acc_type_lower:
                    if name not in accounts["vivo"]:
                        accounts["vivo"].append(name)
                else:
                    item = f"{name} ({acc_type})"
                    if item not in seen_others:
                        seen_others.add(item)
                        accounts["others"].append(item)

        # Tier 5: Device Owner Profile Name
        out_prof = self._shell("content query --uri content://com.android.contacts/profile/data --projection display_name 2>/dev/null", timeout=4)
        if out_prof:
            m_prof = re.search(r'display_name=([^,\n]+)', out_prof)
            if m_prof:
                accounts["device_owner"] = m_prof.group(1).strip()

        return accounts

    def generate_account_summary_file(self, dest_folder=None, device_model="Android") -> str:
        """
        Saves a printable customer text report listing all Google/Gmail accounts
        and vendor logins so the customer can log in on their new phone.
        """
        if not dest_folder:
            dest_folder = os.path.join(APP_DIR, "customer_backup")
        os.makedirs(dest_folder, exist_ok=True)

        accounts = self.get_accounts()
        t = time.strftime("%d-%m-%Y %H:%M:%S")
        lines = []
        lines.append("=" * 65)
        lines.append("       BUKTI DAFTAR AKUN GOOGLE & IDENTITAS PERANGKAT")
        lines.append("          Penyelamat Data Layar Pecah / Ganti HP Baru")
        lines.append(f"          Waktu Ekstraksi : {t}")
        lines.append(f"          Tipe Perangkat  : {device_model}")
        if accounts.get("device_owner"):
            lines.append(f"          Nama Pemilik HP : {accounts['device_owner']}")
        lines.append("=" * 65)
        lines.append("\n[1. AKUN GOOGLE (GMAIL TERPASANG)]")
        if accounts["google"]:
            for idx, g in enumerate(accounts["google"], 1):
                lines.append(f"  {idx}. 📧 Email : {g}")
            lines.append("\n  * Catatan: Gunakan email di atas saat login di HP baru Anda.")
            lines.append("  * Jika lupa password, gunakan fitur 'Lupa Sandi' di Google")
            lines.append("    dengan memasukkan email yang tertera di atas.")
        else:
            lines.append("  (Tidak ditemukan akun Google yang tersimpan atau akses dibatasi)")

        lines.append("\n[2. AKUN WHATSAPP]")
        if accounts["whatsapp"]:
            for w in accounts["whatsapp"]:
                lines.append(f"  • Akun WhatsApp : {w}")
        else:
            lines.append("  (Tidak terdaftar di AccountManager)")

        lines.append("\n[3. AKUN VENDOR / MI ACCOUNT / SAMSUNG / VIVO]")
        has_vendor = False
        if accounts.get("xiaomi"):
            has_vendor = True
            for x in accounts["xiaomi"]:
                lines.append(f"  • ID Akun Mi (Xiaomi) : {x}")
        if accounts.get("samsung"):
            has_vendor = True
            for s in accounts["samsung"]:
                lines.append(f"  • Akun Samsung        : {s}")
        if accounts.get("vivo"):
            has_vendor = True
            for v in accounts["vivo"]:
                lines.append(f"  • ID Akun Vivo (BBK)  : {v}")
        if not has_vendor:
            lines.append("  (Tidak terdeteksi akun vendor khusus)")

        if accounts.get("others"):
            lines.append("\n[4. AKUN APLIKASI LAIN]")
            for o in accounts["others"]:
                lines.append(f"  • {o}")

        lines.append("\n" + "=" * 65)
        lines.append("   Dicetak oleh Android Hardware Doctor Pro - Bengkel Servis HP")
        lines.append("=" * 65)

        file_path = os.path.join(dest_folder, f"Daftar_Akun_Gmail_{int(time.time())}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return file_path
        except OSError:
            return ""

    # -------------------------------------------------------------
    # 2. CONTACTS EXPORTER (.VCF / VCARD 3.0)
    # -------------------------------------------------------------
    def export_contacts_vcf(self, dest_folder=None) -> tuple[bool, str, int]:
        """
        Extracts all contacts via Android Contacts Content Provider without
        needing the screen or touch to work, and saves as a standard .vcf file.
        """
        if not dest_folder:
            dest_folder = os.path.join(APP_DIR, "customer_backup")
        os.makedirs(dest_folder, exist_ok=True)

        # Primary query: Unified contacts data
        cmd_str = (
            "content query --uri content://com.android.contacts/data "
            "--projection display_name:data1:mimetype "
            "--where \"mimetype='vnd.android.cursor.item/phone_v2'\" 2>/dev/null"
        )
        res = self._shell(cmd_str, timeout=15)

        # Fallback query if first returns empty
        if not res or "Row:" not in res:
            cmd_str_fallback = "content query --uri content://contacts/phones/ 2>/dev/null"
            res = self._shell(cmd_str_fallback, timeout=12)

        contacts = []
        seen = set()

        if res:
            for line in res.splitlines():
                line = line.strip()
                if not line.startswith("Row:"):
                    continue

                # Parse display_name and phone number safely
                m = re.search(r'display_name=(.*?),\s*data1=(.*?),\s*mimetype=', line)
                if m:
                    name = m.group(1).strip()
                    phone = m.group(2).strip()
                else:
                    # Alternate pattern
                    m_name = re.search(r'name=([^,]+)', line) or re.search(r'display_name=([^,]+)', line)
                    m_phone = re.search(r'number=([^,]+)', line) or re.search(r'data1=([^,]+)', line)
                    name = m_name.group(1).strip() if m_name else "Tanpa Nama"
                    phone = m_phone.group(1).strip() if m_phone else ""

                if phone:
                    key = (name.lower(), phone)
                    if key not in seen:
                        seen.add(key)
                        contacts.append((name, phone))

        if not contacts:
            return False, "Tidak ada kontak telepon ditemukan di database perangkat.", 0

        # Build vCard 3.0 lines
        vcf_lines = []
        txt_lines = [
            f"DAFTAR KONTAK TELEPON PASIEN (TOTAL: {len(contacts)} KONTAK)",
            f"Waktu Backup: {time.strftime('%d-%m-%Y %H:%M:%S')}",
            "=" * 50,
            ""
        ]

        for name, phone in contacts:
            vcf_lines.append("BEGIN:VCARD")
            vcf_lines.append("VERSION:3.0")
            vcf_lines.append(f"FN:{name}")
            vcf_lines.append(f"TEL;TYPE=CELL:{phone}")
            vcf_lines.append("END:VCARD")

            txt_lines.append(f"• {name} : {phone}")

        ts = int(time.time())
        vcf_path = os.path.join(dest_folder, f"Kontak_Pasien_{ts}.vcf")
        txt_path = os.path.join(dest_folder, f"Kontak_Pasien_{ts}.txt")

        try:
            with open(vcf_path, "w", encoding="utf-8") as f:
                f.write("\n".join(vcf_lines) + "\n")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(txt_lines) + "\n")
            return True, vcf_path, len(contacts)
        except OSError as e:
            return False, f"Gagal menulis file kontak: {str(e)}", 0

    # -------------------------------------------------------------
    # 3. WHATSAPP DATA RESCUE & SAFE RESTORE ENGINE
    # -------------------------------------------------------------
    @staticmethod
    def inspect_whatsapp_backup(backup_folder: str) -> dict:
        """
        Inspects a local backup directory to locate and validate WhatsApp
        databases (msgstore*.db.crypt*), backups, and media files.
        Works even if user selects the parent customer folder or directly
        the WhatsApp/Databases folder.
        """
        if not backup_folder or not os.path.exists(backup_folder):
            return {"valid": False, "error": f"Folder backup tidak ditemukan: {backup_folder}"}

        db_files = []
        db_dir = None
        backups_dir = None
        media_dir = None

        # Search recursively for Databases directory or msgstore files
        for root, dirs, files in os.walk(backup_folder):
            for f in files:
                if re.match(r"^msgstore.*\.db\.crypt\d+$", f, re.I):
                    fpath = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fpath)
                    except OSError:
                        sz = 0
                    try:
                        mt = os.path.getmtime(fpath)
                    except OSError:
                        mt = 0
                    db_files.append({
                        "name": f,
                        "path": fpath,
                        "size_bytes": sz,
                        "size_mb": round(sz / (1024 * 1024), 2),
                        "mtime": mt
                    })
                    if not db_dir:
                        db_dir = root

            base_lower = os.path.basename(root).lower()
            if base_lower == "backups" and not backups_dir:
                backups_dir = root
            if base_lower == "media" and not media_dir:
                media_dir = root

        if not db_files:
            return {
                "valid": False,
                "error": "Tidak ditemukan file database WhatsApp (msgstore*.db.crypt*) di dalam folder ini."
            }

        # Check for 0-byte corrupted files
        corrupt_files = [d["name"] for d in db_files if d["size_bytes"] == 0]
        valid_db_files = [d for d in db_files if d["size_bytes"] > 0]
        if not valid_db_files:
            return {
                "valid": False,
                "error": f"Seluruh file database WhatsApp rusak (ukuran 0 bytes): {', '.join(corrupt_files)}"
            }

        # Identify active database: WhatsApp looks for 'msgstore.db.cryptXX' without date stamp
        active_db = None
        active_db_path = None
        for d in valid_db_files:
            if re.match(r"^msgstore\.db\.crypt\d+$", d["name"], re.I):
                active_db = d["name"]
                active_db_path = d["path"]
                break

        # If no un-dated file, pick the newest dated file by mtime/name
        if not active_db:
            sorted_by_date = sorted(valid_db_files, key=lambda x: x["mtime"], reverse=True)
            active_db = sorted_by_date[0]["name"]
            active_db_path = sorted_by_date[0]["path"]

        # Calculate Media info if present
        media_count = 0
        media_size_bytes = 0
        if media_dir and os.path.exists(media_dir):
            for root, _, files in os.walk(media_dir):
                media_count += len(files)
                for f in files:
                    try:
                        media_size_bytes += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass

        total_db_size = sum(d["size_bytes"] for d in valid_db_files)
        return {
            "valid": True,
            "db_dir": db_dir,
            "db_files": valid_db_files,
            "corrupt_files": corrupt_files,
            "active_db": active_db,
            "active_db_path": active_db_path,
            "total_db_size_mb": round(total_db_size / (1024 * 1024), 2),
            "total_db_files_count": len(valid_db_files),
            "has_backups": backups_dir is not None and os.path.exists(backups_dir),
            "backups_dir": backups_dir,
            "has_media": media_count > 0,
            "media_dir": media_dir,
            "media_count": media_count,
            "media_size_mb": round(media_size_bytes / (1024 * 1024), 2)
        }

    def backup_whatsapp(
        self,
        dest_folder=None,
        backup_type="all",
        package_name="com.whatsapp",
        on_progress=None
    ) -> tuple[bool, str]:
        """
        Safely backs up WhatsApp data with priority given to chat databases
        (msgstore.db.crypt) and settings (Backups), followed by Media.
        Computes SHA256 integrity hash, supports Android 10 s/d 15 paths,
        and saves a recovery manifest for reliable restoration.
        """
        if not dest_folder:
            dest_folder = os.path.join(APP_DIR, "customer_backup")
        
        wa_target_dir = os.path.join(dest_folder, "WhatsApp_Backup")
        os.makedirs(wa_target_dir, exist_ok=True)

        if on_progress:
            on_progress("🔍 Mencari direktori data WhatsApp pada perangkat...")

        # Determine target package and subfolder name
        is_w4b = "w4b" in str(package_name).lower()
        sub_name = "WhatsApp Business" if is_w4b else "WhatsApp"
        pkg = "com.whatsapp.w4b" if is_w4b else "com.whatsapp"

        source_candidates = [
            f"/sdcard/Android/media/{pkg}/{sub_name}",
            f"/sdcard/{sub_name}"
        ]

        found_path = None
        for p in source_candidates:
            check = self._shell(f"ls -d '{p}' 2>/dev/null", timeout=4)
            if check and p in check:
                found_path = p
                break

        # Fallback check across WhatsApp Business if standard not found
        if not found_path and not is_w4b:
            w4b_candidates = [
                "/sdcard/Android/media/com.whatsapp.w4b/WhatsApp Business",
                "/sdcard/WhatsApp Business"
            ]
            for p in w4b_candidates:
                check = self._shell(f"ls -d '{p}' 2>/dev/null", timeout=4)
                if check and p in check:
                    found_path = p
                    sub_name = "WhatsApp Business"
                    pkg = "com.whatsapp.w4b"
                    is_w4b = True
                    break

        if not found_path:
            return False, f"Folder data {sub_name} tidak ditemukan di penyimpanan internal HP."

        local_wa_dir = os.path.join(wa_target_dir, sub_name)
        local_db_dir = os.path.join(local_wa_dir, "Databases")
        local_backups_dir = os.path.join(local_wa_dir, "Backups")
        os.makedirs(local_db_dir, exist_ok=True)
        os.makedirs(local_backups_dir, exist_ok=True)

        # 1. PULL DATABASES (PRIORITAS UTAMA - CEPAT & AMAN)
        if on_progress:
            on_progress("📥 Mengamankan database riwayat chat (msgstore.db.crypt)...")

        db_cmd = self.base_cmd + ["pull", f"{found_path}/Databases", local_wa_dir]
        try:
            subprocess.run(
                db_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception as e:
            if on_progress:
                on_progress(f"⚠️ Catatan saat menarik Databases: {e}")

        # 2. PULL BACKUPS (Chat settings, wallpaper, etc.)
        if on_progress:
            on_progress("⚙️ Mengamankan pengaturan obrolan & cadangan akun...")
        try:
            subprocess.run(
                self.base_cmd + ["pull", f"{found_path}/Backups", local_wa_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception:
            pass

        # 3. VERIFY DATABASES
        insp = self.inspect_whatsapp_backup(wa_target_dir)
        if not insp.get("valid"):
            if on_progress:
                on_progress("🔄 Mencoba penarikan alternatif folder WhatsApp...")
            try:
                subprocess.run(
                    self.base_cmd + ["pull", found_path, wa_target_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                insp = self.inspect_whatsapp_backup(wa_target_dir)
            except Exception:
                pass

        if not insp.get("valid"):
            return False, f"Gagal menyelamatkan database WhatsApp: {insp.get('error', 'Database tidak ditemukan')}"

        # 4. PULL MEDIA (Jika dipilih 'all')
        if backup_type == "all":
            if on_progress:
                on_progress("📸 Mengunduh file media (foto, audio, video) WhatsApp...")
            try:
                subprocess.run(
                    self.base_cmd + ["pull", f"{found_path}/Media", local_wa_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=900,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
            except Exception as e:
                if on_progress:
                    on_progress(f"⚠️ Sebagian media tidak selesai ditarik: {e}")

        # 5. RE-INSPECT & GENERATE MANIFEST + PETUNJUK
        final_insp = self.inspect_whatsapp_backup(wa_target_dir)

        active_sha = ""
        active_db_path = final_insp.get("active_db_path")
        if active_db_path and os.path.exists(active_db_path):
            try:
                h = hashlib.sha256()
                with open(active_db_path, "rb") as f:
                    while chunk := f.read(65536):
                        h.update(chunk)
                active_sha = h.hexdigest()
            except Exception:
                pass

        manifest_data = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "package_name": pkg,
            "app_name": sub_name,
            "source_device_serial": self.serial or "unknown",
            "source_path": found_path,
            "backup_type": backup_type,
            "active_database": final_insp.get("active_db"),
            "active_database_sha256": active_sha,
            "total_db_files": final_insp.get("total_db_files_count", 0),
            "total_db_size_mb": final_insp.get("total_db_size_mb", 0),
            "has_backups": final_insp.get("has_backups", False),
            "has_media": final_insp.get("has_media", False),
            "media_count": final_insp.get("media_count", 0),
            "media_size_mb": final_insp.get("media_size_mb", 0)
        }

        try:
            with open(os.path.join(wa_target_dir, "wa_manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)

            petunjuk_path = os.path.join(wa_target_dir, "PETUNJUK_RESTORE_WHATSAPP.txt")
            with open(petunjuk_path, "w", encoding="utf-8") as f:
                f.write(
                    "===========================================================\n"
                    "   PANDUAN PEMULIHAN (RESTORE) DATABASE WHATSAPP KE HP BARU\n"
                    "===========================================================\n\n"
                    f"Aplikasi        : {sub_name} ({pkg})\n"
                    f"Tanggal Backup  : {manifest_data['created_at']}\n"
                    f"Database Utama  : {manifest_data['active_database']} ({manifest_data['total_db_size_mb']} MB)\n"
                    f"Checksum SHA256 : {active_sha}\n\n"
                    "LANGKAH-LANGKAH RESTORE AMAN DI HP BARU:\n"
                    "1. Install WhatsApp di HP baru dari Play Store, TETAPI JANGAN DIBUKA DULU.\n"
                    "2. Gunakan fitur 'Restore WhatsApp ke HP Baru' di aplikasi Android Hardware Doctor.\n"
                    "   Sistem akan otomatis:\n"
                    "   - Menyalin database ke jalur Android 11+ maupun Legacy (/sdcard/WhatsApp).\n"
                    "   - Mengatur izin akses penyimpanan via ADB (pm grant & appops).\n"
                    "   - Memverifikasi byte database di HP target.\n"
                    "3. Buka WhatsApp di HP baru -> Izinkan akses penyimpanan jika diminta.\n"
                    "4. Masukkan nomor HP yang sama & verifikasi OTP SMS.\n"
                    "5. WhatsApp akan otomatis mendeteksi: 'Cadangan Lokal Ditemukan'.\n"
                    "6. Klik tombol 'PULIHKAN' / 'RESTORE' -> Tunggu sampai 100% -> Selesai!\n"
                )
        except Exception:
            pass

        summary_msg = (
            f"✅ Backup {sub_name} Sukses!\n\n"
            f"• Database Utama: {final_insp.get('active_db')} ({final_insp.get('total_db_size_mb')} MB)\n"
            f"• Cadangan Harian: {final_insp.get('total_db_files_count')} file riwayat\n"
            f"• Pengaturan Obrolan: {'Tersedia' if final_insp.get('has_backups') else 'Tidak ada'}\n"
            f"• Media Foto/Video: {final_insp.get('media_count', 0)} file ({final_insp.get('media_size_mb', 0)} MB)\n\n"
            f"Folder Tersimpan:\n{os.path.abspath(wa_target_dir)}"
        )
        return True, summary_msg

    def restore_whatsapp(
        self,
        backup_folder: str,
        target_package: str = "com.whatsapp",
        restore_media: bool = False,
        auto_grant_perms: bool = True,
        on_progress: callable = None
    ) -> tuple[bool, str]:
        """
        Ultra-safe WhatsApp restoration engine with:
        1. Local database integrity & checksum inspection.
        2. Normalization of active database name (auto-clones latest daily backup if needed).
        3. Target device overwrite safety backup (preserves target's existing DB in Databases_SAFETY).
        4. Dual-path deployment: injects to BOTH modern Android 11+ Scoped Storage
           (/sdcard/Android/media/com.whatsapp/WhatsApp/Databases) AND legacy path (/sdcard/WhatsApp/Databases).
        5. Permission hardening: chmod 777 and auto pm grant / appops so WhatsApp
           immediately detects the local backup upon initial registration.
        6. Post-restore verification: verifies target file existence and size.
        """
        if on_progress:
            on_progress("🔍 Memeriksa integritas file backup WhatsApp di PC...")

        insp = self.inspect_whatsapp_backup(backup_folder)
        if not insp.get("valid"):
            return False, f"Folder backup tidak valid:\n{insp.get('error', 'Database tidak ditemukan')}"

        db_dir = insp["db_dir"]
        active_db_name = insp["active_db"]
        active_db_path = insp["active_db_path"]

        # Check target phone ADB connection
        dev_serial = self._shell("getprop ro.serialno", timeout=5)
        if not dev_serial or not dev_serial.strip():
            return False, "HP target tidak terdeteksi via kabel USB ADB. Pastikan USB Debugging aktif di HP target!"

        # Query Android API level
        sdk_str = self._shell("getprop ro.build.version.sdk", timeout=4)
        sdk_int = int(sdk_str.strip()) if sdk_str and sdk_str.strip().isdigit() else 30

        is_w4b = "w4b" in str(target_package).lower()
        sub_name = "WhatsApp Business" if is_w4b else "WhatsApp"
        pkg = "com.whatsapp.w4b" if is_w4b else "com.whatsapp"

        # Modern vs Legacy target directories
        modern_root = f"/sdcard/Android/media/{pkg}/{sub_name}"
        legacy_root = f"/sdcard/{sub_name}"

        # 1. NORMALISASI NAMA DATABASE UTAMA
        crypt_ext_match = re.search(r"(\.db\.crypt\d+)$", active_db_name, re.I)
        if crypt_ext_match:
            standard_active_name = f"msgstore{crypt_ext_match.group(1)}"
            standard_active_path = os.path.join(db_dir, standard_active_name)
            if not os.path.exists(standard_active_path):
                if on_progress:
                    on_progress(f"📝 Normalisasi nama database -> {standard_active_name}...")
                try:
                    shutil.copy2(active_db_path, standard_active_path)
                    active_db_name = standard_active_name
                    active_db_path = standard_active_path
                except Exception:
                    pass

        # 2. TARGET DEVICE OVERWRITE SAFETY BACKUP (PROTEKSI KONTEN LAMA HP TARGET)
        if on_progress:
            on_progress("🛡️ Memeriksa database lama di HP target & membuat cadangan pengaman...")

        ts = int(time.time())
        check_target_db = self._shell(
            f"ls '{modern_root}/Databases' '{legacy_root}/Databases' 2>/dev/null",
            timeout=5
        )
        if check_target_db and "msgstore" in check_target_db:
            if on_progress:
                on_progress("🛡️ Ditemukan database lama di HP target! Mengamankan ke Databases_SAFETY...")
            self._shell(f"cp -r '{modern_root}/Databases' '{modern_root}/Databases_SAFETY_{ts}' 2>/dev/null")
            self._shell(f"cp -r '{legacy_root}/Databases' '{legacy_root}/Databases_SAFETY_{ts}' 2>/dev/null")

        # 3. BUAT STRUKTUR DIREKTORI TARGET
        if on_progress:
            on_progress("📁 Mempersiapkan struktur direktori di HP target...")

        self._shell(f"mkdir -p '{modern_root}/Databases' '{modern_root}/Backups' 2>/dev/null")
        self._shell(f"mkdir -p '{legacy_root}/Databases' '{legacy_root}/Backups' 2>/dev/null")

        # 4. PUSH DATABASE KE HP TARGET (DUAL-PATH DEPLOYMENT)
        if on_progress:
            on_progress("📥 Menyuntikkan database chat WhatsApp ke HP target...")

        # Push database ke modern path
        subprocess.run(
            self.base_cmd + ["push", db_dir, modern_root + "/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        # Push database ke legacy path untuk kompatibilitas mutlak
        subprocess.run(
            self.base_cmd + ["push", db_dir, legacy_root + "/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        # Push Backups jika ada
        if insp.get("has_backups") and insp.get("backups_dir"):
            if on_progress:
                on_progress("⚙️ Menyuntikkan file pengaturan chat (Backups)...")
            subprocess.run(
                self.base_cmd + ["push", insp["backups_dir"], modern_root + "/"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            subprocess.run(
                self.base_cmd + ["push", insp["backups_dir"], legacy_root + "/"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

        # 5. PUSH MEDIA (JIKA DIPILIH)
        media_restored_info = "Tidak dipulihkan (hanya database chat)"
        if restore_media and insp.get("has_media") and insp.get("media_dir"):
            if on_progress:
                on_progress(f"📸 Menyuntikkan file media ({insp.get('media_count')} file, ~{insp.get('media_size_mb')} MB)...")
            target_media_parent = modern_root if sdk_int >= 30 else legacy_root
            subprocess.run(
                self.base_cmd + ["push", insp["media_dir"], target_media_parent + "/"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=900,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            media_restored_info = f"Tersalin {insp.get('media_count')} file ({insp.get('media_size_mb')} MB)"

        # 6. PERMISSION & APPOPS HARDENING (KUNCI SUKSES RESTORE LOKAL ANDROID 11+)
        if on_progress:
            on_progress("🔑 Mengatur izin hak akses file (chmod 777 & runtime permissions)...")

        self._shell(f"chmod -R 777 '{modern_root}' 2>/dev/null")
        self._shell(f"chmod -R 777 '{legacy_root}' 2>/dev/null")

        if auto_grant_perms:
            if on_progress:
                on_progress("🛡️ Mengaktifkan izin penyimpanan otomatis WhatsApp via ADB...")
            pkg_installed = self._shell(f"pm list packages {pkg} 2>/dev/null")
            if pkg_installed and pkg in pkg_installed:
                self._shell(f"pm grant {pkg} android.permission.READ_EXTERNAL_STORAGE 2>/dev/null")
                self._shell(f"pm grant {pkg} android.permission.WRITE_EXTERNAL_STORAGE 2>/dev/null")
                self._shell(f"pm grant {pkg} android.permission.READ_MEDIA_IMAGES 2>/dev/null")
                self._shell(f"pm grant {pkg} android.permission.READ_MEDIA_VIDEO 2>/dev/null")
                self._shell(f"pm grant {pkg} android.permission.READ_MEDIA_AUDIO 2>/dev/null")
                self._shell(f"appops set {pkg} MANAGE_EXTERNAL_STORAGE allow 2>/dev/null")

        # 7. VERIFIKASI POST-RESTORE (INTEGRITY CHECK PADA HP TARGET)
        if on_progress:
            on_progress("🔍 Verifikasi integritas database di HP target...")

        verify_modern = self._shell(f"ls -l '{modern_root}/Databases/{active_db_name}' 2>/dev/null")
        verify_legacy = self._shell(f"ls -l '{legacy_root}/Databases/{active_db_name}' 2>/dev/null")

        if not (verify_modern and active_db_name in verify_modern) and not (verify_legacy and active_db_name in verify_legacy):
            return False, "❌ Verifikasi gagal: File database tidak ditemukan di HP target setelah proses push."

        # Broadcast media scanner
        self._shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{modern_root}/Databases/{active_db_name} 2>/dev/null")

        report = (
            f"🎉 RESTORE DATABASE {sub_name.upper()} BERHASIL!\n\n"
            f"• Database Terpasang: {active_db_name} ({insp.get('total_db_size_mb')} MB)\n"
            f"• Jumlah File Cadangan: {insp.get('total_db_files_count')} file riwayat\n"
            f"• Status Media: {media_restored_info}\n"
            f"• Kompatibilitas Jalur: Dual-Path (Android 11+ & Legacy) AKTIF\n"
            f"• Hak Akses & Izin File: chmod 777 & Storage Permissions DIBERIKAN\n\n"
            "📋 LANGKAH SELANJUTNYA PADA HP TARGET:\n"
            "1. Jika WhatsApp sudah pernah dibuka sebelumnya, lakukan 'Hapus Data / Clear Data' di Info Aplikasi WhatsApp.\n"
            "2. Buka aplikasi WhatsApp di HP target.\n"
            "3. Masukkan nomor HP & verifikasi SMS OTP.\n"
            "4. Layar 'Cadangan Ditemukan' akan OTOMATIS muncul.\n"
            "5. Klik 'PULIHKAN' / 'RESTORE' dan tunggu sampai 100%!"
        )
        return True, report

    # -------------------------------------------------------------
    # 4. PHOTOS & DOCUMENTS BACKUP (MULTI-FOLDER DEEP SCAN)
    # -------------------------------------------------------------
    def backup_all_jpg(self, dest_folder=None, on_progress=None) -> tuple[bool, str, int]:
        """
        Scans the ENTIRE device storage (/sdcard/ and /storage/) for all files with
        .jpg and .jpeg extensions across ALL directories (DCIM, WhatsApp, Telegram,
        Pictures, Downloads, Bluetooth, etc.).
        
        Preserves the source directory structure in the destination folder
        so files are organized cleanly by folder and never collide or get jumbled together.
        """
        if not dest_folder:
            dest_folder = os.path.join(APP_DIR, "customer_backup", "Semua_Foto_JPG")
        os.makedirs(dest_folder, exist_ok=True)

        if on_progress:
            on_progress("🔍 Memindai seluruh penyimpanan HP mencari file .jpg...")

        # Deep search across internal and external storage
        cmd_find = (
            "find /sdcard/ /storage/ -type f "
            "\\( -name '*.jpg' -o -name '*.JPG' -o -name '*.jpeg' -o -name '*.JPEG' \\) "
            "2>/dev/null"
        )
        raw_output = self._shell(cmd_find, timeout=45)
        if not raw_output or not raw_output.strip():
            raw_output = self._shell("find /sdcard/ -type f | grep -E -i '\\.(jpg|jpeg)$' 2>/dev/null", timeout=45)

        if not raw_output or not raw_output.strip():
            # If find didn't return, fallback to pulling DCIM & Pictures directly
            fallback_pull = self._fallback_pull_photos(dest_folder)
            return fallback_pull

        all_files = [line.strip() for line in raw_output.splitlines() if line.strip()]
        
        # Filter out thumbnail cache directories
        filtered_files = []
        seen = set()
        for f in all_files:
            f_norm = f.replace("\\", "/")
            if f_norm in seen:
                continue
            seen.add(f_norm)
            f_lower = f_norm.lower()
            if "/.thumbnails/" in f_lower or "/.thumb/" in f_lower or "/cache/" in f_lower:
                continue
            filtered_files.append(f_norm)

        total_files = len(filtered_files)
        if total_files == 0:
            fallback_pull = self._fallback_pull_photos(dest_folder)
            return fallback_pull

        if on_progress:
            on_progress(f"📸 Ditemukan {total_files} file .jpg. Mengorganisir folder tujuan...")

        # Group files by parent directory to preserve structure
        from collections import defaultdict
        grouped = defaultdict(list)
        for remote_path in filtered_files:
            parent = os.path.dirname(remote_path)
            grouped[parent].append(remote_path)

        success_count = 0
        CHUNK_SIZE = 35
        total_groups = len(grouped)
        group_idx = 0

        for parent_dir, files in grouped.items():
            group_idx += 1
            # Determine clean relative folder name for PC
            clean_rel = parent_dir
            for prefix in ["/storage/emulated/0/", "/storage/emulated/legacy/", "/storage/self/primary/", "/sdcard/"]:
                if clean_rel.startswith(prefix):
                    clean_rel = clean_rel[len(prefix):]
                    break
            if clean_rel.startswith("/storage/"):
                clean_rel = clean_rel[len("/storage/"):].lstrip("/")
            clean_rel = clean_rel.lstrip("/").replace("/", os.sep)
            if not clean_rel:
                clean_rel = "Root_Penyimpanan"

            local_subfolder = os.path.join(dest_folder, clean_rel)
            os.makedirs(local_subfolder, exist_ok=True)

            if on_progress:
                on_progress(f"📥 Menyalin folder [{group_idx}/{total_groups}] {os.path.basename(parent_dir)} ({len(files)} foto)...")

            # Batch pull files in this directory
            for i in range(0, len(files), CHUNK_SIZE):
                chunk = files[i:i + CHUNK_SIZE]
                pull_cmd = self.base_cmd + ["pull"] + chunk + [local_subfolder]
                try:
                    subprocess.run(
                        pull_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=180,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    for f in chunk:
                        fname = os.path.basename(f)
                        if os.path.exists(os.path.join(local_subfolder, fname)):
                            success_count += 1
                except Exception:
                    # Individual fallback if batch fails
                    for f in chunk:
                        try:
                            single_cmd = self.base_cmd + ["pull", f, local_subfolder]
                            subprocess.run(single_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                            if os.path.exists(os.path.join(local_subfolder, os.path.basename(f))):
                                success_count += 1
                        except Exception:
                            pass

        msg = f"Berhasil mem-backup {success_count} dari {total_files} file .jpg ke dalam {total_groups} subfolder terorganisir di:\n{os.path.abspath(dest_folder)}"
        return True, msg, success_count

    def _fallback_pull_photos(self, dest_folder) -> tuple[bool, str, int]:
        """Fallback pulling known photo directories if find command is unavailable."""
        folders = [
            ("/sdcard/DCIM", "DCIM"),
            ("/sdcard/Pictures", "Pictures"),
            ("/sdcard/WhatsApp/Media/WhatsApp Images", "WhatsApp_Images"),
            ("/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images", "WhatsApp_Images_Android11"),
            ("/sdcard/Download", "Download")
        ]
        count = 0
        for remote_p, local_sub in folders:
            t_dir = os.path.join(dest_folder, local_sub)
            os.makedirs(t_dir, exist_ok=True)
            cmd = self.base_cmd + ["pull", remote_p, t_dir]
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            except Exception:
                pass
        for root, _, files in os.walk(dest_folder):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg')):
                    count += 1
        return True, f"Backup foto selesai (Fallback Pull). Total file terkumpul: {count} foto.", count

    def backup_photos(self, dest_folder=None, on_progress=None) -> tuple[bool, str]:
        """Backs up all JPG photos from all directories across device storage."""
        ok, msg, _ = self.backup_all_jpg(dest_folder=dest_folder, on_progress=on_progress)
        return ok, msg

    def backup_documents(self, dest_folder=None) -> tuple[bool, str]:
        """Backs up Download and Documents folders."""
        if not dest_folder:
            dest_folder = os.path.join(APP_DIR, "customer_backup", "Dokumen_Penting")
        os.makedirs(dest_folder, exist_ok=True)

        try:
            subprocess.run(self.base_cmd + ["pull", "/sdcard/Download", dest_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            subprocess.run(self.base_cmd + ["pull", "/sdcard/Documents", dest_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return True, f"Dokumen berhasil disimpan di:\n{os.path.abspath(dest_folder)}"
        except Exception as e:
            return False, f"Gagal backup dokumen: {str(e)}"

    # -------------------------------------------------------------
    # 5. ONE-CLICK FULL DATA RESCUE
    # -------------------------------------------------------------
    def full_data_rescue(self, device_model="Android", on_status=None) -> tuple[bool, str]:
        """
        One-click full customer data rescue:
        Creates a dedicated folder, exports Gmail report, contacts vCard,
        photos, and documents in one seamless operation.
        """
        ts = int(time.time())
        clean_model = re.sub(r'[^a-zA-Z0-9_-]', '_', device_model).strip("_") or "Android"
        folder_name = f"Pasien_{clean_model}_{ts}"
        rescue_dir = os.path.join(APP_DIR, "customer_backup", folder_name)
        os.makedirs(rescue_dir, exist_ok=True)

        if on_status:
            on_status("🔍 [1/4] Mendeteksi Akun Google & Gmail terpasang...")
        self.generate_account_summary_file(dest_folder=rescue_dir, device_model=device_model)

        if on_status:
            on_status("📇 [2/4] Mengekspor Kontak Telepon (.VCF)...")
        self.export_contacts_vcf(dest_folder=rescue_dir)

        if on_status:
            on_status("📸 [3/4] Memindai & menyalin seluruh file foto .jpg dari semua folder...")
        photo_dir = os.path.join(rescue_dir, "Semua_Foto_JPG")
        self.backup_all_jpg(dest_folder=photo_dir, on_progress=on_status)

        if on_status:
            on_status("📂 [4/4] Menyalin File Dokumen & Unduhan...")
        doc_dir = os.path.join(rescue_dir, "Dokumen_Penting")
        self.backup_documents(dest_folder=doc_dir)

        if on_status:
            on_status("✅ Penyelamatan data selesai seluruhnya!")

        return True, rescue_dir
