from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Adds the custom shipping fields to the admin detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Stylinsole Customer Data', {'fields': ('phone_number', 'address', 'state')}),
    )
    
    # Shows these columns in the main user list
    list_display = ['username', 'email', 'phone_number', 'is_staff']