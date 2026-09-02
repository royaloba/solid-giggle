

# Register your models here.
# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'size', 'price', 'quantity']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'email', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reference', 'email', 'paystack_transaction_id']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    inlines = [OrderItemInline]