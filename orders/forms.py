# orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    # Extra fields not saved directly on the Order model, but useful for shipping
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}), required=True)
    state = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Order
        fields = ['email'] # Only bind email directly to the model for now
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'})
        }