import time
import os
from nicegui import ui,run
from models.user import User
from models.data_manager import DataManager
from models.mahasiswa import Mahasiswa
from models.exceptions import ValidationError, DataNotFound
from utils.email_sender import send_data_via_email
from utils.sorters import merge_sort, shell_sort
from utils.searchers import binary_search
from config import CSV_USERS, CSV_MAHASISWA

# --- State Aplikasi ---
class AppState:
    current_user = None

app_state = AppState()

# --- FUNGSI BACKGROUND (Baru) ---
def set_background():
    """Mengatur background image + overlay transparan untuk halaman"""
    # 1. Layer Gambar (Paling Belakang: z-20)
    # Ganti URL di bawah dengan path file lokal lu (misal: 'assets/bg.jpg') kalau mau
    url_gambar = 'static/bg.jpg'
    ui.image(url_gambar).classes('fixed inset-0 w-full h-full object-cover -z-20')
    
    # 2. Layer Overlay Hitam (Di atas gambar, di bawah konten: z-10)
    # bg-black/60 artinya warna hitam dengan opacity 60%. Bisa lu ganti /50 atau /70 sesuai selera.
    ui.element('div').classes('fixed inset-0 w-full h-full bg-black/60 -z-10')

# --- Halaman Login ---
@ui.page('/')
def login_page():
    set_background() # <--- Panggil fungsi background disini

    if app_state.current_user:
        ui.navigate.to('/dashboard')
        return

    # Sedikit styling transparan di card login biar nyatu sama background
    with ui.card().classes('w-96 mx-auto mt-20 bg-white/90 backdrop-blur-sm shadow-xl'):
        ui.label('Login').classes('text-2xl font-bold text-center w-full mb-4')
        username = ui.input('Username').props('dense outlined').classes('w-full')
        password = ui.input('Password', password=True).props('dense outlined').classes('w-full')
        
        def handle_login():
            try:
                user = User.validate_login(username.value, password.value, CSV_USERS)
                app_state.current_user = user
                ui.navigate.to('/dashboard')
            except Exception as e:
                ui.notify(f'Login gagal: {e}', type='negative')

        ui.button('Login', on_click=handle_login).classes('w-full bg-blue-600 text-white mt-4')

