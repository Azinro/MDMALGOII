import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from config import EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

def send_data_via_email(to_email: str, csv_file_path: str, subject: str = "Data Mahasiswa"):
    # 1. CEK APAKAH CSV ADA
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"File CSV tidak ditemukan di: {csv_file_path}")
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    try:
        df = pd.read_csv(csv_file_path)
        # Simpan xlsx di folder yang sama dengan csv
        excel_path = os.path.splitext(csv_file_path)[0] + '.xlsx'
        
        # Wajib punya openpyxl
        df.to_excel(excel_path, index=False, engine='openpyxl') 
    except Exception as e:
        raise Exception(f"Gagal convert ke Excel. Pastikan 'openpyxl' terinstall. Error: {e}")
    
    
    body = "Terlampir data mahasiswa dalam format Excel."
    msg.attach(MIMEText(body, 'plain'))

    df = pd.read_csv(csv_file_path)
    excel_path = csv_file_path.replace('.csv', '.xlsx')
    df.to_excel(excel_path, index=False)

    with open(excel_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {excel_path}',
        )
        msg.attach(part)

    server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, to_email, text)
    server.quit()