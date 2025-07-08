"""
Views for orders app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Order, OrderItem
from food.models import FoodItem
from tables.models import Table

@login_required
def order_list(request):
    """Display user's orders"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)

@login_required
def create_order(request):
    """Create a new order from cart"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('orders:view_cart')
    
    # Get user's current table
    table = Table.objects.filter(reserved_by=request.user, is_available=False).first()
    if not table:
        messages.error(request, 'You must select a table first!')
        return redirect('tables:table_list')
    
    try:
        with transaction.atomic():
            # Calculate total amount
            total_amount = Decimal('0.00')
            order_items_data = []
            
            for food_id_str, item in cart.items():
                food_item = FoodItem.objects.get(id=int(food_id_str))
                quantity = item['quantity']
                unit_price = food_item.price
                subtotal = unit_price * quantity
                total_amount += subtotal
                
                order_items_data.append({
                    'food_item': food_item,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal,
                })
            
            # Create the order
            order = Order.objects.create(
                customer=request.user,
                table=table,
                total_amount=total_amount,
                status='pending'
            )
            
            # Create order items
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    food_item=item_data['food_item'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    subtotal=item_data['subtotal'],
                )
            
            # Clear the cart
            request.session['cart'] = {}
            request.session.modified = True
            
            # Send real-time notification to admin panel
            channel_layer = get_channel_layer()
            if channel_layer:
                order_data = {
                    'id': order.id,
                    'customer': order.customer.username,
                    'table_number': order.table.table_number,
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'total_amount': str(order.total_amount),
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                
                async_to_sync(channel_layer.group_send)(
                    'admin_orders',
                    {
                        'type': 'new_order',
                        'order': order_data
                    }
                )
            
            messages.success(request, f'Order #{order.id} placed successfully! Total: ${total_amount}')
            return redirect('orders:order_detail', order_id=order.id)
    
    except Exception as e:
        messages.error(request, f'Error creating order: {str(e)}')
        return redirect('orders:view_cart')

@login_required
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    order_items = order.items.all().select_related('food_item')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def view_cart(request):
    """Display shopping cart"""
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')
    
    for food_id_str, item in cart.items():
        try:
            food_item = FoodItem.objects.get(id=int(food_id_str))
            item_data = {
                'food_id': food_id_str,
                'food_item': food_item,
                'name': item['name'],
                'price': Decimal(item['price']),
                'quantity': item['quantity'],
                'subtotal': Decimal(item['subtotal']),
            }
            cart_items.append(item_data)
            cart_total += item_data['subtotal']
        except FoodItem.DoesNotExist:
            # Remove invalid items from cart
            continue
    
    # Check if user has a table
    user_table = Table.objects.filter(reserved_by=request.user, is_available=False).first()
    
    # Calculate tax and charges
    tax_rate = Decimal('0.08')  # 8% tax
    service_charge = Decimal('2.00') if cart_total > 0 else Decimal('0.00')
    tax_amount = cart_total * tax_rate
    final_total = cart_total + tax_amount + service_charge
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': len(cart_items),
        'user_table': user_table,
        'tax_amount': tax_amount,
        'service_charge': service_charge,
        'final_total': final_total,
    }
    return render(request, 'orders/view_cart.html', context)

@login_required
def clear_cart(request):
    """Clear all items from cart"""
    request.session['cart'] = {}
    request.session.modified = True
    messages.success(request, 'Cart cleared!')
    return redirect('orders:view_cart')

@login_required
def order_success(request, order_id):
    """Display order success page after payment"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Ensure order is actually paid
    if order.status != 'paid':
        messages.warning(request, 'This order has not been marked as paid yet.')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_success.html', context)
