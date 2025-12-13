class ValidationError(Exception):
    """Dipicu saat input tidak valid"""
    pass

class DataNotFound(Exception):
    """Dipicu saat data tidak ditemukan"""
    pass

class NIMInvalidError(ValidationError):
    """Dipicu saat format NIM salah"""
    pass