from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # 1. Force email to be required
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number')
        
    # 2. Force email to be totally unique in the database
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes to all fields automatically
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-black outline-none transition'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'state')

# 3. NEW: Custom Login form to change the label to "Username or Email"
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email", widget=forms.TextInput(attrs={'autofocus': True}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-black outline-none transition'

# ... (Keep your StyledPasswordResetForm and StyledSetPasswordForm down here) ...


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the email input field
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-wine focus:border-wine outline-none transition-all',
            'placeholder': 'Enter your email address'
        })

    def get_users(self, email):
        """
        Override default behavior to strictly prevent staff and superusers 
        from utilizing the public password reset form.
        """
        active_users = CustomUser.objects.filter(
            email__iexact=email,
            is_active=True,
            is_staff=False,       # Blocks the Site Owner
            is_superuser=False    # Blocks the Developer
        )
        return (u for u in active_users if u.has_usable_password())

class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the new password and confirm password fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-wine focus:border-wine outline-none transition-all'
            })