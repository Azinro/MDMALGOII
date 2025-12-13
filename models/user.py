import pandas as pd
from .exceptions import ValidationError

class User:
    def __init__(self, username: str, password: str, role: str = "user"):
        self.username = username
        self.password = password
        self.role = role  # "admin" atau "user"

    def verify_password(self, input_password: str) -> bool:
        return self.password == input_password

    @staticmethod
    def validate_login(username: str, password: str, users_csv_path: str):
        try:
            df = pd.read_csv(users_csv_path)
            user_row = df[df['username'] == username]
            if user_row.empty:
                raise ValidationError("Username tidak ditemukan.")
            stored_password = user_row.iloc[0]['password']
            role = user_row.iloc[0]['role']
            if stored_password != password:
                raise ValidationError("Password salah.")
            return User(username, password, role)
        except FileNotFoundError:
            raise ValidationError("File pengguna tidak ditemukan.")