from django.db import models
from django.contrib.auth.models import User

class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField(default=4)
    is_available = models.BooleanField(default=True)
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reserved_at = models.DateTimeField(null=True, blank=True)
    icon = models.ImageField(upload_to='table_icons/', default='table_icons/table_with_chairs.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['table_number']
    
    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity})"
    
    def release_table(self):
        """Release table from reservation"""
        self.is_available = True
        self.reserved_by = None
        self.reserved_at = None
        self.save()
