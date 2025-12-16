import smtplib
import os
import sys
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from config import EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

# --- DEBUGGER ---
def log_debug(msg):
    print(f"[EMAIL DEBUG] {msg}", file=sys.stdout, flush=True)

# --- FIX IPv4 ---
def force_ipv4_socket():
    old_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        responses = old_getaddrinfo(*args, **kwargs)
        return [r for r in responses if r[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo

def send_data_via_email(to_email: str, csv_file_path: str, subject: str = "Data Mahasiswa"):
    force_ipv4_socket() # Aktifkan paksa IPv4
    
    log_debug(f"Memulai proses email ke: {to_email} via Port {EMAIL_SMTP_PORT}")
    
    if not os.path.exists(csv_file_path):
        log_debug("File CSV tidak ditemukan!")
        raise FileNotFoundError(f"File tidak ada: {csv_file_path}")

    # Convert Excel
    try:
        log_debug("Mengconvert CSV ke Excel...")
        df = pd.read_csv(csv_file_path)
        excel_path = csv_file_path.replace('.csv', '.xlsx')
        df.to_excel(excel_path, index=False)
        log_debug("Convert sukses.")
    except Exception as e:
        log_debug(f"Gagal convert excel: {e}")
        raise e

    # Setup Email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText("Terlampir data mahasiswa (Excel).", 'plain'))

    with open(excel_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename=Data_Mahasiswa.xlsx')
        msg.attach(part)

    try:
        log_debug(f"Menghubungi Gmail pakai SSL (Port 465)...")
        
        # PAKE SMTP_SSL
        server = smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, timeout=30)
        
        # HAPUS server.starttls()
        
        log_debug("Mencoba Login...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        log_debug("Mengirim pesan...")
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        
        log_debug("Logout...")
        server.quit()
        
        log_debug("SUKSES TERKIRIM!")
        
    except Exception as e:
        log_debug(f"ERROR SAAT KIRIM: {e}")
        raise e