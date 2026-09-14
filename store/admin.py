from django.contrib import admin
from django.utils.html import mark_safe
from .models import Category, Brand, Product, ProductVariant, ProductImage

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height: 60px; border-radius: 8px; border: 1px solid #ccc;"/>')
        return "No Image Uploaded"
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Changed 'in_stock' to the actual model field 'is_in_stock'
    list_display = ('name', 'brand', 'category', 'base_price', 'discount_price', 'is_in_stock')
    
    # Added 'is_in_stock' so you can toggle availability without opening the product!
    list_editable = ('discount_price', 'is_in_stock') 
    
    list_filter = ('brand', 'category', 'is_in_stock')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    # Organizes the admin form into clean sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'brand', 'category', 'description')
        }),
        ('Pricing & Visibility', {
            # Added 'is_in_stock' here so it shows up when editing a specific product
            'fields': ('base_price', 'discount_price', 'is_featured', 'is_in_stock')
        }),
    )

    

# Register Brand and Category so they show their real names!
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}