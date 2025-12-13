from .exceptions import ValidationError
import re

class Mahasiswa:
    STATUS_OPTIONS = ["Aktif", "Cuti", "Non Aktif"]
    PRODI_OPTIONS = ["Teknik Informatika", "Sistem Informasi", "Desain Komunikas Visual", "Manajemen", "Ilmu Hukum", "Teknik Sipil", "Arsitektur", "Matematika", "Biologi"] # Contoh
    JK_OPTIONS = ["Laki-laki", "Perempuan"]

    def __init__(self, nama: str, nim: str, jenis_kelamin: str, kelas: str, prodi: str, status: str):
        self.nama = nama
        self.set_nim(nim)
        self.set_jenis_kelamin(jenis_kelamin)
        self.kelas = kelas
        self.set_prodi(prodi)
        self.set_status(status)

    def get_nama(self):
        return self.nama

    def get_nim(self):
        return self.__nim

    def set_nim(self, nim: str):
        if not re.fullmatch(r'^\d{12}$', nim):
            raise ValidationError("NIM harus berupa 12 digit angka.")
        self.__nim = nim

    def get_jenis_kelamin(self):
        return self.__jenis_kelamin

    def set_jenis_kelamin(self, jenis_kelamin: str):
        if jenis_kelamin not in self.JK_OPTIONS:
            raise ValidationError(f"Jenis kelamin harus salah satu dari: {', '.join(self.JK_OPTIONS)}")
        self.__jenis_kelamin = jenis_kelamin

    def get_prodi(self):
        return self.__prodi

    def set_prodi(self, prodi: str):
        if prodi not in self.PRODI_OPTIONS:
            raise ValidationError(f"Prodi harus salah satu dari: {', '.join(self.PRODI_OPTIONS)}")
        self.__prodi = prodi

    def get_status(self):
        return self.__status

    def set_status(self, status: str):
        if status not in self.STATUS_OPTIONS:
            raise ValidationError(f"Status harus salah satu dari: {', '.join(self.STATUS_OPTIONS)}")
        self.__status = status

    def to_dict(self):
        return {
            "nama": self.nama,
            "nim": self.get_nim(),
            "jenis_kelamin": self.get_jenis_kelamin(),
            "kelas": self.kelas,
            "prodi": self.get_prodi(),
            "status": self.get_status()
        }