# --- Halaman Dashboard ---
@ui.page('/dashboard')
def dashboard_page():
    set_background() # Pastiin fungsi ini masih ada di atas ya

    if not app_state.current_user:
        ui.navigate.to('/')
        return

    # Header Atas
    with ui.header().classes('bg-blue-600/90 backdrop-blur-md text-white shadow-md'):
        ui.label(f'MANAJEMEN DATA MAHASISWA').classes('text-2xl font-bold')
        ui.space()
        ui.button('Logout', on_click=lambda: logout(), icon='logout').props('color=red-5 unelevated text-white rounded')

    # Statistik
    dm = DataManager(CSV_MAHASISWA)
    data = dm.load_data()
    total = len(data)
    aktif = len([m for m in data if m.get_status() == "Aktif"])
    cuti = len([m for m in data if m.get_status() == "Cuti"])
    non_aktif = len([m for m in data if m.get_status() == "Non Aktif"])

    with ui.grid(columns=4).classes('w-full gap-4 mb-6 mt-4'):
        with ui.card().classes('bg-blue-500/90 text-white p-4 rounded-lg text-center backdrop-blur-sm shadow-lg'):
            ui.label(f'TOTAL: {total}').classes('font-bold')
        with ui.card().classes('bg-green-500/90 text-white p-4 rounded-lg text-center backdrop-blur-sm shadow-lg'):
            ui.label(f'AKTIF: {aktif}').classes('font-bold')
        with ui.card().classes('bg-yellow-500/90 text-white p-4 rounded-lg text-center backdrop-blur-sm shadow-lg'):
            ui.label(f'CUTI: {cuti}').classes('font-bold')
        with ui.card().classes('bg-red-500/90 text-white p-4 rounded-lg text-center backdrop-blur-sm shadow-lg'):
            ui.label(f'NON-AKTIF: {non_aktif}').classes('font-bold')

    # --- BAR UTAMA ---
    # Container Biru Besar
    with ui.row().classes('w-full bg-[#0047AB]/90 backdrop-blur-md rounded-3xl p-5 justify-between items-start text-white shadow-xl border border-white/20'):
        
        # === BAGIAN KIRI (Search & Time) === TETAP (Gede & Jelas)
        with ui.column().classes('gap-1'):
            with ui.row().classes('items-center gap-4 h-12'):
                ui.label('Cari berdasarkan').classes('font-bold text-lg')
                search_column = ui.select(['Nama', 'NIM'], value='Nama').classes('bg-white text-black rounded w-28 no-shadow text-base').props('outlined dense options-dense behavior="menu"')
                search_query_state = ui.input(placeholder='Keyword...').classes('w-72').props('dark dense outlined bg-color="blue-10" borderless input-class="text-base" append-icon="search"')

            with ui.row().classes('items-center gap-2 pl-1'):
                ui.label('Time :').classes('font-bold text-sm')
                time_display = ui.label('0.00 ms').classes('font-bold text-sm text-yellow-300')

        # === BAGIAN TENGAH (Sort) === TETAP (Gede & Jelas)
        with ui.row().classes('items-center gap-4 h-12'): 
            ui.label('Urut berdasarkan').classes('font-bold text-lg')
            sort_by_state = ui.select([
                'Nama', 'NIM', 'Jenis Kelamin', 'Kelas', 'Prodi', 'Status'
            ], value='Nama').classes('bg-white text-black rounded w-40 no-shadow text-base').props('outlined dense options-dense behavior="menu"')

        # === BAGIAN KANAN (Buttons) === 
        # Gap-2 biar jarak atas-bawah rapet
        with ui.column().classes('gap-2 pt-1'): 
            # Tombol Email
            if app_state.current_user.role == 'admin':
                # FIX 1: Ganti w-64 jadi w-72 biar lebih lebar dikit
                ui.button('Send to Email', on_click=lambda: ui.navigate.to('/email')).props('color=deep-purple-7 unelevated').classes('w-72 rounded-full font-bold shadow-lg')
            
            # Tombol Action
            # FIX 2: Ganti w-64 jadi w-72 juga, biar sejajar sama tombol email
            with ui.row().classes('w-72 justify-between'):
                # Padding px-4 (dikecilin dikit dari 5 biar DELETE gak sesak)
                if app_state.current_user.role == 'admin':
                ui.button('ADD', on_click=lambda: ui.navigate.to('/add')).props('color=positive unelevated').classes('rounded-full font-bold px-4 text-sm shadow-lg')
                ui.button('EDIT', on_click=lambda: ui.navigate.to('/edit_delete')).props('color=warning unelevated').classes('rounded-full font-bold px-4 text-white text-sm shadow-lg')
                ui.button('DELETE', on_click=lambda: ui.navigate.to('/edit_delete')).props('color=negative unelevated').classes('rounded-full font-bold px-4 text-sm shadow-lg')

    # --- Tabel Data ---
    table_card = ui.card().classes('w-full mt-6 bg-white/95 backdrop-blur-sm p-0 rounded-lg shadow-2xl')
    
    table_container = ui.column().classes('w-full')

    def update_table():
        table_container.clear()
        with table_card: 
             with table_container:
                # Load data fresh
                current_data = dm.load_data()
                
                # Filter
                filtered_data = current_data
                if search_query_state.value and search_query_state.value.strip():
                    query = search_query_state.value.strip().lower()
                    if search_column.value == 'Nama':
                        filtered_data = [m for m in current_data if query in m.get_nama().lower()]
                    elif search_column.value == 'NIM':
                        filtered_data = [m for m in current_data if query in m.get_nim().lower()]

                # Sorting
                sort_key = sort_by_state.value
                start_time = time.time()

                if sort_key == 'Nama':
                    sorted_data = merge_sort(filtered_data, key_func=lambda m: m.get_nama().lower())
                elif sort_key == 'NIM':
                    sorted_data = merge_sort(filtered_data, key_func=lambda m: m.get_nim().lower())
                elif sort_key == 'Kelas':
                    sorted_data = merge_sort(filtered_data, key_func=lambda m: m.kelas.lower())
                elif sort_key == 'Jenis Kelamin':
                    sorted_data = shell_sort([m for m in filtered_data], key_func=lambda m: m.get_jenis_kelamin().lower())
                elif sort_key == 'Prodi':
                    sorted_data = shell_sort([m for m in filtered_data], key_func=lambda m: m.get_prodi().lower())
                elif sort_key == 'Status':
                    sorted_data = shell_sort([m for m in filtered_data], key_func=lambda m: m.get_status().lower())
                else:
                    sorted_data = filtered_data

                end_time = time.time()
                time_taken = (end_time - start_time) * 1000  # ms

                time_display.text = f"{time_taken:.2f} ms"

                if sorted_data:
                    rows = []
                    for i, m in enumerate(sorted_data, 1):
                        row = m.to_dict()
                        row['no'] = i
                        rows.append(row)

                    columns = [
                        {'name': 'no', 'label': 'NO', 'field': 'no', 'align': 'center'},
                        {'name': 'nama', 'label': 'NAMA', 'field': 'nama', 'align': 'center', 'classes': 'text-left', 'headerClasses': 'font-bold text-center'},
                        {'name': 'nim', 'label': 'NIM', 'field': 'nim', 'align': 'center'},
                        {'name': 'jenis_kelamin', 'label': 'JENIS KELAMIN', 'field': 'jenis_kelamin', 'align': 'center'},
                        {'name': 'kelas', 'label': 'KELAS', 'field': 'kelas', 'align': 'center'},
                        {'name': 'prodi', 'label': 'PROGRAM STUDI', 'field': 'prodi', 'align': 'center'},
                        {'name': 'status', 'label': 'STATUS', 'field': 'status', 'align': 'center'},
                    ]
                    # Tabel styling
                    ui.table(columns=columns, rows=rows).classes('w-full header-blue')
                else:
                    ui.label('Tidak ada data yang sesuai dengan pencarian.').classes('text-gray-500 m-4 text-center w-full')

    # Trigger update
    search_query_state.on_value_change(lambda e: update_table())
    search_column.on_value_change(lambda e: update_table())
    sort_by_state.on_value_change(lambda e: update_table())
    
    update_table()

