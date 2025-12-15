# test_email.py
import os
import smtplib
from dotenv import load_dotenv

# Paksa load .env
load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")

print(f"Mencoba login dengan Email: {email}")
# Jangan print password demi keamanan, tapi cek panjangnya
print(f"Panjang Password: {len(str(password))} karakter")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("Koneksi TLS berhasil...")
    
    server.login(email, password)
    print("LOGIN BERHASIL! Codingan aman, masalahnya ada di tempat lain.")
    server.quit()
except Exception as e:
    print("---------------------------")
    print("LOGIN GAGAL. Errornya adalah:")
    print(e)
    print("---------------------------")
    if "Username and Password not accepted" in str(e):
        print("TIPS: Ini berarti kamu belum pakai App Password atau salah ketik.")