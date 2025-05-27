from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils import timezone
import json

from menu.models import Meja, Pesanan, DetailPesanan

def kasir_index(request):
    """
    Main kasir landing page with overview and navigation
    """
    # Get some basic statistics
    pesanan_pending = Pesanan.objects.filter(status__in=['BARU', 'DIPROSES']).count()
    pesanan_selesai_belum_bayar = Pesanan.objects.filter(status='SELESAI').count()
    total_meja = Meja.objects.count()
    
    context = {
        'pesanan_pending': pesanan_pending,
        'pesanan_selesai_belum_bayar': pesanan_selesai_belum_bayar,
        'total_meja': total_meja,
    }
    
    return render(request, 'kasir/kasir_index.html', context)

def dapur_view(request):
    """
    View untuk tampilan dapur (Kitchen Display System)
    """
    # Ambil pesanan dengan status BARU dan DIPROSES
    pesanan_baru = Pesanan.objects.filter(status='BARU').order_by('created_at')
    pesanan_diproses = Pesanan.objects.filter(status='DIPROSES').order_by('created_at')
    
    context = {
        'pesanan_baru': pesanan_baru,
        'pesanan_diproses': pesanan_diproses,
    }
    
    return render(request, 'kasir/dapur.html', context)

def kasir_dashboard(request):
    """
    View untuk dashboard kasir
    """
    # Form pencarian meja
    return render(request, 'kasir/kasir_dashboard.html')

def detail_pesanan_meja(request, nomor_meja):
    """
    View untuk menampilkan detail pesanan berdasarkan meja
    """
    # Ambil meja
    meja = get_object_or_404(Meja, nomor_meja=nomor_meja)
    
    # Ambil pesanan yang belum dibayar untuk meja tersebut
    pesanan_list = Pesanan.objects.filter(
        meja=meja,
        status__in=['BARU', 'DIPROSES', 'SELESAI']
    ).order_by('-created_at')
    
    context = {
        'meja': meja,
        'pesanan_list': pesanan_list,
    }
    
    return render(request, 'kasir/detail_pesanan_meja.html', context)

@csrf_exempt
@require_POST
def update_status_pesanan(request, pesanan_id):
    """
    API endpoint untuk update status pesanan
    """
    try:
        # Ambil pesanan
        pesanan = get_object_or_404(Pesanan, id=pesanan_id)
        
        # Parse data dari request
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validasi status
        valid_statuses = ['BARU', 'DIPROSES', 'SELESAI', 'DIBAYAR', 'DIBATALKAN']
        if new_status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': 'Status tidak valid'}, status=400)
        
        # Update status
        pesanan.status = new_status
        pesanan.save()
        
        return JsonResponse({'status': 'success', 'message': 'Status pesanan berhasil diupdate'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def print_receipt(request, pesanan_id):
    """
    View untuk print receipt pesanan
    """
    pesanan = get_object_or_404(Pesanan, id=pesanan_id)
      # Hitung total pesanan
    detail_pesanan = pesanan.detailpesanan_set.all()
    total = sum(detail.subtotal for detail in detail_pesanan)
    
    context = {
        'pesanan': pesanan,
        'detail_pesanan': detail_pesanan,
        'total': total,
        'print_time': timezone.now(),
    }
    
    # Render template khusus untuk receipt
    receipt_html = render_to_string('kasir/receipt.html', context)
    
    # Return sebagai response HTML yang bisa di-print
    response = HttpResponse(receipt_html, content_type='text/html')
    response['Content-Disposition'] = f'inline; filename="receipt_pesanan_{pesanan_id}.html"'
    
    return response
