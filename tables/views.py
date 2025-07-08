"""
Views for tables app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Table

@login_required
def table_list(request):
    """Display available tables"""
    # Release any table currently reserved by this user
    current_table = Table.objects.filter(reserved_by=request.user, is_available=False).first()
    
    # Get all tables
    tables = Table.objects.all().order_by('table_number')
    
    context = {
        'tables': tables,
        'current_table': current_table,
    }
    return render(request, 'tables/table_list.html', context)

@login_required
def select_table(request, table_id):
    """Select a specific table"""
    table = get_object_or_404(Table, id=table_id)
    
    # Check if table is available
    if not table.is_available:
        messages.error(request, f'Table {table.table_number} is already occupied!')
        return redirect('tables:table_list')
    
    # Release any previously reserved table by this user
    previous_table = Table.objects.filter(reserved_by=request.user, is_available=False).first()
    if previous_table:
        previous_table.release_table()
        messages.info(request, f'Released Table {previous_table.table_number}')
    
    # Reserve the new table
    table.is_available = False
    table.reserved_by = request.user
    table.reserved_at = timezone.now()
    table.save()
    
    messages.success(request, f'Table {table.table_number} has been selected successfully!')
    return redirect('food:food_menu')

@login_required
def release_table(request):
    """Release current user's table"""
    table = Table.objects.filter(reserved_by=request.user, is_available=False).first()
    
    if table:
        table.release_table()
        messages.success(request, f'Table {table.table_number} has been released.')
    else:
        messages.info(request, 'No table to release.')
    
    return redirect('tables:table_list')