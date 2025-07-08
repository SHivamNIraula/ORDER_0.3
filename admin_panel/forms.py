from django import forms
from tables.models import Table
from food.models import FoodItem, FoodCategory

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity']
        widgets = {
            'table_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter table number'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter table capacity'
            }),
        }
    
    def clean_table_number(self):
        table_number = self.cleaned_data['table_number']
        if table_number <= 0:
            raise forms.ValidationError("Table number must be positive.")
        return table_number
    
    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity <= 0:
            raise forms.ValidationError("Capacity must be positive.")
        return capacity

class FoodCategoryForm(forms.ModelForm):
    class Meta:
        model = FoodCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'category', 'price', 'image', 'is_available', 'preparation_time']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter food item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter price'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'preparation_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Time in minutes'
            }),
        }
    
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be positive.")
        return price
    
    def clean_preparation_time(self):
        prep_time = self.cleaned_data['preparation_time']
        if prep_time <= 0:
            raise forms.ValidationError("Preparation time must be positive.")
        return prep_time