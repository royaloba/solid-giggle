from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes to all fields automatically
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-black outline-none transition'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'state')