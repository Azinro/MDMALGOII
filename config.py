import os
from dotenv import load_dotenv

load_dotenv()  # Ini akan membaca file .env

# --- Konfigurasi File ---
CSV_MAHASISWA = "data/mahasiswa.csv"
CSV_USERS = "data/users.csv"

# --- Konfigurasi Email ---
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Inisialisasi Folder Data ---
os.makedirs("data", exist_ok=True)

# Buat file mahasiswa.csv jika belum ada
if not os.path.exists(CSV_MAHASISWA):
    import pandas as pd
    df_empty = pd.DataFrame(columns=["nama", "nim", "jenis_kelamin", "kelas", "prodi", "status"])
    df_empty.to_csv(CSV_MAHASISWA, index=False)

# Buat file users.csv jika belum ada
if not os.path.exists(CSV_USERS):
    import pandas as pd
    df_users = pd.DataFrame(columns=["username", "password", "role"])
    df_users.to_csv(CSV_USERS, index=False)
    # Tambahkan user default
    df_default = pd.DataFrame([{
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    },
    {
        "username": "user",
        "password": "user123",
        "role": "user"
    }])
    df_default.to_csv(CSV_USERS, mode='a', header=False, index=False)