def logout():
    app_state.current_user = None
    ui.navigate.to('/')


# --- Halaman Tambah Mahasiswa ---
@ui.page('/add')
def add_page():
    if not app_state.current_user or app_state.current_user.role != 'admin': # Tambahkan pengecekan
        ui.notify('Akses ditolak. Hanya admin yang bisa menambah data.', type='negative')
        ui.navigate.to('/dashboard') # Alihkan ke dashboard
        return

    set_background() # Panggil background biar konsisten

    if not app_state.current_user:
        ui.navigate.to('/')
        return

    with ui.header().classes('bg-blue-600/90 backdrop-blur-md text-white shadow-md'):
        ui.label('Tambah Mahasiswa Baru').classes('text-2xl font-bold')
        ui.space()
        ui.button('Logout', on_click=lambda: logout(), icon='logout').props('color=red-5 unelevated text-white')

    # Container Form
    with ui.card().classes('w-full max-w-2xl mx-auto mt-20 bg-white/95 backdrop-blur-sm p-6 shadow-xl'):
        ui.label('Form Tambah Data').classes('text-xl font-bold mb-4')

        # Input Field
        nama = ui.input('Nama Lengkap').classes('w-full')
        nim = ui.input('NIM').classes('w-full')
        jenis_kelamin = ui.select(Mahasiswa.JK_OPTIONS, label='Jenis Kelamin').classes('w-full')
        kelas = ui.input('Kelas').classes('w-full')
        prodi = ui.select(Mahasiswa.PRODI_OPTIONS, label='Prodi').classes('w-full')
        status = ui.select(Mahasiswa.STATUS_OPTIONS, label='Status').classes('w-full')

        def save():
            # Validasi Input Kosong
            if not nama.value or not nim.value or not jenis_kelamin.value or not kelas.value or not prodi.value or not status.value:
                ui.notify('Harap isi semua field!', type='warning')
                return

            try:
                dm = DataManager(CSV_MAHASISWA)
                
                # Cek apakah NIM sudah ada (biar gak duplikat)
                existing_data = dm.load_data()
                if any(m.get_nim() == nim.value for m in existing_data):
                    ui.notify(f'NIM {nim.value} sudah terdaftar!', type='negative')
                    return

                # Buat Object Mahasiswa Baru
                new_mhs = Mahasiswa(
                    nama=nama.value,
                    nim=nim.value,
                    jenis_kelamin=jenis_kelamin.value,
                    kelas=kelas.value,
                    prodi=prodi.value,
                    status=status.value
                )
                
                # Simpan ke CSV
                # NOTE: Pastikan di data_manager.py lu ada method 'add_mahasiswa'
                # Kalau error, coba ganti jadi logic append manual
                dm.add_mahasiswa(new_mhs) 
                
                ui.notify('Data berhasil ditambahkan!', type='positive')
                ui.navigate.to('/dashboard')

            except Exception as e:
                ui.notify(f'Gagal menyimpan: {e}', type='negative')

        # Tombol Aksi
        with ui.row().classes('w-full justify-between mt-6'):
            ui.button('Simpan', on_click=save).classes('bg-green-600 text-white shadow-md')
            ui.button('Kembali', on_click=lambda: ui.navigate.to('/dashboard')).props('outline')


