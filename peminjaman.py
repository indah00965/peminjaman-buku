import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3

# Font standar
FONT_BESAR = ("Arial", 12)
FONT_TABEL = ("Arial", 11)

# Stok buku
buku_list = [
    {"judul": "Teknologi Masa Depan", "stok": 10},
    {"judul": "Sastra Nusantara", "stok": 5},
    {"judul": "Fisika Quantum", "stok": 2},
    {"judul": "Ekonomi Global", "stok": 7},
    {"judul": "AI dan Masa Depan Manusia", "stok": 13},
    {"judul": "Sejarah Dunia", "stok": 4},
    {"judul": "Algoritma dan Pemrograman", "stok": 9},
    {"judul": "Psikologi Modern", "stok": 6},
    {"judul": "Manajemen Waktu", "stok": 8},
    {"judul": "Kecerdasan Emosional", "stok": 3}
]

# List peminjam (sementara)
daftar_peminjam = []

# Inisialisasi database
def init_db():
    conn = sqlite3.connect("peminjaman.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS peminjaman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            judul TEXT,
            pinjam TEXT,
            kembali TEXT
        )
    ''')
    conn.commit()
    conn.close()

def pinjam_buku():
    nama = entry_nama.get()
    judul = combo_buku.get()
    if not nama or not judul:
        messagebox.showwarning("⚠ Peringatan", "Lengkapi nama dan pilih buku.")
        return
    for buku in buku_list:
        if buku["judul"] == judul:
            if buku["stok"] > 0:
                buku["stok"] -= 1
                tanggal_pinjam = datetime.now()
                tanggal_pengembalian = tanggal_pinjam + timedelta(days=7)

                # Simpan ke daftar sementara
                daftar_peminjam.append({
                    "nama": nama.title(),
                    "judul": judul,
                    "pinjam": tanggal_pinjam.strftime("%d-%m-%Y"),
                    "kembali": tanggal_pengembalian.strftime("%d-%m-%Y")
                })

                # Simpan ke database
                conn = sqlite3.connect("peminjaman.db")
                c = conn.cursor()
                c.execute("INSERT INTO peminjaman (nama, judul, pinjam, kembali) VALUES (?, ?, ?, ?)",
                          (nama.title(), judul, tanggal_pinjam.strftime("%d-%m-%Y"), tanggal_pengembalian.strftime("%d-%m-%Y")))
                conn.commit()
                conn.close()

                messagebox.showinfo(
                    "✅ Berhasil",
                    f"{nama} meminjam '{judul}'.\nTanggal pengembalian: {tanggal_pengembalian.strftime('%d-%m-%Y')}"
                )
                update_stok()
                update_peminjam()
            else:
                messagebox.showerror("❌ Gagal", f"Buku '{judul}' habis.")
            return

def kembalikan_buku():
    nama = entry_nama.get()
    judul = combo_buku.get()
    if not nama or not judul:
        messagebox.showwarning("⚠ Peringatan", "Lengkapi nama dan pilih buku.")
        return

    # Hapus dari daftar sementara
    found = False
    for i, pinjam in enumerate(daftar_peminjam):
        if pinjam["nama"].lower() == nama.lower() and pinjam["judul"] == judul:
            daftar_peminjam.pop(i)
            found = True
            break

    if found:
        for buku in buku_list:
            if buku["judul"] == judul:
                buku["stok"] += 1

                # Hapus dari database
                conn = sqlite3.connect("peminjaman.db")
                c = conn.cursor()
                c.execute("DELETE FROM peminjaman WHERE nama=? AND judul=? LIMIT 1", (nama.title(), judul))
                conn.commit()
                conn.close()

                messagebox.showinfo("📘 Kembali", f"{nama} mengembalikan '{judul}'.")
                update_stok()
                update_peminjam()
                return
    else:
        messagebox.showerror("❌ Gagal", f"Tidak ditemukan peminjaman '{judul}' atas nama {nama}.")

def update_stok():
    for i in tree_stok.get_children():
        tree_stok.delete(i)
    for i, buku in enumerate(buku_list, start=1):
        status = "Tersedia" if buku["stok"] > 0 else "Habis"
        tag = "habis" if buku["stok"] == 0 else ("even" if i % 2 == 0 else "odd")
        tree_stok.insert("", "end", values=(i, buku["judul"], buku["stok"], status), tags=(tag,))

def update_peminjam():
    daftar_peminjam.clear()

    conn = sqlite3.connect("peminjaman.db")
    c = conn.cursor()
    c.execute("SELECT nama, judul, pinjam, kembali FROM peminjaman")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        daftar_peminjam.append({
            "nama": row[0],
            "judul": row[1],
            "pinjam": row[2],
            "kembali": row[3]
        })

    for i in tree_peminjam.get_children():
        tree_peminjam.delete(i)
    for i, pinjam in enumerate(daftar_peminjam, start=1):
        tree_peminjam.insert("", "end", values=(i, pinjam["nama"], pinjam["judul"], pinjam["pinjam"], pinjam["kembali"]))

# UI
root = tk.Tk()
root.title("📚 Aplikasi Pinjam & Kembali Buku")

tk.Label(root, text="Nama Peminjam:", font=FONT_BESAR).pack(pady=5)
entry_nama = tk.Entry(root, width=30, font=FONT_BESAR)
entry_nama.pack()

tk.Label(root, text="Pilih Buku:", font=FONT_BESAR).pack(pady=5)
combo_buku = ttk.Combobox(root, values=[b["judul"] for b in buku_list], state="readonly", width=35, font=FONT_BESAR)
combo_buku.pack()

tk.Button(root, text="📖 Pinjam", command=pinjam_buku, font=FONT_BESAR).pack(pady=5)
tk.Button(root, text="🔁 Kembalikan", command=kembalikan_buku, font=FONT_BESAR).pack(pady=5)

# Tabel Stok Buku
tk.Label(root, text="📚 Stok Buku", font=FONT_BESAR).pack()
columns_stok = ("No", "Judul Buku", "Stok", "Status")
tree_stok = ttk.Treeview(root, columns=columns_stok, show="headings", height=8)
for col in columns_stok:
    tree_stok.heading(col, text=col)
    tree_stok.column(col, anchor="center", width=180 if col == "Judul Buku" else 100)
tree_stok.pack(pady=10)

# Tabel Daftar Peminjam
tk.Label(root, text="👥 Daftar Peminjam", font=FONT_BESAR).pack()
columns_peminjam = ("No", "Nama", "Judul Buku", "Tanggal Pinjam", "Pengembalian")
tree_peminjam = ttk.Treeview(root, columns=columns_peminjam, show="headings", height=8)
for col in columns_peminjam:
    tree_peminjam.heading(col, text=col)
    tree_peminjam.column(col, anchor="center", width=140)
tree_peminjam.pack(pady=10)

# Gaya tampilan
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.configure("Treeview", font=FONT_TABEL, rowheight=30)

tree_stok.tag_configure("odd", background="#f0f0ff")
tree_stok.tag_configure("even", background="#ffffff")
tree_stok.tag_configure("habis", background="#ffe5e5", foreground="red")

# Inisialisasi DB & Update tampilan
init_db()
update_stok()
update_peminjam()

root.mainloop()
