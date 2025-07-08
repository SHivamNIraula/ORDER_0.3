from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Food Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(default=15, help_text="Time in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
