#!/usr/bin/env python
"""
Script untuk mengisi data sample ke dalam database
Jalankan dengan: python manage.py shell < populate_sample_data.py
"""

from menu.models import Meja, KategoriMenu, MenuItem
from decimal import Decimal

print("Mengisi data sample...")

# Buat data meja
meja_data = [
    {'nomor_meja': '1', 'kapasitas': 2},
    {'nomor_meja': '2', 'kapasitas': 4},
    {'nomor_meja': '3', 'kapasitas': 4},
    {'nomor_meja': '4', 'kapasitas': 6},
    {'nomor_meja': 'A1', 'kapasitas': 2},
    {'nomor_meja': 'A2', 'kapasitas': 4},
    {'nomor_meja': 'VIP1', 'kapasitas': 8},
]

for data in meja_data:
    meja, created = Meja.objects.get_or_create(
        nomor_meja=data['nomor_meja'],
        defaults={'kapasitas': data['kapasitas']}
    )
    if created:
        print(f"✓ Meja {meja.nomor_meja} berhasil dibuat")

# Buat kategori menu
kategori_data = [
    {'nama': 'Makanan Utama', 'deskripsi': 'Nasi dan lauk pauk', 'urutan': 1},
    {'nama': 'Minuman', 'deskripsi': 'Minuman segar dan hangat', 'urutan': 2},
    {'nama': 'Appetizer', 'deskripsi': 'Makanan pembuka', 'urutan': 3},
    {'nama': 'Dessert', 'deskripsi': 'Makanan penutup', 'urutan': 4},
]

for data in kategori_data:
    kategori, created = KategoriMenu.objects.get_or_create(
        nama=data['nama'],
        defaults={
            'deskripsi': data['deskripsi'],
            'urutan': data['urutan']
        }
    )
    if created:
        print(f"✓ Kategori {kategori.nama} berhasil dibuat")

# Buat menu items
menu_data = [
    # Makanan Utama
    {'nama': 'Nasi Gudeg Jogja', 'kategori': 'Makanan Utama', 'harga': 25000, 'deskripsi': 'Nasi gudeg khas Jogja dengan ayam dan telur'},
    {'nama': 'Nasi Rawon', 'kategori': 'Makanan Utama', 'harga': 28000, 'deskripsi': 'Rawon daging sapi dengan kuah hitam khas Jawa Timur'},
    {'nama': 'Ayam Bakar Taliwang', 'kategori': 'Makanan Utama', 'harga': 32000, 'deskripsi': 'Ayam bakar pedas khas Lombok'},
    {'nama': 'Gado-gado Jakarta', 'kategori': 'Makanan Utama', 'harga': 22000, 'deskripsi': 'Salad sayuran dengan bumbu kacang'},
    {'nama': 'Nasi Padang', 'kategori': 'Makanan Utama', 'harga': 30000, 'deskripsi': 'Nasi dengan aneka lauk khas Padang'},
    
    # Minuman
    {'nama': 'Es Teh Manis', 'kategori': 'Minuman', 'harga': 8000, 'deskripsi': 'Teh manis dingin segar'},
    {'nama': 'Es Jeruk', 'kategori': 'Minuman', 'harga': 10000, 'deskripsi': 'Jeruk peras segar dengan es'},
    {'nama': 'Kopi Tubruk', 'kategori': 'Minuman', 'harga': 12000, 'deskripsi': 'Kopi hitam khas Indonesia'},
    {'nama': 'Jus Alpukat', 'kategori': 'Minuman', 'harga': 15000, 'deskripsi': 'Jus alpukat segar dengan susu'},
    {'nama': 'Es Cendol', 'kategori': 'Minuman', 'harga': 13000, 'deskripsi': 'Minuman tradisional dengan cendol dan santan'},
    
    # Appetizer
    {'nama': 'Kerupuk Udang', 'kategori': 'Appetizer', 'harga': 5000, 'deskripsi': 'Kerupuk udang renyah'},
    {'nama': 'Tahu Crispy', 'kategori': 'Appetizer', 'harga': 12000, 'deskripsi': 'Tahu goreng crispy dengan saus sambal'},
    {'nama': 'Lumpia Semarang', 'kategori': 'Appetizer', 'harga': 15000, 'deskripsi': 'Lumpia basah khas Semarang'},
    {'nama': 'Siomay Bandung', 'kategori': 'Appetizer', 'harga': 18000, 'deskripsi': 'Siomay dengan bumbu kacang'},
    
    # Dessert
    {'nama': 'Es Krim Vanilla', 'kategori': 'Dessert', 'harga': 12000, 'deskripsi': 'Es krim vanilla dengan topping'},
    {'nama': 'Pisang Goreng', 'kategori': 'Dessert', 'harga': 10000, 'deskripsi': 'Pisang goreng crispy dengan madu'},
    {'nama': 'Klepon', 'kategori': 'Dessert', 'harga': 8000, 'deskripsi': 'Kue tradisional dengan gula merah'},
    {'nama': 'Es Campur', 'kategori': 'Dessert', 'harga': 15000, 'deskripsi': 'Es campur dengan aneka topping'},
]

for data in menu_data:
    try:
        kategori = KategoriMenu.objects.get(nama=data['kategori'])
        menu_item, created = MenuItem.objects.get_or_create(
            nama=data['nama'],
            defaults={
                'kategori': kategori,
                'harga': Decimal(str(data['harga'])),
                'deskripsi': data['deskripsi'],
                'is_tersedia': True
            }
        )
        if created:
            print(f"✓ Menu {menu_item.nama} berhasil dibuat - Rp {menu_item.harga}")
    except KategoriMenu.DoesNotExist:
        print(f"✗ Kategori {data['kategori']} tidak ditemukan untuk menu {data['nama']}")

print("\n🎉 Data sample berhasil diisi!")
print("Anda sekarang dapat:")
print("1. Mengakses halaman menu: http://127.0.0.1:8000/menu/meja/1/")
print("2. Melihat kitchen display: http://127.0.0.1:8000/kasir/dapur/")
print("3. Akses dashboard kasir: http://127.0.0.1:8000/kasir/kasir_dashboard/")
print("4. Kelola data di admin: http://127.0.0.1:8000/admin/")
