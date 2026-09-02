from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, slug):
    # prefetch_related prevents N+1 queries when looping through images and variants in the template
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants'), 
        slug=slug
    )
    
    context = {
        'product': product,
        # Optional: You can filter out variants with 0 stock here, 
        # or handle it visually in the template (shown below)
        'variants': product.variants.all(), 
        'images': product.images.all(),
    }
    
    return render(request, 'store/product_detail.html', context)