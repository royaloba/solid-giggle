# Create your views here.
# cart/views.py
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse
from store.models import ProductVariant
from .cart import Cart

@require_POST
def cart_add(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart.add(variant=variant, quantity=quantity)
    
    # Return drawer partial and trigger event for navbar badge update
    response = render(request, 'cart/partials/cart_drawer_content.html', {'cart': cart})
    response['HX-Trigger'] = 'cartUpdated'
    return response

@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart.add(variant=variant, quantity=quantity, override_quantity=True)
    else:
        cart.remove(variant)

    response = render(request, 'cart/partials/cart_drawer_content.html', {'cart': cart})
    response['HX-Trigger'] = 'cartUpdated'
    return response

@require_POST
def cart_remove(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart.remove(variant)

    response = render(request, 'cart/partials/cart_drawer_content.html', {'cart': cart})
    response['HX-Trigger'] = 'cartUpdated'
    return response

@require_GET
def cart_drawer(request):
    """Returns the full cart drawer content on demand."""
    cart = Cart(request)
    return render(request, 'cart/partials/cart_drawer_content.html', {'cart': cart})

@require_GET
def cart_badge(request):
    """Returns just the cart item count for the navbar badge."""
    cart = Cart(request)
    return render(request, 'cart/partials/cart_badge.html', {'cart': cart})