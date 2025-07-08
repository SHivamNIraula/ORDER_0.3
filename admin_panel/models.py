from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

class AdminSettings(models.Model):
    """Global settings for the restaurant"""
    restaurant_name = models.CharField(max_length=200, default="My Restaurant")
    max_tables = models.IntegerField(default=20)
    default_table_capacity = models.IntegerField(default=4)
    service_charge_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Admin Settings"
        verbose_name_plural = "Admin Settings"
    
    def __str__(self):
        return f"Settings for {self.restaurant_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create admin settings"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings

class DailyReport(models.Model):
    """Daily sales and order reports"""
    date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Report for {self.date}"
    
    @classmethod
    def generate_daily_report(cls, date=None):
        """Generate or update daily report"""
        if date is None:
            date = timezone.now().date()
        
        from orders.models import Order
        from payment.models import Payment
        
        # Get orders for the date
        orders = Order.objects.filter(created_at__date=date)
        completed_orders = orders.filter(status__in=['delivered', 'paid'])
        cancelled_orders = orders.filter(status='cancelled')
        
        # Calculate revenue from completed payments
        payment_revenue = Payment.objects.filter(
            order__created_at__date=date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Get order IDs that have completed payments to avoid double counting
        paid_via_payment_ids = Payment.objects.filter(
            order__created_at__date=date,
            status='completed'
        ).values_list('order_id', flat=True)
        
        # Add revenue from orders marked as paid (excluding those already paid via payment system)
        paid_orders_revenue = orders.filter(
            status='paid'
        ).exclude(id__in=paid_via_payment_ids).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Combine both revenue sources (no double counting)
        revenue = payment_revenue + paid_orders_revenue
        
        # Calculate average order value
        avg_order_value = Decimal('0.00')
        if completed_orders.exists():
            avg_order_value = revenue / completed_orders.count()
        
        # Create or update report
        report, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_orders': orders.count(),
                'total_revenue': revenue,
                'completed_orders': completed_orders.count(),
                'cancelled_orders': cancelled_orders.count(),
                'average_order_value': avg_order_value,
            }
        )
        
        if not created:
            report.total_orders = orders.count()
            report.total_revenue = revenue
            report.completed_orders = completed_orders.count()
            report.cancelled_orders = cancelled_orders.count()
            report.average_order_value = avg_order_value
            report.save()
        
        return report

class MonthlyReport(models.Model):
    """Monthly aggregated reports"""
    year = models.IntegerField()
    month = models.IntegerField()
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"Report for {self.month}/{self.year}"
    
    @classmethod
    def generate_monthly_report(cls, year=None, month=None):
        """Generate or update monthly report"""
        if year is None or month is None:
            now = timezone.now()
            year = year or now.year
            month = month or now.month
        
        # Aggregate daily reports for the month
        daily_reports = DailyReport.objects.filter(
            date__year=year,
            date__month=month
        )
        
        if not daily_reports.exists():
            return None
        
        aggregated = daily_reports.aggregate(
            total_orders=Sum('total_orders'),
            total_revenue=Sum('total_revenue'),
            completed_orders=Sum('completed_orders'),
            cancelled_orders=Sum('cancelled_orders')
        )
        
        # Calculate average order value
        avg_order_value = Decimal('0.00')
        if aggregated['completed_orders'] and aggregated['completed_orders'] > 0:
            avg_order_value = aggregated['total_revenue'] / aggregated['completed_orders']
        
        # Create or update monthly report
        report, created = cls.objects.get_or_create(
            year=year,
            month=month,
            defaults={
                'total_orders': aggregated['total_orders'] or 0,
                'total_revenue': aggregated['total_revenue'] or Decimal('0.00'),
                'completed_orders': aggregated['completed_orders'] or 0,
                'cancelled_orders': aggregated['cancelled_orders'] or 0,
                'average_order_value': avg_order_value,
            }
        )
        
        if not created:
            report.total_orders = aggregated['total_orders'] or 0
            report.total_revenue = aggregated['total_revenue'] or Decimal('0.00')
            report.completed_orders = aggregated['completed_orders'] or 0
            report.cancelled_orders = aggregated['cancelled_orders'] or 0
            report.average_order_value = avg_order_value
            report.save()
        
        return report
