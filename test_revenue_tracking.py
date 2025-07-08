#!/usr/bin/env python3
"""
Test script to verify revenue tracking functionality
"""
import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.insert(0, '/mnt/c/PYTHON DJANGO PROJECT/ORDER_0.1/RESTAURANT_ORDER_SYSTEM')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_system.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from orders.models import Order, OrderItem
from tables.models import Table
from food.models import FoodItem, FoodCategory
from admin_panel.models import DailyReport, MonthlyReport
from payment.models import Payment

def test_revenue_tracking():
    """Test that revenue is tracked when order status changes to 'paid'"""
    print("Testing revenue tracking functionality...")
    
    # Get today's date
    today = timezone.now().date()
    
    # Check if we have required models
    try:
        # Check if we have users
        if not User.objects.exists():
            print("Warning: No users exist. Revenue tracking requires orders with customers.")
            return
        
        # Check if we have tables
        if not Table.objects.exists():
            print("Warning: No tables exist. Revenue tracking requires orders with tables.")
            return
            
        # Check if we have food items
        if not FoodItem.objects.exists():
            print("Warning: No food items exist. Revenue tracking requires orders with food items.")
            return
        
        # Generate initial daily report
        initial_report = DailyReport.generate_daily_report(today)
        print(f"Initial daily report - Revenue: ${initial_report.total_revenue}")
        
        # Generate initial monthly report
        initial_monthly = MonthlyReport.generate_monthly_report(today.year, today.month)
        if initial_monthly:
            print(f"Initial monthly report - Revenue: ${initial_monthly.total_revenue}")
        
        # Get test data
        user = User.objects.first()
        table = Table.objects.first()
        food_item = FoodItem.objects.first()
        
        # Create a test order
        test_order = Order.objects.create(
            customer=user,
            table=table,
            status='pending',
            total_amount=Decimal('25.50'),
            special_instructions='Test order for revenue tracking'
        )
        
        # Add order item
        OrderItem.objects.create(
            order=test_order,
            food_item=food_item,
            quantity=2,
            unit_price=food_item.price,
            subtotal=Decimal('25.50')
        )
        
        print(f"Created test order #{test_order.id} with amount ${test_order.total_amount}")
        
        # Change order status to 'paid'
        test_order.status = 'paid'
        test_order.save()
        
        print(f"Changed order status to '{test_order.status}'")
        
        # Check updated reports
        updated_report = DailyReport.generate_daily_report(today)
        print(f"Updated daily report - Revenue: ${updated_report.total_revenue}")
        
        updated_monthly = MonthlyReport.generate_monthly_report(today.year, today.month)
        if updated_monthly:
            print(f"Updated monthly report - Revenue: ${updated_monthly.total_revenue}")
        
        # Clean up test data
        test_order.delete()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_revenue_tracking()