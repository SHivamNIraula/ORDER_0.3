"""
Views for food app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import FoodCategory, FoodItem
from decimal import Decimal

@login_required
def food_menu(request):
    """Display food menu with categories and items"""
    categories = FoodCategory.objects.filter(is_active=True).prefetch_related('items')
    food_items = FoodItem.objects.filter(is_available=True).select_related('category')
    
    # Get cart count for display
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    
    context = {
        'categories': categories,
        'food_items': food_items,
        'cart_count': cart_count,
    }
    return render(request, 'food/food_menu.html', context)

@login_required
def category_items(request, category_id):
    """Display items in a specific category"""
    category = get_object_or_404(FoodCategory, id=category_id, is_active=True)
    items = FoodItem.objects.filter(category=category, is_available=True)
    
    context = {
        'category': category,
        'items': items,
    }
    return render(request, 'food/category_items.html', context)

@login_required
def add_to_cart(request, food_id):
    """Add food item to cart (handles both GET and POST)"""
    food_item = get_object_or_404(FoodItem, id=food_id, is_available=True)
    
    # Get or create cart in session
    cart = request.session.get('cart', {})
    
    # Convert food_id to string (session keys must be strings)
    food_id_str = str(food_id)
    
    if food_id_str in cart:
        # Item already in cart, increase quantity
        cart[food_id_str]['quantity'] += 1
        cart[food_id_str]['subtotal'] = str(Decimal(cart[food_id_str]['price']) * cart[food_id_str]['quantity'])
    else:
        # Add new item to cart
        cart[food_id_str] = {
            'name': food_item.name,
            'price': str(food_item.price),
            'quantity': 1,
            'subtotal': str(food_item.price),
            'image': food_item.image.url if food_item.image else None,
        }
    
    # Save cart to session
    request.session['cart'] = cart
    request.session.modified = True
    
    # Calculate cart totals
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(Decimal(item['subtotal']) for item in cart.values())
    
    # Handle AJAX requests (return JSON)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'message': f'{food_item.name} added to cart!',
            'cart_count': cart_count,
            'cart_total': str(cart_total),
        })
    
    # Handle regular requests (redirect with message)
    messages.success(request, f'{food_item.name} added to cart!')
    return redirect('food:food_menu')

@login_required
def remove_from_cart(request, food_id):
    """Remove item from cart"""
    cart = request.session.get('cart', {})
    food_id_str = str(food_id)
    
    if food_id_str in cart:
        del cart[food_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')
    
    return redirect('orders:view_cart')

@login_required
def update_cart_quantity(request, food_id):
    """Update quantity of item in cart"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        food_id_str = str(food_id)
        
        if food_id_str in cart and quantity > 0:
            cart[food_id_str]['quantity'] = quantity
            cart[food_id_str]['subtotal'] = str(Decimal(cart[food_id_str]['price']) * quantity)
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Cart updated!')
        elif quantity <= 0:
            # Remove item if quantity is 0 or negative
            if food_id_str in cart:
                del cart[food_id_str]
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, 'Item removed from cart!')
    
    return redirect('orders:view_cart')
