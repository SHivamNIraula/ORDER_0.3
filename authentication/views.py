"""
Views for authentication app
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    """User login view"""
    # If user is already logged in, redirect them appropriately
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_panel:dashboard')
        else:
            return redirect('tables:table_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type
            if user.is_staff or user.is_superuser:
                return redirect('admin_panel:dashboard')
            else:
                return redirect('tables:table_list')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'authentication/login.html')

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('authentication:login')
    
    return render(request, 'authentication/register.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('authentication:login')