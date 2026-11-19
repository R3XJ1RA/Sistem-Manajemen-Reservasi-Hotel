import json
import os
from datetime import datetime, date

# ==============================================================================
# 1. KONFIGURASI DAN PENYIMPANAN DATABASE JSON
# ==============================================================================

FILE_KAMAR = "data_kamar.json"
FILE_RESERVASI = "data_reservasi.json"
FILE_TAMU = "data_tamu.json"

REFERENSI_TIPE = {
    "1": {"jenis": "Standard", "harga": 250000},
    "2": {"jenis": "Deluxe", "harga": 400000},
    "3": {"jenis": "Suite", "harga": 650000}
}


# Tugas: Menyimpan data list/dict ke dalam file JSON
def simpan_json(nama_file, data):
    try:
        with open(nama_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"Gagal menyimpan data ke {nama_file}: {error}")


# Tugas: Membaca data dari file JSON
def muat_json(nama_file):
    if not os.path.exists(nama_file):
        return []
    try:
        with open(nama_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


# Tugas: Memuat data kamar atau membuat data awal kamar & tamu jika file belum ada
def muat_atau_buat_kamar():
    if os.path.exists(FILE_KAMAR):
        try:
            with open(FILE_KAMAR, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except (json.JSONDecodeError, OSError):
            pass

    try:
        jumlah_total = int(input("Masukkan jumlah total kamar hotel yang ingin dibuat: "))
        if jumlah_total <= 0:
            raise ValueError
    except ValueError:
        jumlah_total = 15
        print(f"Input tidak valid, otomatis menggunakan {jumlah_total} kamar.")

    kamar_awal = []
    tamu_awal = []

    for i in range(1, jumlah_total + 1):
        nomor_kamar = str(100 + i)
        id_tamu = f"{i:03d}"

        kamar_awal.append({
            "nomor": nomor_kamar,
            "jenis": "Belum diatur",
            "harga": 0,
            "status": "Tersedia",
            "status_reservasi": "Not Booked"
        })

        tamu_awal.append({
            "id": id_tamu,
            "nama": f"Tamu {nomor_kamar}",
            "telepon": "-",
            "nomor_kamar": nomor_kamar
        })

    simpan_json(FILE_KAMAR, kamar_awal)
    simpan_json(FILE_TAMU, tamu_awal)

    if not os.path.exists(FILE_RESERVASI):
        simpan_json(FILE_RESERVASI, [])

    return kamar_awal


DATA_KAMAR = muat_atau_buat_kamar()


# ==============================================================================
# 2. FUNGSI BANTU, VALIDASI INPUT, & GENERATOR ID
# ==============================================================================

# Tugas: Mengecek apakah sudah ada kamar berstatus 'Full' untuk membuka akses Menu 4
def cek_kamar_sudah_full():
    for kamar in DATA_KAMAR:
        if kamar.get("status") == "Full" or kamar.get("status_reservasi") == "Booked":
            return True
    return False


# Tugas: Memastikan input teks dari pengguna tidak kosong
def input_tidak_kosong(pesan):
    while True:
        nilai = input(pesan).strip()
        if nilai:
            return nilai
        print("Input tidak boleh kosong!")


# Tugas: Memvalidasi input tanggal sesuai format DD-MM-YYYY
def input_tanggal(pesan):
    while True:
        teks = input(pesan).strip()
        try:
            return datetime.strptime(teks, "%d-%m-%Y").date()
        except ValueError:
            print("Format tanggal salah. Gunakan DD-MM-YYYY, contoh 20-12-2026.")


# Tugas: Memastikan input angka bernilai lebih dari 0
def input_angka_positif(pesan):
    while True:
        try:
            angka = int(input(pesan))
            if angka > 0:
                return angka
            print("Masukkan angka lebih dari 0.")
        except ValueError:
            print("Input harus berupa angka bulat!")


# Tugas: Mengubah angka menjadi format mata uang Rupiah (contoh: Rp250.000)
def format_rupiah(nilai):
    return "Rp" + f"{nilai:,}".replace(",", ".")


# Tugas: Mencari data kamar berdasarkan nomor kamar
def cari_kamar(nomor_kamar):
    for kamar in DATA_KAMAR:
        if kamar.get("nomor") == nomor_kamar:
            return kamar
    return None


# Tugas: Mengecek agar jadwal reservasi kamar tidak bentrok dengan reservasi lain
def tanggal_tidak_bentrok(nomor_kamar, check_in, check_out, data_reservasi, id_dikecualikan=None):
    for reservasi in data_reservasi:
        if reservasi.get("id") == id_dikecualikan:
            continue
        if reservasi.get("nomor_kamar") != nomor_kamar:
            continue

        try:
            mulai_lama = datetime.strptime(reservasi.get("check_in", reservasi.get("tanggal", "2026-01-01")), "%Y-%m-%d").date()
            selesai_lama = datetime.strptime(reservasi.get("check_out", reservasi.get("tanggal", "2026-01-01")), "%Y-%m-%d").date()
        except ValueError:
            continue

        if check_in < selesai_lama and check_out > mulai_lama:
            return False
    return True


# Tugas: Memvalidasi tanggal check-in dan check-out (tidak boleh tanggal lampau)
def validasi_periode():
    while True:
        check_in = input_tanggal("Tanggal check-in  (DD-MM-YYYY): ")
        check_out = input_tanggal("Tanggal check-out (DD-MM-YYYY): ")

        if check_in < date.today():
            print("Check-in tidak boleh sebelum tanggal hari ini.")
        elif check_out <= check_in:
            print("Check-out harus setelah tanggal check-in.")
        else:
            return check_in, check_out


# Tugas: Membuat ID reservasi otomatis (RES-001, RES-002, dst.)
def buat_id_reservasi(data_reservasi):
    nomor_terbesar = 0
    for reservasi in data_reservasi:
        try:
            rid = str(reservasi["id"])
            if rid.startswith("RES-"):
                nomor = int(rid.replace("RES-", ""))
            else:
                nomor = int(rid)
            nomor_terbesar = max(nomor_terbesar, nomor)
        except (ValueError, KeyError):
            continue
    return f"RES-{nomor_terbesar + 1:03d}"


# Tugas: Membuat ID tamu otomatis (001, 002, dst.)
def buat_id_tamu(tamu_list):
    nomor_terbesar = 0
    for data in tamu_list:
        try:
            nomor = int(data["id"])
            nomor_terbesar = max(nomor_terbesar, nomor)
        except (ValueError, KeyError):
            continue
    return f"{nomor_terbesar + 1:03d}"


# ==============================================================================
# 3. FITUR MENU 1, 2, & 3: MANAJEMEN DATA KAMAR
# ==============================================================================

# [MENU 1] Menampilkan Data Kamar
def tampilkan_kamar():
    print("\n" + "=" * 95)
    print("                                DAFTAR KAMAR HOTEL")
    print("=" * 95)
    print(f"{'Nomor':<10}{'Jenis Kamar':<18}{'Harga per Malam':<20}{'Status':<15}{'Reservasi':<15}")
    print("-" * 95)

    for kamar in DATA_KAMAR:
        harga = kamar.get('harga', 0)
        harga_str = format_rupiah(harga) if harga > 0 else "-"
        status_res = kamar.get('status_reservasi', 'Not Booked')
        print(
            f"{kamar.get('nomor', '-'):<10}"
            f"{kamar.get('jenis', 'Belum diatur'):<18}"
            f"{harga_str:<20}"
            f"{kamar.get('status', 'Tersedia'):<15}"
            f"{status_res:<15}"
        )
    print("=" * 95)


# [MENU 2] Atur Tipe dan Harga Kamar (Standard / Deluxe / Suite)
def atur_tipe_dan_harga():
    tampilkan_kamar()
    nomor_input = input_tidak_kosong("\nMasukkan nomor kamar yang ingin diatur: ")
    kamar = cari_kamar(nomor_input)

    if kamar is None:
        print("Nomor kamar tidak ditemukan.")
        return

    print("\nPilih Tipe Kamar:")
    print("1. Standard (Rp 250.000)")
    print("2. Deluxe (Rp 400.000)")
    print("3. Suite (Rp 650.000)")

    pilihan = input_tidak_kosong("Masukkan pilihan tipe (1/2/3): ").strip()

    if pilihan in REFERENSI_TIPE:
        data_pilihan = REFERENSI_TIPE[pilihan]
        kamar["jenis"] = data_pilihan["jenis"]
        kamar["harga"] = data_pilihan["harga"]
        simpan_json(FILE_KAMAR, DATA_KAMAR)
        print(f"Kamar {kamar['nomor']} berhasil diatur ke tipe {kamar['jenis']} dengan harga {format_rupiah(kamar['harga'])}!")
    else:
        print("Pilihan tidak valid! Masukkan angka 1, 2, atau 3.")


# [MENU 3] Ubah Status Kamar (Full / Tersedia)
def ubah_status_kamar():
    tampilkan_kamar()
    nomor_input = input_tidak_kosong("\nMasukkan nomor kamar yang ingin diubah statusnya: ")
    kamar = cari_kamar(nomor_input)

    if kamar is None:
        print("Nomor kamar tidak ditemukan.")
        return

    print(f"Status saat ini untuk kamar {kamar['nomor']}: {kamar['status']}")
    status_baru = input_tidak_kosong("Masukkan status baru (ketik 'Full' atau 'Tersedia'): ").capitalize()

    if status_baru in ["Full", "Tersedia"]:
        kamar["status"] = status_baru
        kamar["status_reservasi"] = "Booked" if status_baru == "Full" else "Not Booked"
        simpan_json(FILE_KAMAR, DATA_KAMAR)
        print(f"Status kamar {kamar['nomor']} berhasil diubah menjadi {status_baru}!")
    else:
        print("Status tidak valid! Gunakan 'Full' atau 'Tersedia'.")


# ==============================================================================
# 4. FITUR MENU 4: MANAJEMEN DATA TAMU (CRUD TAMU)
# ==============================================================================

# [SUB-MENU 4.2] Menampilkan seluruh daftar tamu dari file JSON
def tampilkan_tamu():
    tamu = muat_json(FILE_TAMU)
    print("\n--- DAFTAR TAMU HOTEL ---")
    if not tamu:
        print("Belum ada data tamu.")
        return

    print(f"{'ID':<8} {'NAMA TAMU':<20} {'NO. TELEPON':<18} {'NOMOR KAMAR':<15}")
    print("-" * 65)

    for data in tamu:
        nomor_kamar = data.get("nomor_kamar", "-")
        print(f"{data['id']:<8} {data['nama']:<20} {data['telepon']:<18} {nomor_kamar:<15}")


# [SUB-MENU 4.1] Menambahkan data tamu baru secara manual
def tambah_tamu():
    tamu = muat_json(FILE_TAMU)
    print("\n--- TAMBAH TAMU ---")

    id_tamu = buat_id_tamu(tamu)
    print(f"ID Tamu yang digenerate otomatis: {id_tamu}")

    nama = input_tidak_kosong("Masukkan nama tamu: ")
    telepon = input_tidak_kosong("Masukkan nomor telepon: ")
    nomor_kamar = input_tidak_kosong("Masukkan nomor kamar (misal: 101): ")

    tamu.append({"id": id_tamu, "nama": nama, "telepon": telepon, "nomor_kamar": nomor_kamar})
    simpan_json(FILE_TAMU, tamu)
    print(f"Data tamu berhasil ditambahkan dengan ID {id_tamu}.")


# [SUB-MENU 4.3] Mengubah data tamu berdasarkan ID tamu
def ubah_tamu():
    tamu = muat_json(FILE_TAMU)
    print("\n--- UBAH DATA TAMU ---")
    id_tamu = input_tidak_kosong("Masukkan ID tamu yang akan diubah (misal: 001): ")
    for data in tamu:
        if data["id"] == id_tamu:
            print("Kosongkan input jika data tidak ingin diubah.")
            nama = input(f"Nama baru [{data['nama']}]: ").strip()
            telepon = input(f"Nomor telepon baru [{data['telepon']}]: ").strip()
            nomor_kamar = input(f"Nomor kamar baru [{data.get('nomor_kamar', '-')}]: ").strip()

            if nama:
                data["nama"] = nama
            if telepon:
                data["telepon"] = telepon
            if nomor_kamar:
                data["nomor_kamar"] = nomor_kamar

            simpan_json(FILE_TAMU, tamu)
            print("Data tamu berhasil diperbarui.")
            return
    print("ID tamu tidak ditemukan.")


# [SUB-MENU 4.4] Menghapus data tamu berdasarkan ID tamu
def hapus_tamu():
    tamu = muat_json(FILE_TAMU)
    print("\n--- HAPUS DATA TAMU ---")
    id_tamu = input_tidak_kosong("Masukkan ID tamu yang akan dihapus (misal: 001): ")
    for data in tamu:
        if data["id"] == id_tamu:
            konfirmasi = input(f"Yakin ingin menghapus data {data['nama']}? (y/n): ").strip().lower()
            if konfirmasi == "y":
                tamu.remove(data)
                simpan_json(FILE_TAMU, tamu)
                print("Data tamu berhasil dihapus.")
            else:
                print("Penghapusan dibatalkan.")
            return
    print("ID tamu tidak ditemukan.")


# [MENU 4] Manajemen Data Tamu (Hanya terbuka jika minimal 1 kamar berstatus Full)
def menu_tamu():
    if not cek_kamar_sudah_full():
        print("\n[AKSES DITOLAK] Kamar masih kosong / belum ada yang berstatus Full!")
        print("Manajemen Data Tamu baru bisa diakses jika sudah ada kamar yang terisi atau berstatus 'Full'.")
        return

    while True:
        print("\n=== MENU MANAJEMEN TAMU ===")
        print("1. Tambah data tamu")
        print("2. Tampilkan data tamu")
        print("3. Ubah data tamu")
        print("4. Hapus data tamu")
        print("0. Kembali ke Menu Utama")
        pilihan = input("Pilih menu (0-4): ").strip()

        if pilihan == "1":
            tambah_tamu()
        elif pilihan == "2":
            tampilkan_tamu()
        elif pilihan == "3":
            ubah_tamu()
        elif pilihan == "4":
            hapus_tamu()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


# ==============================================================================
# 5. FITUR MENU 5, 6, 7, 8, & 9: PENGELOLAAN RESERVASI HOTEL
# ==============================================================================

# Tugas: Sinkronisasi otomatis data tamu saat reservasi baru dibuat pada Menu 6
def perbarui_tamu_otomatis(nama_tamu_baru, nomor_kamar_baru, telepon_tamu="123456789"):
    tamu = muat_json(FILE_TAMU)
    ditemukan = False
    for data in tamu:
        if data.get("nomor_kamar") == nomor_kamar_baru:
            data["nama"] = nama_tamu_baru
            if telepon_tamu != "123456789":
                data["telepon"] = telepon_tamu
            ditemukan = True
            break

    if not ditemukan:
        id_tamu = buat_id_tamu(tamu)
        tamu.append({"id": id_tamu, "nama": nama_tamu_baru, "telepon": telepon_tamu, "nomor_kamar": nomor_kamar_baru})

    simpan_json(FILE_TAMU, tamu)


# [MENU 5] Menampilkan Seluruh Reservasi
def tampilkan_reservasi():
    reservasi = muat_json(FILE_RESERVASI)
    print("\n===== DAFTAR SELURUH RESERVASI =====")

    if len(reservasi) == 0:
        print("Belum ada data reservasi.")
        return

    for r in reservasi:
        print("--------------------------------")
        print("ID Reservasi :", r["id"])
        print("Nama Tamu    :", r.get("nama_tamu", r.get("nama", "-")))
        print("Nama Pemesan :", r.get("nama", "-"))
        print("Tipe Kamar   :", r.get("kamar", r.get("jenis_kamar", "-")))
        print("Nomor Kamar  :", r.get("nomor_kamar", "-"))
        print("Tanggal      :", r.get("tanggal", r.get("check_in", "-")))
        print("Jumlah Tamu  :", r["jumlah_tamu"])
        print("Status       :", r["status"])


# [MENU 6] Tambah Reservasi Kamar Baru (Hitung biaya, simpan reservasi, & kunci kamar jadi Full)
def tambah_reservasi(data_reservasi):
    print("\n========== TAMBAH RESERVASI ==========")
    tampilkan_kamar()

    nomor_kamar = input_tidak_kosong("Pilih nomor kamar: ")
    kamar = cari_kamar(nomor_kamar)

    if kamar is None:
        print("Nomor kamar tidak ditemukan.")
        return

    if kamar["jenis"] == "Belum diatur":
        print("Kamar ini belum diatur tipe dan harganya. Atur melalui menu pengaturan kamar terlebih dahulu.")
        return

    if kamar["status"] == "Full" or kamar.get("status_reservasi") == "Booked":
        print("Maaf, kamar tersebut sudah di-reservasi (Booked/Full).")
        return

    check_in, check_out = validasi_periode()

    if not tanggal_tidak_bentrok(nomor_kamar, check_in, check_out, data_reservasi):
        print("Maaf, kamar tidak tersedia pada tanggal tersebut.")
        return

    nama_pemesan = input_tidak_kosong("Nama pemesan: ")
    nama_tamu = input_tidak_kosong("Data Nama Tamu/Kamar: ")
    telepon_tamu = input_tidak_kosong("Nomor Telepon Tamu: ")
    jumlah_tamu = input_angka_positif("Jumlah tamu: ")

    jumlah_malam = (check_out - check_in).days
    total_biaya = jumlah_malam * kamar["harga"]

    reservasi_baru = {
        "id": buat_id_reservasi(data_reservasi),
        "nama": nama_pemesan,
        "nama_tamu": nama_tamu,
        "kamar": kamar["jenis"],
        "jenis_kamar": kamar["jenis"],
        "jumlah_tamu": jumlah_tamu,
        "nomor_kamar": nomor_kamar,
        "tanggal": check_in.strftime("%d-%m-%Y"),
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "jumlah_malam": jumlah_malam,
        "harga_per_malam": kamar["harga"],
        "total_biaya": total_biaya,
        "status": "Menunggu"
    }

    data_reservasi.append(reservasi_baru)
    simpan_json(FILE_RESERVASI, data_reservasi)

    perbarui_tamu_otomatis(nama_tamu, nomor_kamar, telepon_tamu)

    kamar["status"] = "Full"
    kamar["status_reservasi"] = "Booked"
    simpan_json(FILE_KAMAR, DATA_KAMAR)

    print("\nReservasi berhasil disimpan & status kamar otomatis menjadi FULL (Booked)!")
    detail_reservasi_by_object(reservasi_baru)


# [MENU 7] Mengubah Status Reservasi (Menunggu / Dikonfirmasi / Selesai / Dibatalkan)
def ubah_status():
    reservasi = muat_json(FILE_RESERVASI)
    tampilkan_reservasi()

    if len(reservasi) == 0:
        return

    id_input = input("\nMasukkan ID reservasi (misal: RES-001): ").strip()

    target_r = None
    for r in reservasi:
        if str(r["id"]).lower() == id_input.lower():
            target_r = r
            break

    if target_r:
        print("\nPilih Status Baru:")
        print("1. Menunggu")
        print("2. Dikonfirmasi")
        print("3. Selesai")
        print("4. Dibatalkan")

        pilihan = input("Masukkan pilihan: ")

        status_map = {
            "1": "Menunggu",
            "2": "Dikonfirmasi",
            "3": "Selesai",
            "4": "Dibatalkan"
        }

        if pilihan in status_map:
            old_status = target_r["status"]
            new_status = status_map[pilihan]
            target_r["status"] = new_status

            if new_status in ["Selesai", "Dibatalkan"] and old_status not in ["Selesai", "Dibatalkan"]:
                kamar = cari_kamar(target_r["nomor_kamar"])
                if kamar:
                    kamar["status"] = "Tersedia"
                    kamar["status_reservasi"] = "Not Booked"
                    simpan_json(FILE_KAMAR, DATA_KAMAR)
            elif new_status in ["Menunggu", "Dikonfirmasi"] and old_status in ["Selesai", "Dibatalkan"]:
                kamar = cari_kamar(target_r["nomor_kamar"])
                if kamar:
                    kamar["status"] = "Full"
                    kamar["status_reservasi"] = "Booked"
                    simpan_json(FILE_KAMAR, DATA_KAMAR)

            simpan_json(FILE_RESERVASI, reservasi)
            print("Status reservasi berhasil diubah!")
        else:
            print("Pilihan status tidak valid.")
        return

    print("Reservasi tidak ditemukan!")


# [MENU 8] Membatalkan Reservasi & Mengembalikan Status Kamar Menjadi Tersedia
def batalkan_reservasi():
    reservasi = muat_json(FILE_RESERVASI)
    tampilkan_reservasi()

    if len(reservasi) == 0:
        return

    id_input = input("\nMasukkan ID reservasi yang dibatalkan (misal: RES-001): ").strip()

    target_r = None
    for r in reservasi:
        if str(r["id"]).lower() == id_input.lower():
            target_r = r
            break

    if target_r:
        konfirmasi = input("Yakin ingin membatalkan reservasi? (y/n): ")

        if konfirmasi.lower() == "y":
            target_r["status"] = "Dibatalkan"

            kamar = cari_kamar(target_r["nomor_kamar"])
            if kamar:
                kamar["status"] = "Tersedia"
                kamar["status_reservasi"] = "Not Booked"
                simpan_json(FILE_KAMAR, DATA_KAMAR)

            simpan_json(FILE_RESERVASI, reservasi)
            print("Reservasi berhasil dibatalkan!")
        else:
            print("Pembatalan tidak dilakukan.")
        return

    print("Reservasi tidak ditemukan!")


# Tugas: Mencetak rincian lengkap satu objek reservasi beserta total biayanya
def detail_reservasi_by_object(r):
    print("\n===== DETAIL RESERVASI TAMU =====")
    print("ID Reservasi    :", r["id"])
    print("Nama Pemesan    :", r.get("nama", "-"))
    print("Nama Tamu/Kamar :", r.get("nama_tamu", "-"))
    print("Tipe Kamar      :", r.get("kamar", r.get("jenis_kamar", "-")))
    print("Nomor Kamar     :", r.get("nomor_kamar", "-"))
    print("Tanggal         :", r.get("tanggal", r.get("check_in", "-")))
    print("Jumlah Tamu     :", r["jumlah_tamu"])
    print("Status          :", r["status"])
    if "total_biaya" in r:
        print("Total Biaya     :", format_rupiah(r["total_biaya"]))


# [MENU 9] Menampilkan Detail Reservasi Berdasarkan ID
def detail_reservasi():
    reservasi = muat_json(FILE_RESERVASI)
    if len(reservasi) == 0:
        print("\nBelum ada data reservasi.")
        return

    id_input = input("\nMasukkan ID reservasi tamu (misal: RES-001): ").strip()

    for r in reservasi:
        if str(r["id"]).lower() == id_input.lower():
            detail_reservasi_by_object(r)
            return

    print("Reservasi tidak ditemukan!")


# ==============================================================================
# 6. MENU UTAMA & PENGENDALI PROGRAM (SESUAI TAMPILAN GAMBAR)
# ==============================================================================

def menu_utama():
    while True:
        print("\n========================================")
        print("     SISTEM MANAJEMEN & HOTEL")
        print("========================================")
        print("1. Menampilkan Data Kamar")
        print("2. Atur Tipe dan Harga Kamar")
        print("3. Ubah Status Kamar (Full / Tersedia)")
        print("4. Manajemen Data Tamu")
        print("5. Menampilkan Seluruh Reservasi")
        print("6. Tambah Reservasi Kamar Baru")
        print("7. Mengubah Status Reservasi")
        print("8. Membatalkan Reservasi")
        print("9. Menampilkan Detail Reservasi")
        print("0. Keluar")
        print("========================================")

        pilihan = input("Pilih menu (0-9): ").strip()

        data_reservasi = muat_json(FILE_RESERVASI)

        if pilihan == "1":
            tampilkan_kamar()           # Menjalankan Menu 1
        elif pilihan == "2":
            atur_tipe_dan_harga()       # Menjalankan Menu 2
        elif pilihan == "3":
            ubah_status_kamar()         # Menjalankan Menu 3
        elif pilihan == "4":
            menu_tamu()                 # Menjalankan Menu 4
        elif pilihan == "5":
            tampilkan_reservasi()       # Menjalankan Menu 5
        elif pilihan == "6":
            tambah_reservasi(data_reservasi)  # Menjalankan Menu 6
        elif pilihan == "7":
            ubah_status()               # Menjalankan Menu 7
        elif pilihan == "8":
            batalkan_reservasi()        # Menjalankan Menu 8
        elif pilihan == "9":
            detail_reservasi()          # Menjalankan Menu 9
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan sistem hotel!")
            break                       # Menjalankan Menu 0 (Keluar)
        else:
            print("Pilihan tidak valid! Silakan coba lagi.")


if __name__ == "__main__":
    menu_utama()