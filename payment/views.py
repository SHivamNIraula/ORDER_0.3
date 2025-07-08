"""
Views for payment app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from orders.models import Order

@login_required
def payment_options(request, order_id):
    """Display payment options for an order"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    context = {'order': order}
    return render(request, 'payment/payment_options.html', context)

@login_required
def qr_payment(request, order_id):
    """Display QR code for payment"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    context = {'order': order}
    return render(request, 'payment/qr_payment.html', context)

@login_required
def counter_payment(request, order_id):
    """Handle counter payment selection"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Send notification to admin
    channel_layer = get_channel_layer()
    if channel_layer:
        notification_data = {
            'type': 'counter_payment',
            'message': f'Table {order.table.table_number} will pay at counter',
            'order_id': order.id,
            'table_number': order.table.table_number
        }
        
        async_to_sync(channel_layer.group_send)(
            'admin_orders',
            {
                'type': 'counter_payment_notification',
                'notification': notification_data
            }
        )
    
    messages.success(request, f'Payment notification sent to counter. Please proceed to pay at the counter for Table {order.table.table_number}.')
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def process_payment(request, order_id):
    """Process payment for an order"""
    messages.success(request, 'Payment processed successfully!')
    return redirect('payment:payment_success', order_id=order_id)

@login_required
def payment_success(request, order_id):
    """Display payment success page"""
    context = {'order_id': order_id}
    return render(request, 'payment/payment_success.html', context)
