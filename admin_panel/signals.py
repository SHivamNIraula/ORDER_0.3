from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from orders.models import Order
from .models import DailyReport, MonthlyReport
from django.utils import timezone

channel_layer = get_channel_layer()

@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance, created, **kwargs):
    """Send real-time notification when order is created or updated"""
    if channel_layer:
        order_data = {
            'id': instance.id,
            'customer': instance.customer.username,
            'table_number': instance.table.table_number,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'total_amount': str(instance.total_amount),
            'created_at': instance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        message_type = 'new_order' if created else 'order_update'
        
        async_to_sync(channel_layer.group_send)(
            'admin_orders',
            {
                'type': message_type,
                'order': order_data
            }
        )
    
    # Update daily report when order status changes to delivered or paid
    if instance.status in ['delivered', 'paid']:
        today = timezone.now().date()
        DailyReport.generate_daily_report(today)
        # Also update monthly report
        MonthlyReport.generate_monthly_report(today.year, today.month)

@receiver(post_save, sender=Order)
def update_daily_reports(sender, instance, **kwargs):
    """Update daily reports when order is completed"""
    if instance.status in ['delivered', 'cancelled', 'paid']:
        today = timezone.now().date()
        DailyReport.generate_daily_report(today)
        # Also update monthly report
        MonthlyReport.generate_monthly_report(today.year, today.month)