# --- Halaman Edit/Hapus Mahasiswa ---
@ui.page('/edit_delete')
def edit_delete_page():
    if not app_state.current_user or app_state.current_user.role != 'admin': # Tambahkan pengecekan
        ui.notify('Akses ditolak. Hanya admin yang bisa mengedit atau menghapus data.', type='negative')
        ui.navigate.to('/dashboard') # Alihkan ke dashboard
        return
    
    set_background() # <--- Panggil fungsi background disini

    if not app_state.current_user:
        ui.navigate.to('/')
        return

    with ui.header().classes('bg-blue-600/90 backdrop-blur-md text-white shadow-md'):
        ui.label('Edit atau Hapus Mahasiswa').classes('text-2xl font-bold')
        ui.space()
        ui.button('Logout', on_click=lambda: logout()).props('flat text-white')

    dm = DataManager(CSV_MAHASISWA)
    data = dm.load_data()

    # Container Utama (Card Putih Transparan)
    with ui.card().classes('w-full max-w-4xl mx-auto mt-4 bg-white/95 backdrop-blur-sm p-6 shadow-xl'):
        
        if not data:
            ui.label('Tidak ada data untuk diedit atau dihapus.').classes('text-lg')
            ui.button('Kembali', on_click=lambda: ui.navigate.to('/dashboard')).classes('mt-4')
            return

        df = [m.to_dict() for m in data]
        selected_nim = ui.select(options=[row['nim'] for row in df], label='Pilih NIM Mahasiswa').classes('w-full')

        # Container untuk form input
        form_container = ui.column().classes('hidden w-full gap-4 mt-4')

        with form_container:
            nama = ui.input('Nama Lengkap').classes('w-full')
            jenis_kelamin = ui.select(Mahasiswa.JK_OPTIONS, label='Jenis Kelamin').classes('w-full')
            kelas = ui.input('Kelas').classes('w-full')
            prodi = ui.select(Mahasiswa.PRODI_OPTIONS, label='Prodi').classes('w-full')
            status = ui.select(Mahasiswa.STATUS_OPTIONS, label='Status').classes('w-full')

        def load_data_for_edit():
            if selected_nim.value:
                current_data = dm.load_data()
                mhs = next((m for m in current_data if m.get_nim() == selected_nim.value), None)
                if mhs:
                    nama.value = mhs.nama
                    jenis_kelamin.value = mhs.get_jenis_kelamin()
                    kelas.value = mhs.kelas
                    prodi.value = mhs.get_prodi()
                    status.value = mhs.get_status()
                    form_container.classes(remove='hidden')
                else:
                    form_container.classes(add='hidden')
            else:
                form_container.classes(add='hidden')

        selected_nim.on_value_change(load_data_for_edit)

        def update():
            if not selected_nim.value:
                ui.notify('Pilih mahasiswa terlebih dahulu', type='warning')
                return
            if not nama.value or not jenis_kelamin.value or not kelas.value or not prodi.value or not status.value:
                ui.notify('Isi semua field terlebih dahulu', type='warning')
                return
            try:
                mhs_baru = Mahasiswa(
                    nama=nama.value,
                    nim=selected_nim.value,
                    jenis_kelamin=jenis_kelamin.value,
                    kelas=kelas.value,
                    prodi=prodi.value,
                    status=status.value
                )
                dm.update_mahasiswa(selected_nim.value, mhs_baru)
                ui.notify('Data berhasil diperbarui!', type='positive')
                ui.navigate.to('/dashboard')
            except ValidationError as e:
                ui.notify(f'Gagal memperbarui: {e}', type='negative')

        def delete():
            if not selected_nim.value:
                ui.notify('Pilih mahasiswa terlebih dahulu', type='warning')
                return
            try:
                dm.delete_mahasiswa(selected_nim.value)
                ui.notify('Data berhasil dihapus!', type='positive')
                ui.navigate.to('/dashboard')
            except DataNotFound as e:
                ui.notify(f'Gagal menghapus data: {e}', type='negative')

        with ui.row().classes('w-full justify-between mt-6'):
            ui.button('Update', on_click=update).classes('bg-blue-600 text-white shadow-md')
            ui.button('Hapus', on_click=delete).classes('bg-red-600 text-white shadow-md')
            ui.button('Kembali', on_click=lambda: ui.navigate.to('/dashboard')).props('outline')

