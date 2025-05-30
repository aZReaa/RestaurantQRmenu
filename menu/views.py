from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .models import Meja, KategoriMenu, MenuItem, Pesanan, DetailPesanan, DailyReport, MenuAnalytics

def menu_index(request):
    """
    View untuk halaman index menu - redirect ke QR codes
    """
    return HttpResponseRedirect(reverse('menu:qr_codes'))

def menu_view(request, nomor_meja):
    """
    View untuk menampilkan menu berdasarkan nomor meja
    """
    # Ambil meja
    meja = get_object_or_404(Meja, nomor_meja=nomor_meja, is_aktif=True)
    
    # Ambil semua kategori dan menu items
    kategori_list = KategoriMenu.objects.all()
    
    # Group menu items by category
    menu_items_by_category = {}
    for kategori in kategori_list:
        menu_items = MenuItem.objects.filter(
            kategori=kategori, 
            is_tersedia=True
        ).order_by('nama')
        
        if menu_items:
            menu_items_by_category[kategori] = menu_items
    
    context = {
        'meja': meja,
        'menu_items_by_category': menu_items_by_category,
    }
    
    return render(request, 'menu/menu_view.html', context)

@csrf_exempt
@require_POST
def tambah_ke_keranjang(request):
    """
    API endpoint untuk menambahkan item ke keranjang (untuk AJAX request)
    """
    try:
        data = json.loads(request.body)
        menu_item_id = data.get('menu_item_id')
        jumlah = data.get('jumlah', 1)
        catatan = data.get('catatan', '')
        
        # Validasi data
        if not menu_item_id or jumlah < 1:
            return JsonResponse({'status': 'error', 'message': 'Data tidak valid'}, status=400)
        
        # Ambil menu item
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, is_tersedia=True)
        except MenuItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Menu tidak ditemukan'}, status=404)
        
        # Data yang akan dikembalikan
        item_data = {
            'id': menu_item.id,
            'nama': menu_item.nama,
            'harga': float(menu_item.harga),
            'jumlah': jumlah,
            'subtotal': float(menu_item.harga * jumlah),
            'catatan': catatan
        }
        
        return JsonResponse({'status': 'success', 'item': item_data})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def checkout_keranjang(request):
    """
    API endpoint untuk checkout keranjang belanja
    """
    try:
        data = json.loads(request.body)
        nomor_meja = data.get('nomor_meja')
        items = data.get('items', [])
        catatan_pesanan = data.get('catatan_pesanan', '')
        nama_pemesan = data.get('nama_pemesan', 'Pelanggan')
          # Validasi data
        if not nomor_meja or not items:
            return JsonResponse({'status': 'error', 'message': 'Data tidak valid'}, status=400)
        
        # Ambil meja
        try:
            meja = Meja.objects.get(nomor_meja=nomor_meja, is_aktif=True)
        except Meja.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Meja tidak ditemukan'}, status=404)
        
        # Buat pesanan baru
        pesanan = Pesanan.objects.create(
            meja=meja,
            status='BARU',
            catatan=catatan_pesanan,
            nama_pemesan=nama_pemesan,
            total_harga=0  # Akan dihitung otomatis di model
        )
        
        # Tambahkan detail pesanan
        total_harga = Decimal('0')
        
        for item in items:
            menu_item_id = item.get('id')
            jumlah = item.get('jumlah', 1)
            catatan_item = item.get('catatan', '')
            
            # Ambil menu item
            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                
                # Buat detail pesanan
                DetailPesanan.objects.create(
                    pesanan=pesanan,
                    menu_item=menu_item,
                    jumlah=jumlah,
                    harga_per_item=menu_item.harga,
                    subtotal=menu_item.harga * jumlah,
                    catatan_item=catatan_item
                )
                
                total_harga += menu_item.harga * Decimal(str(jumlah))
                
            except MenuItem.DoesNotExist:
                # Skip jika menu tidak ditemukan
                continue
        
        # Update total harga pesanan
        pesanan.total_harga = total_harga
        pesanan.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Pesanan berhasil dibuat',
            'pesanan_id': pesanan.id
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def generate_qr_codes_view(request):
    """
    View untuk generate QR Code untuk semua meja
    """
    from .utils import generate_all_table_qr_codes
    
    if request.method == 'POST':
        results = generate_all_table_qr_codes(request)
        
        # Update model dengan QR Code yang sudah digenerate
        for nomor_meja, file_path in results.items():
            if not file_path.startswith('Error:'):
                try:
                    meja = Meja.objects.get(nomor_meja=nomor_meja)
                    meja.qr_code = file_path
                    meja.save()
                except Meja.DoesNotExist:
                    pass
        
        context = {
            'results': results,
            'success': True
        }
    else:
        # Show current QR Code status
        meja_list = Meja.objects.filter(is_aktif=True)
        context = {
            'meja_list': meja_list,
            'success': False
        }
    
    return render(request, 'menu/qr_codes.html', context)

def download_qr_code(request, nomor_meja):
    """
    Download QR Code untuk meja tertentu
    """
    meja = get_object_or_404(Meja, nomor_meja=nomor_meja, is_aktif=True)
    
    if not meja.qr_code:
        # Generate QR Code jika belum ada
        meja.generate_qr_code(request)
    
    if meja.qr_code:
        from django.http import HttpResponse
        import os
        
        qr_path = meja.qr_code.path
        if os.path.exists(qr_path):
            with open(qr_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="QR_Meja_{nomor_meja}.png"'
                return response
    
    from django.http import Http404
    raise Http404("QR Code tidak ditemukan")


def analytics_dashboard(request):
    """
    View untuk analytics dashboard
    """
    # Tanggal hari ini
    today = timezone.now().date()
    
    # 7 hari terakhir
    week_ago = today - timedelta(days=7)
    
    # Daily reports 7 hari terakhir
    daily_reports = DailyReport.objects.filter(
        tanggal__gte=week_ago,
        tanggal__lte=today
    ).order_by('tanggal')
    
    # Menu analytics hari ini
    today_menu_analytics = MenuAnalytics.objects.filter(
        tanggal=today
    ).select_related('menu_item').order_by('-jumlah_terjual')[:10]
    
    # Top selling menu 7 hari terakhir
    top_menu_week = MenuAnalytics.objects.filter(
        tanggal__gte=week_ago,
        tanggal__lte=today
    ).values('menu_item__nama').annotate(
        total_terjual=Sum('jumlah_terjual'),
        total_pendapatan=Sum('total_pendapatan')
    ).order_by('-total_terjual')[:10]
    
    # Summary hari ini
    today_summary = DailyReport.objects.filter(tanggal=today).first()
    
    # Summary 7 hari terakhir
    week_summary = DailyReport.objects.filter(
        tanggal__gte=week_ago,
        tanggal__lte=today
    ).aggregate(
        total_pesanan=Sum('total_pesanan'),
        total_pendapatan=Sum('total_pendapatan'),
        total_item_terjual=Sum('total_item_terjual')
    )
    
    context = {
        'today': today,
        'daily_reports': daily_reports,
        'today_menu_analytics': today_menu_analytics,
        'top_menu_week': top_menu_week,
        'today_summary': today_summary,
        'week_summary': week_summary,
    }
    
    return render(request, 'menu/analytics.html', context)
