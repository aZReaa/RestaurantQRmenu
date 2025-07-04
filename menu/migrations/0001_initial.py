# Generated by Django 5.2.1 on 2025-05-27 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KategoriMenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=100)),
                ('deskripsi', models.TextField(blank=True, null=True)),
                ('urutan', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Kategori Menu',
                'verbose_name_plural': 'Kategori Menu',
                'ordering': ['urutan', 'nama'],
            },
        ),
        migrations.CreateModel(
            name='Meja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomor_meja', models.CharField(max_length=10, unique=True)),
                ('kapasitas', models.IntegerField(default=4)),
                ('is_aktif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Meja',
                'verbose_name_plural': 'Meja-meja',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=200)),
                ('deskripsi', models.TextField(blank=True, null=True)),
                ('harga', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_tersedia', models.BooleanField(default=True)),
                ('gambar', models.ImageField(blank=True, null=True, upload_to='menu_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('kategori', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.kategorimenu')),
            ],
            options={
                'verbose_name': 'Menu Item',
                'verbose_name_plural': 'Menu Items',
                'ordering': ['kategori__urutan', 'nama'],
            },
        ),
        migrations.CreateModel(
            name='Pesanan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_harga', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('BARU', 'Pesanan Baru'), ('DIPROSES', 'Sedang Diproses'), ('SELESAI', 'Selesai Dibuat'), ('DIBAYAR', 'Sudah Dibayar'), ('DIBATALKAN', 'Dibatalkan')], default='BARU', max_length=20)),
                ('catatan', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.meja')),
            ],
            options={
                'verbose_name': 'Pesanan',
                'verbose_name_plural': 'Pesanan-pesanan',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DetailPesanan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah', models.IntegerField(default=1)),
                ('harga_per_item', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('catatan_item', models.TextField(blank=True, null=True)),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.menuitem')),
                ('pesanan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.pesanan')),
            ],
            options={
                'verbose_name': 'Detail Pesanan',
                'verbose_name_plural': 'Detail Pesanan',
            },
        ),
    ]
