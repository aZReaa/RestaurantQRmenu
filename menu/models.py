from django.db import models
from django.utils import timezone

class Meja(models.Model):
    nomor_meja = models.CharField(max_length=10, unique=True)
    kapasitas = models.IntegerField(default=4)
    is_aktif = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Meja"
        verbose_name_plural = "Meja-meja"
    
    def __str__(self):
        return f"Meja {self.nomor_meja}"
    
    def generate_qr_code(self, request=None):
        """Generate QR Code untuk meja ini"""
        from .utils import generate_qr_code_for_table
        try:
            file_path = generate_qr_code_for_table(self.nomor_meja, request)
            self.qr_code = file_path
            self.save()
            return True
        except Exception as e:
            print(f"Error generating QR code for meja {self.nomor_meja}: {e}")
            return False
    
    def get_menu_url(self, request=None):
        """Get URL menu untuk meja ini"""
        if request:
            base_url = request.build_absolute_uri('/')[:-1]
        else:
            base_url = "http://127.0.0.1:8000"
        return f"{base_url}/menu/meja/{self.nomor_meja}/"

class KategoriMenu(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True, null=True)
    urutan = models.IntegerField(default=0)  # untuk sorting
    
    class Meta:
        verbose_name = "Kategori Menu"
        verbose_name_plural = "Kategori Menu"
        ordering = ['urutan', 'nama']
    
    def __str__(self):
        return self.nama

class MenuItem(models.Model):
    nama = models.CharField(max_length=200)
    kategori = models.ForeignKey(KategoriMenu, on_delete=models.CASCADE)
    deskripsi = models.TextField(blank=True, null=True)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    is_tersedia = models.BooleanField(default=True)
    gambar = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['kategori__urutan', 'nama']
    
    def __str__(self):
        return f"{self.nama} - Rp {self.harga:,.0f}"

class Pesanan(models.Model):
    STATUS_CHOICES = [
        ('BARU', 'Pesanan Baru'),
        ('DIPROSES', 'Sedang Diproses'),        ('SELESAI', 'Selesai Dibuat'),
        ('DIBAYAR', 'Sudah Dibayar'),
        ('DIBATALKAN', 'Dibatalkan'),
    ]
    
    meja = models.ForeignKey(Meja, on_delete=models.CASCADE)
    nama_pemesan = models.CharField(max_length=100, default='Pelanggan')
    total_harga = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BARU')
    catatan = models.TextField(blank=True, null=True)
    analytics_processed = models.BooleanField(default=False)  # Track if analytics have been processed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pesanan"
        verbose_name_plural = "Pesanan-pesanan"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pesanan #{self.id} - {self.meja} - {self.status}"
    
    def get_total_items(self):
        return sum(detail.jumlah for detail in self.detailpesanan_set.all())

class DetailPesanan(models.Model):
    pesanan = models.ForeignKey(Pesanan, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    jumlah = models.IntegerField(default=1)
    harga_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    catatan_item = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Detail Pesanan"
        verbose_name_plural = "Detail Pesanan"
    
    def __str__(self):
        return f"{self.menu_item.nama} x{self.jumlah}"
    
    def save(self, *args, **kwargs):
        # Auto calculate subtotal
        self.subtotal = self.jumlah * self.harga_per_item
        super().save(*args, **kwargs)
        
        # Update total pesanan
        self.pesanan.total_harga = sum(
            detail.subtotal for detail in self.pesanan.detailpesanan_set.all()
        )
        self.pesanan.save()

class MenuAnalytics(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)
    jumlah_terjual = models.PositiveIntegerField(default=0)
    total_pendapatan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Analytics Menu"
        verbose_name_plural = "Analytics Menu"
        unique_together = ['menu_item', 'tanggal']
        ordering = ['-tanggal', '-jumlah_terjual']
    
    def __str__(self):
        return f"{self.menu_item.nama} - {self.tanggal} ({self.jumlah_terjual} terjual)"

class DailyReport(models.Model):
    tanggal = models.DateField(unique=True)
    total_pesanan = models.PositiveIntegerField(default=0)
    total_pendapatan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_item_terjual = models.PositiveIntegerField(default=0)
    rata_rata_per_pesanan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Laporan Harian"
        verbose_name_plural = "Laporan Harian"
        ordering = ['-tanggal']
    
    def __str__(self):
        return f"Laporan {self.tanggal} - Rp {self.total_pendapatan:,.0f}"
