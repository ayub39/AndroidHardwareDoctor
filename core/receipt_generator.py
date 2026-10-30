import os
import sys
import time
import html
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DIR


class ReceiptGenerator:
    @staticmethod
    def generate_html_receipt(
        shop_name: str,
        shop_contact: str,
        customer_name: str,
        customer_phone: str,
        complaint: str,
        estimate_price: str,
        scan_data: dict
    ) -> str:
        date_str = time.strftime("%d-%m-%Y %H:%M")
        receipt_id = f"SRV-{int(time.time())}"

        # Sanitize HTML inputs
        s_shop_name = html.escape(shop_name or "KONTER SERVIS HP")
        s_shop_contact = html.escape(shop_contact or "Jasa Servis & Diagnosa Hardware HP Profesional")
        s_cust_name = html.escape(customer_name or "-")
        s_cust_phone = html.escape(customer_phone or "-")
        s_complaint = html.escape(complaint or "Cek Hardware Keseluruhan")
        s_estimate_price = html.escape(estimate_price or "Menunggu Konfirmasi Teknisi")

        # Extract diagnostic results
        dev = scan_data.get("device_info", {})
        bat = scan_data.get("battery", {})
        stor = scan_data.get("storage", {})
        disp = scan_data.get("display", {})
        touch = scan_data.get("touchscreen", {})
        cams = scan_data.get("cameras", {})
        sens = scan_data.get("sensors", {})
        faults = scan_data.get("hardware_faults", [])

        model_name = html.escape(
            f"{dev.get('brand', '')} {dev.get('model', '')}".strip() or
            scan_data.get('product') or
            scan_data.get('title') or
            "Android Device"
        )
        serial_no = html.escape(str(dev.get('serial') or scan_data.get('port') or 'N/A'))

        faults_html = ""
        if faults:
            for f in faults:
                cat = html.escape(str(f.get('category', '')))
                log_txt = html.escape(str(f.get('log', '')))
                faults_html += f"<li class='text-danger'><b>{cat}:</b> {log_txt}</li>"
        else:
            faults_html = "<li class='text-success'>Tidak terdeteksi error bus hardware fatal di log kernel.</li>"

        html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Nota Servis - {receipt_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .receipt-card {{
            max-width: 680px;
            margin: auto;
            background: #fff;
            padding: 25px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-top: 5px solid #007ACC;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px dashed #ddd;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: #007ACC;
        }}
        .header p {{
            margin: 4px 0 0;
            color: #666;
            font-size: 13px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        .info-box {{
            background: #f9fbfd;
            border: 1px solid #e1e8ed;
            padding: 10px 14px;
            border-radius: 6px;
        }}
        .info-box h4 {{
            margin: 0 0 6px;
            color: #444;
            font-size: 13px;
            border-bottom: 1px solid #e1e8ed;
            padding-bottom: 4px;
        }}
        .diag-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        .diag-table th, .diag-table td {{
            border: 1px solid #e1e8ed;
            padding: 8px 10px;
            text-align: left;
        }}
        .diag-table th {{
            background: #f0f4f8;
            color: #333;
        }}
        .badge-ok {{
            color: #107c41;
            font-weight: bold;
        }}
        .badge-warn {{
            color: #d83b01;
            font-weight: bold;
        }}
        .badge-danger {{
            color: #a80000;
            font-weight: bold;
        }}
        .faults-section {{
            background: #fff8f5;
            border: 1px solid #ffd6cc;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 12px;
        }}
        .text-danger {{ color: #d83b01; }}
        .text-success {{ color: #107c41; }}
        .estimate-box {{
            background: #e8f4fd;
            border: 1px solid #b8daff;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            color: #0056b3;
            margin-bottom: 25px;
        }}
        .signatures {{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            text-align: center;
            font-size: 13px;
        }}
        .sig-box {{
            width: 200px;
        }}
        .sig-line {{
            margin-top: 55px;
            border-top: 1px solid #333;
        }}
        .btn-print {{
            display: block;
            width: 100%;
            background: #007ACC;
            color: white;
            text-align: center;
            padding: 12px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 20px;
            cursor: pointer;
            border: none;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .receipt-card {{ box-shadow: none; border-top: none; padding: 0; }}
            .btn-print {{ display: none; }}
        }}
    </style>
</head>
<body>

<div class="receipt-card">
    <div class="header">
        <h1>{s_shop_name}</h1>
        <p>{s_shop_contact}</p>
        <p><b>No. Tanda Terima:</b> {receipt_id} | <b>Waktu Masuk:</b> {date_str}</p>
    </div>

    <div class="info-grid">
        <div class="info-box">
            <h4>DATA KONSUMEN</h4>
            <p><b>Nama:</b> {s_cust_name}</p>
            <p><b>No. HP / WA:</b> {s_cust_phone}</p>
            <p><b>Keluhan:</b> {s_complaint}</p>
        </div>
        <div class="info-box">
            <h4>IDENTITAS PERANGKAT</h4>
            <p><b>Tipe HP:</b> {model_name}</p>
            <p><b>Serial No:</b> {serial_no}</p>
            <p><b>No. IMEI:</b> {html.escape(str(dev.get('imei1', '-')))} ({html.escape(str(dev.get('signal_diagnosis', '-')))})</p>
            <p><b>RAM / OS:</b> {html.escape(str(dev.get('ram_total', '-')))} | Android {html.escape(str(dev.get('android_version', '-')))}</p>
            <p><b>Akun Google:</b> {html.escape(str(dev.get('google_accounts', '-')))}</p>
        </div>
    </div>

    <h4 style="margin: 0 0 8px; font-size: 14px;">HASIL SCAN HARDWARE VIA KABEL USB:</h4>
    <table class="diag-table">
        <tr>
            <th>Komponen</th>
            <th>Hasil Pengujian</th>
            <th>Status</th>
        </tr>
        <tr>
            <td><b>Baterai & IC Charger</b></td>
            <td>Kesehatan: {html.escape(str(bat.get('health_pct', '-')))} ({html.escape(str(bat.get('capacity_loss', '-')))}) | Siklus: {html.escape(str(bat.get('cycle_count', '-')))} | Kapasitas: {html.escape(str(bat.get('current_capacity', '-')))} / Asli {html.escape(str(bat.get('design_capacity', '-')))} | Voltase: {html.escape(str(bat.get('voltage', '-')))}</td>
            <td><span class="{ 'badge-ok' if bat.get('status_flag') == 'OK' else 'badge-danger' }">{html.escape(str(bat.get('status_flag', 'OK')))}</span></td>
        </tr>
        <tr>
            <td><b>Memori Internal (eMMC/UFS)</b></td>
            <td>Keausan: {html.escape(str(stor.get('wear_percentage', '-')))} | Cadangan Blok: {html.escape(str(stor.get('pre_eol_status', '-')))}</td>
            <td><span class="{ 'badge-ok' if stor.get('status_flag') == 'OK' else 'badge-warn' }">{html.escape(str(stor.get('status_flag', 'OK')))}</span></td>
        </tr>
        <tr>
            <td><b>Layar Display & Touch IC</b></td>
            <td>Resolusi: {html.escape(str(disp.get('resolution', '-')))} | Controller: {html.escape(str(touch.get('controller', '-')))}</td>
            <td><span class="{ 'badge-ok' if touch.get('status_flag') == 'OK' else 'badge-warn' }">{html.escape(str(touch.get('status_flag', 'OK')))}</span></td>
        </tr>
        <tr>
            <td><b>Sensor & Kamera</b></td>
            <td>Kamera: {cams.get('count', 0)} Modul | Sensor Aktif: {sens.get('detected_count', 0)} Unit</td>
            <td><span class="{ 'badge-ok' if cams.get('status_flag') == 'OK' else 'badge-danger' }">{html.escape(str(cams.get('status_flag', 'OK')))}</span></td>
        </tr>
    </table>

    <div class="faults-section">
        <b>Catatan IC & Bus Hardware (Kernel):</b>
        <ul style="margin: 4px 0 0; padding-left: 18px;">
            {faults_html}
        </ul>
    </div>

    <div class="estimate-box">
        <span>ESTIMASI BIAYA & PENGERJAAN:</span>
        <span>{s_estimate_price}</span>
    </div>

    <div class="signatures">
        <div class="sig-box">
            Pelanggan
            <div class="sig-line">{s_cust_name}</div>
        </div>
        <div class="sig-box">
            Teknisi Servis
            <div class="sig-line">{s_shop_name}</div>
        </div>
    </div>

    <button class="btn-print" onclick="window.print()">🖨️ CETAK NOTA / SIMPAN PDF</button>
</div>

</body>
</html>"""

        receipts_dir = os.path.join(APP_DIR, "receipts")
        os.makedirs(receipts_dir, exist_ok=True)
        file_path = os.path.join(receipts_dir, f"nota_{receipt_id}.html")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return file_path
        except OSError:
            return ""

    @staticmethod
    def open_receipt(file_path: str):
        if not file_path or not os.path.exists(file_path):
            return
        try:
            webbrowser.open(os.path.abspath(file_path))
        except Exception:
            pass
