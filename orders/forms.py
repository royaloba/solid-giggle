from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'state']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 08012345678'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
        }