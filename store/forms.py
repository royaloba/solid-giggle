from django import forms
from .models import Product, ProductImage, Brand, Category

class ProductForm(forms.ModelForm):
    # Dynamic text field instead of hardcoded checkboxes
    available_sizes = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 40, 41, 42.5, US 9'}),
        help_text="Enter sizes separated by commas.",
        error_messages={'required': 'You must provide at least one available size.'}
    )

    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'description', 'base_price', 'discount_price', 'is_featured', 'is_in_stock']

    def clean_available_sizes(self):
        """Takes '40, 41, 42' and turns it into ['40', '41', '42']"""
        data = self.cleaned_data.get('available_sizes', '')
        
        # Split by comma, remove extra spaces, and ignore empty entries
        sizes = [size.strip() for size in data.split(',') if size.strip()]
        
        # Remove any accidental duplicates while keeping the order
        unique_sizes = []
        for size in sizes:
            if size not in unique_sizes:
                unique_sizes.append(size)
                
        # Failsafe: if they just typed commas with no numbers
        if not unique_sizes:
            raise forms.ValidationError("Please enter valid sizes.")
            
        return unique_sizes
    
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug']
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']