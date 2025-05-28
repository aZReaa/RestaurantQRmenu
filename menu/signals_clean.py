from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
from .models import Pesanan, MenuAnalytics, DailyReport


@receiver(post_save, sender=Pesanan)
def update_analytics_on_payment(sender, instance, created, **kwargs):
    """
    Update analytics hanya ketika pesanan berubah status menjadi DIBAYAR
    dan belum pernah diproses sebelumnya
    """
    if instance.status == 'DIBAYAR' and not instance.analytics_processed:
        try:
            today = timezone.now().date()
            
            # Update menu analytics untuk setiap item
            for detail in instance.detailpesanan_set.all():
                menu_analytics, analytics_created = MenuAnalytics.objects.get_or_create(
                    menu_item=detail.menu_item,
                    tanggal=today,
                    defaults={
                        'jumlah_terjual': 0,
                        'total_pendapatan': Decimal('0.00')
                    }
                )
                menu_analytics.jumlah_terjual += detail.jumlah
                menu_analytics.total_pendapatan += detail.jumlah * detail.harga_per_item
                menu_analytics.save()
            
            # Update daily report
            daily_report, report_created = DailyReport.objects.get_or_create(
                tanggal=today,
                defaults={
                    'total_pesanan': 0,
                    'total_pendapatan': Decimal('0.00'),
                    'total_item_terjual': 0,
                    'rata_rata_per_pesanan': Decimal('0.00')
                }
            )
            
            total_pendapatan = sum(
                detail.jumlah * detail.harga_per_item 
                for detail in instance.detailpesanan_set.all()
            )
            total_items = sum(
                detail.jumlah 
                for detail in instance.detailpesanan_set.all()
            )
            
            daily_report.total_pesanan += 1
            daily_report.total_pendapatan += total_pendapatan
            daily_report.total_item_terjual += total_items
            
            # Hitung rata-rata per pesanan
            if daily_report.total_pesanan > 0:
                daily_report.rata_rata_per_pesanan = daily_report.total_pendapatan / daily_report.total_pesanan
            
            daily_report.save()
            
            # Mark analytics as processed to prevent duplicate processing
            instance.analytics_processed = True
            instance.save(update_fields=['analytics_processed'])
            
        except Exception as e:
            # Log error but don't crash the payment process
            print(f"Error updating analytics for pesanan {instance.id}: {e}")
            # Still mark as processed to prevent infinite retries
            instance.analytics_processed = True
            instance.save(update_fields=['analytics_processed'])