# --- Halaman Kirim Email ---
@ui.page('/email')
def email_page():
    set_background() # <--- Panggil fungsi background disini

    if not app_state.current_user or app_state.current_user.role != 'admin':
        ui.navigate.to('/')
        return

    with ui.header().classes('bg-blue-600/90 backdrop-blur-md text-white shadow-md'):
        ui.label('Kirim Data Mahasiswa via Email').classes('text-2xl font-bold')
        ui.space()
        ui.button('Logout', on_click=lambda: logout()).props('flat text-white')

    with ui.card().classes('w-full max-w-2xl mx-auto mt-20 bg-white/95 backdrop-blur-sm p-6 shadow-xl'):
        ui.label('Form Email').classes('text-xl font-bold mb-4')
        email_penerima = ui.input('Alamat Email Penerima').classes('w-full')

        # --- KODE BARU (ASYNCHRONOUS) ---
        async def send_email():  # 1. Tambah 'async' di depan def
            if not email_penerima.value:
                ui.notify('Silakan masukkan alamat email penerima.', type='negative')
                return
            
            # Kasih notifikasi biar user tau lagi proses
            ui.notify('Sedang mengirim email... Mohon tunggu.', type='info', spinner=True)
            
            try:
                # 2. Pindahkan proses berat ke background thread pakai run.io_bound
                # Ini kuncinya biar "Connection Lost" hilang
                await run.io_bound(send_data_via_email, email_penerima.value, CSV_MAHASISWA)
                
                ui.notify('Email berhasil dikirim!', type='positive')
                ui.navigate.to('/dashboard')
            except Exception as e:
                ui.notify(f'Gagal mengirim email: {e}', type='negative')

        with ui.row().classes('w-full justify-between mt-6'):
            ui.button('Kirim Email', on_click=send_email).classes('bg-green-600 text-white shadow-md')
            ui.button('Kembali', on_click=lambda: ui.navigate.to('/dashboard')).props('outline')

# --- Jalankan Aplikasi ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host='0.0.0.0', # Harus 0.0.0.0 biar bisa diakses publik
        port=int(os.environ.get('PORT', 8080)), # Ambil PORT dari Railway
        title='Aplikasi Keren Zetka',
        favicon='🚀'
    )