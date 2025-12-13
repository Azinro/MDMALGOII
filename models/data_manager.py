import pandas as pd
from models.mahasiswa import Mahasiswa
from models.exceptions import DataNotFound
from utils.sorters import merge_sort, shell_sort
from utils.searchers import binary_search
import os

class DataManager:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        if not os.path.exists(self.csv_path):
            df = pd.DataFrame(columns=["nama", "nim", "jenis_kelamin", "kelas", "prodi", "status"])
            df.to_csv(self.csv_path, index=False)

    def load_data(self):
        df = pd.read_csv(self.csv_path)
        df['nim'] = df['nim'].astype(str) # Pastikan NIM tetap string
        records = df.to_dict('records')
        mahasiswas = []
        for row in records:
            try:
                mhs = Mahasiswa(
                    nama=row['nama'],
                    nim=row['nim'],
                    jenis_kelamin=row['jenis_kelamin'],
                    kelas=row['kelas'],
                    prodi=row['prodi'],
                    status=row['status']
                )
                mahasiswas.append(mhs)
            except Exception as e:
                print(f"Data tidak valid dilewati: {row} - {e}")
        return mahasiswas

    def save_data(self,  list):
        df = pd.DataFrame([m.to_dict() for m in list])
        df.to_csv(self.csv_path, index=False)

    def add_mahasiswa(self, mhs: Mahasiswa):
        data = self.load_data()
        data.append(mhs)
        self.save_data(data)

    def update_mahasiswa(self, old_nim: str, new_mhs: Mahasiswa):
        data = self.load_data()
        for i, m in enumerate(data):
            if m.get_nim() == old_nim:
                data[i] = new_mhs
                break
        else:
            raise DataNotFound("Mahasiswa dengan NIM tersebut tidak ditemukan.")
        self.save_data(data)

    def delete_mahasiswa(self, nim: str):
        data = self.load_data()
        new_data = [m for m in data if m.get_nim() != nim]
        if len(new_data) == len(data):
            raise DataNotFound("Mahasiswa dengan NIM tersebut tidak ditemukan.")
        self.save_data(new_data)

    def search_by_nama_or_nim(self, query: str,  list):
        sorted_data = merge_sort(data, key_func=lambda m: m.get_nim())
        idx = binary_search(sorted_data, query, key_func=lambda m: m.get_nim())
        if idx != -1:
            return [sorted_data[idx]]
        # Jika pencarian nim gagal, coba cari nama
        sorted_data_nama = merge_sort(data, key_func=lambda m: m.get_nama())
        idx_nama = binary_search(sorted_data_nama, query, key_func=lambda m: m.get_nama())
        if idx_nama != -1:
            return [sorted_data_nama[idx_nama]]
        return []

    def sort_by_column(self, column: str, ascending: bool = True):
        data = self.load_data()
        if column in ['nama', 'nim', 'kelas']:
            sorted_data = merge_sort(data, key_func=lambda m: getattr(m, f'get_{column}')().lower())
        elif column in ['jenis_kelamin', 'prodi', 'status']:
            # Shell sort bekerja pada list mutable
            sorted_data = shell_sort([m for m in data], key_func=lambda m: getattr(m, f'get_{column}')().lower())
        else:
            raise ValueError("Kolom tidak valid untuk sorting.")
        if not ascending:
            sorted_data.reverse()
        return sorted_data