from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['variant']
    # You MUST add total_price to readonly_fields so the admin knows it can't be edited
    readonly_fields = ['total_price']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'customer_name', 'phone', 'total_amount', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at', 'state']
    search_fields = ['reference', 'email', 'first_name', 'last_name', 'phone', 'paystack_transaction_id']
    readonly_fields = ['reference', 'total_amount', 'paystack_transaction_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Payment Information', {
            'fields': ('reference', 'status', 'total_amount', 'paystack_transaction_id')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'state')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = "Customer"

    def status_badge(self, obj):
        colors = {
            'SUCCESS': 'green',
            'PENDING': 'orange',
            'FAILED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(f'<span style="color: white; background-color: {color}; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{obj.status}</span>')
    status_badge.short_description = "Status"