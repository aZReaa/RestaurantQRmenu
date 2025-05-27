from django.contrib import admin
from .models import Meja, KategoriMenu, MenuItem, Pesanan, DetailPesanan

@admin.register(Meja)
class MejaAdmin(admin.ModelAdmin):
    list_display = ['nomor_meja', 'kapasitas', 'is_aktif']
    list_filter = ['is_aktif', 'kapasitas']
    search_fields = ['nomor_meja']
    list_editable = ['is_aktif']

@admin.register(KategoriMenu)
class KategoriMenuAdmin(admin.ModelAdmin):
    list_display = ['nama', 'urutan', 'deskripsi']
    list_editable = ['urutan']
    ordering = ['urutan', 'nama']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['nama', 'kategori', 'harga', 'is_tersedia', 'created_at']
    list_filter = ['kategori', 'is_tersedia', 'created_at']
    search_fields = ['nama', 'deskripsi']
    list_editable = ['harga', 'is_tersedia']
    ordering = ['kategori__urutan', 'nama']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama', 'kategori', 'deskripsi')
        }),
        ('Harga & Ketersediaan', {
            'fields': ('harga', 'is_tersedia')
        }),
        ('Gambar', {
            'fields': ('gambar',),
            'classes': ('collapse',)
        }),
    )

class DetailPesananInline(admin.TabularInline):
    model = DetailPesanan
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Pesanan)
class PesananAdmin(admin.ModelAdmin):
    list_display = ['id', 'meja', 'status', 'total_harga', 'get_total_items', 'created_at']
    list_filter = ['status', 'meja', 'created_at']
    search_fields = ['id', 'meja__nomor_meja']
    list_editable = ['status']
    readonly_fields = ['total_harga', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    inlines = [DetailPesananInline]
    
    fieldsets = (
        ('Informasi Pesanan', {
            'fields': ('meja', 'status', 'total_harga')
        }),
        ('Catatan', {
            'fields': ('catatan',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DetailPesanan)
class DetailPesananAdmin(admin.ModelAdmin):
    list_display = ['pesanan', 'menu_item', 'jumlah', 'harga_per_item', 'subtotal']
    list_filter = ['pesanan__status', 'menu_item__kategori']
    search_fields = ['pesanan__id', 'menu_item__nama']
    readonly_fields = ['subtotal']
